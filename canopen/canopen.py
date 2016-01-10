import socket
from canopen.driver.socketcan import SocketCAN


class CANopen:

    def __init__(self, device, node_id):
        print('Starting CANopen device with Node ID %d(0x%02X)' % (node_id, node_id));
        self.driver = SocketCAN(device)
        # TODO start thread receiving CAN frames

    def send(self, node_id, data):
        self.driver.send(node_id, data)

    def recv(self):
        return self.driver.recv()
