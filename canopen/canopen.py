import sched
import time

from canopen.driver.socketcan import SocketCAN
from threading import Thread


class Event:
    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    def get_handler_count(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__ = get_handler_count


class Task:
    def call(self):
        raise NotImplementedError('Method call of Task must be implemented.')

    def interval(self):
        raise NotImplementedError('Method interval of Task must be implemented.')

    def do_next(self):
        return False


class Timer:
    def __init__(self):
        self.scheduler = sched.scheduler(timefunc=time.time)
        self.alive = True
        self.t = Thread(target=self.run)

    def start(self):
        self.t.start()

    def stop(self):
        self.alive = False
        self.t.join()

    def run(self):
        while self.alive:
            self.scheduler.run()
        print('Timer ended')

    def periodic(self, task):
        if task.do_next():
            run_next = time.time() + (task.interval() / 1000)
            self.scheduler.enterabs(time=run_next, priority=1, action=self.__next, argument=(task, run_next))

    def __next(self, task, previous):
        if task.do_next():
            run_next = previous + (task.interval() / 1000)
            self.scheduler.enterabs(time=run_next, priority=1, action=self.__next, argument=(task, run_next))
            task_thread = Thread(target=task.call())
            task_thread.start()


class NMT:
    # Network state identifier of nodes
    # Node is initializing
    BOOTUP = 0x00
    # Node is in pre-operational state
    STOPPED = 0x04
    # Node is in operational state
    OPERATIONAL = 0x05
    # Node is stopped
    PRE_OPERATIONAL = 0x7f

    # Commands from NMT master.
    # Start node
    ENTER_OPERATIONAL = 0x01
    # Stop node
    ENTER_STOPPED = 0x02
    # Put node into pre-operational
    ENTER_PRE_OPERATIONAL = 0x80
    # Reset node
    RESET_NODE = 0x81
    # Reset communication on node
    RESET_COMMUNICATION = 0x82

    def __init__(self, canopen, node_id):
        self.canopen = canopen
        self.operatingState = self.BOOTUP
        self.node_id = node_id
        self.heartbeat = Heartbeat(canopen=canopen)

    def start_heartbeat(self):
        self.canopen.timer.periodic(task=self.heartbeat)

    def delete(self):
        self.heartbeat.stop()


class Heartbeat(Task):

    def __init__(self, canopen):
        super().__init__()
        self.run = True
        self.canopen = canopen

    def stop(self):
        self.run = False

    def call(self):
        data = bytearray()
        data.append(self.canopen.nmt.operatingState)
        self.canopen.send(0x700 + self.canopen.nmt.node_id, data)

    def interval(self):
        return 1000

    def do_next(self):
        return self.run


class CANopenException(Exception):
    pass


class CANopen:
    def __init__(self):
        self.timer = Timer()
        self.nmt = None
        self.driver = None
        self.event = Event()
        self.receiver_alive = True
        self.receiver = Thread(target=self.run)

    def start(self, device, node_id):
        if node_id < 1 or node_id > 127:
            raise CANopenException('Node identifier needs to be in the range of 1 to 127.')

        print('Starting CANopen device with Node ID %d(0x%02X)' % (node_id, node_id))
        self.timer.start()
        self.nmt = NMT(canopen=self, node_id=node_id)
        self.nmt.start_heartbeat()
        self.driver = SocketCAN(device=device)

        # Bootup message
        data = bytearray()
        data.append(self.nmt.operatingState)
        self.send(0x700 + self.nmt.node_id, data)

        self.receiver.start()
        self.nmt.operatingState = self.nmt.OPERATIONAL

    def send(self, node_id, data):
        self.driver.send(node_id, data)

    def register(self, handler):
        self.event += handler

    def run(self):
        while self.receiver_alive:
            try:
                id, len, data = self.driver.recv()
                # TODO use new thread to emit events
                self.event(id=id, len=len, data=data)
            except CANopenException:
                print('Problem receiving data.')
        print('Receiver ended')

    def stop(self):
        print('Stopping CANopen device')
        self.receiver_alive = False
        self.driver.close()
        self.receiver.join()
        self.nmt.delete()
        self.timer.stop()
