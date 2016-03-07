import canopen

from select import select
from socket import AF_CAN, CAN_RAW, SOCK_RAW, error, socket
from struct import pack, unpack


class SocketCAN:
    # CAN frame packing/unpacking (see `struct can_frame` in <linux/can.h>)
    can_frame_fmt = "=IB3x8s"
    # create a raw socket
    socket = socket(AF_CAN, SOCK_RAW, CAN_RAW)
    closed = False

    def __init__(self, device):
        # bind socket to the given CAN interface
        self.socket.bind((device,))

    def dissect_can_frame(self, frame):
        can_id, can_dlc, data = unpack(self.can_frame_fmt, frame)
        return canopen.canopen.ReceivedMessage(ident=can_id, length=can_dlc, data=data[:can_dlc])

    def recv(self):
        try:
            cf = None
            while not cf:
                if self.closed:
                    return
                r, _, _ = select([self.socket], [], [], 1)
                if bool(r):
                    cf, addr = self.socket.recvfrom(16)
        except error:
            raise canopen.canopen.CANopenException('Error reading from socket.')
        return self.dissect_can_frame(cf)

    def build_can_frame(self, can_id, data):
        can_dlc = len(data)
        data = data.ljust(8, b'\x00')
        return pack(self.can_frame_fmt, can_id, can_dlc, data)

    def send(self, node_id, data):
        try:
            self.socket.send(self.build_can_frame(node_id, data))
        except error:
            print('Error sending CAN frame')

    def close(self):
        self.closed = True
        self.socket.close()
