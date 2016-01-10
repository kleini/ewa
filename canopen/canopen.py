from canopen import periodic
from canopen.driver.socketcan import SocketCAN
from datetime import timedelta


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
        periodic(task=self.heartbeat, interval=1000)


class Task:
    def call(self):
        raise NotImplementedError('Method call of Task must be implemented.')


class Heartbeat(Task):

    def __init__(self, canopen):
        super().__init__()
        self.canopen = canopen

    def call(self):
        print('Test')
        # self.canopen.send(self.canopen.nmt.node_id, self.canopen.nmt.operatingState)


class CANopenException(Exception):
    pass


class CANopen:

    def __init__(self, device, node_id):
        if node_id < 1 or node_id > 127:
            raise CANopenException('Node identifier needs to be in the range of 1 to 127.')
        self.nmt = NMT(canopen=self, node_id=node_id)
        print('Starting CANopen device with Node ID %d(0x%02X)' % (node_id, node_id));
        self.driver = SocketCAN(device=device)
        # TODO start thread receiving CAN frames

    def send(self, node_id, data):
        self.driver.send(node_id, data)

    def recv(self):
        return self.driver.recv()
