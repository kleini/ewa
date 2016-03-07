import sched
import time

from canopen.driver.socketcan import SocketCAN
from queue import Empty, Queue
from threading import Condition, Thread


class Event:
    def __init__(self):
        self.handlers = set()
        self.queue = Queue()
        self.alive = True
        self.thread = Thread(target=self.dequeue)

    def start(self):
        self.thread.start()

    def stop(self):
        self.alive = False
        self.thread.join()

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def enqueue(self, message):
        self.queue.put(message)

    def dequeue(self):
        while self.alive:
            try:
                message = self.queue.get(block=True, timeout=1)
            except Empty:
                continue
            if message is not None:
                for handler in self.handlers:
                    handler(message=message)

    def fire(self, *args, **kwargs):
        print('Args %s' % args)
        print('kwArgs %s' % kwargs)
        for handler in self.handlers:
            handler(*args, **kwargs)

    def get_handler_count(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = enqueue
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


class ReceivedMessage:
    def __init__(self, ident, length, data):
        self.ident = ident
        self.length = length
        self.data = data


class SDOResponse:
    condition = Condition()
    message = None

    def receive(self, message):
        self.condition.acquire()
        self.message = message
        self.condition.notify()
        self.condition.release()

    def get(self):
        self.condition.acquire()
        # TODO check for equal 0x580 + node_id, command byte, index, sub-index
        while not self.message:
            self.condition.wait()
        self.condition.release()
        return self.message


class CANopen:
    def __init__(self):
        self.driver = None
        self.event = Event()
        self.receiver_alive = True
        self.receiver = Thread(target=self.run)
        self.timer = Timer()
        self.nmt = None

    def start(self, device, node_id):
        if node_id < 1 or node_id > 127:
            raise CANopenException('Node identifier needs to be in the range of 1 to 127.')

        print('Starting CANopen device with Node ID %d(0x%02X)' % (node_id, node_id))
        self.event.start()
        self.driver = SocketCAN(device=device)
        self.receiver.start()
        self.timer.start()
        self.nmt = NMT(canopen=self, node_id=node_id)

        # Bootup message
        data = bytearray()
        data.append(self.nmt.operatingState)
        self.send(0x700 + self.nmt.node_id, data)

        self.nmt.operatingState = self.nmt.OPERATIONAL

    def send(self, node_id, data):
        self.driver.send(node_id, data)

    def register(self, handler):
        self.event += handler

    def run(self):
        while self.receiver_alive:
            try:
                # TODO do not block, then we can not terminate
                message = self.driver.recv()
                # TODO use new thread to emit events
                self.event(message=message)
            except CANopenException:
                print('Problem receiving data.')

    def stop(self):
        print('Stopping CANopen device')
        self.nmt.delete()
        self.timer.stop()
        self.receiver_alive = False
        self.driver.close()
        self.receiver.join()
        self.event.stop()

    def SDOupload(self, node_id, index, subindex, type, value):
        # only expedited yet
        if len(value) > 4:
            raise CANopenException('Can not upload more than 4 bytes currently.')

        data = bytearray()
        # command byte
        data.append(0x23 | (4 - len(data)) << 2)
        # index LSB
        data.append(index & 0xff)
        data.append((index >> 8) & 0xff)
        # sub-index
        data.append(subindex)
        # data TODO LSB
        data.append(value)

        receive = SDOResponse()
        self.event += receive.receive()
        try:
            self.send(0x580 + node_id, data)
            return receive.get()
        finally:
            self.event -= receive.receive()

    def SDOread(self, node_id, index, subindex, type):
        return 0
