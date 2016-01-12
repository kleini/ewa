import sched
import time

from canopen.driver.socketcan import SocketCAN
from threading import Thread


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
        self.operatingState = self.BOOTUP
        self.node_id = node_id
        self.heartbeat = Heartbeat(canopen=canopen)
        canopen.timer.periodic(task=self.heartbeat)

    def delete(self):
        self.heartbeat.stop()


class Task:
    def call(self):
        raise NotImplementedError('Method call of Task must be implemented.')

    def interval(self):
        raise NotImplementedError('Method interval of Task must be implemented.')

    def do_next(self):
        return False


class Heartbeat(Task):

    def __init__(self, canopen):
        super().__init__()
        self.run = True
        self.canopen = canopen

    def stop(self):
        self.run = False

    def call(self):
        print('Test %10.4f' % time.time())
        data = bytearray()
        data.append(self.canopen.nmt.operatingState)
        self.canopen.send(self.canopen.nmt.node_id, data)

    def interval(self):
        return 1000

    def do_next(self):
        return self.run


class Timer:
    def __init__(self):
        self.scheduler = sched.scheduler(timefunc=time.time)
        self.alive = True
        self.t = Thread(target=self.run)
        self.t.start()

    def delete(self):
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


class CANopenException(Exception):
    pass


class CANopen:

    def init(self, device, node_id):
        if node_id < 1 or node_id > 127:
            raise CANopenException('Node identifier needs to be in the range of 1 to 127.')

        print('Starting CANopen device with Node ID %d(0x%02X)' % (node_id, node_id))
        self.timer = Timer()
        self.nmt = NMT(canopen=self, node_id=node_id)
        self.driver = SocketCAN(device=device)

        # Bootup message
        data = bytearray()
        data.append(self.nmt.operatingState)
        self.send(self.nmt.node_id, data)

        # TODO start thread receiving CAN frames
        self.nmt.operatingState = self.nmt.OPERATIONAL

    def send(self, node_id, data):
        self.driver.send(node_id, data)

    def recv(self):
        return self.driver.recv()

    def delete(self):
        print('Stopping CANopen device')
        self.nmt.delete()
        self.timer.delete()
        self.driver.close()
