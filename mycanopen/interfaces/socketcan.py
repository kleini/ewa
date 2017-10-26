from select import select
from socket import AF_CAN, CAN_RAW, SOCK_RAW, error, socket
from struct import unpack, pack

from .. import canopen
from ..message import ReceivedMessage
from ..driver import DriverABC
from canopen import CANopenException

# CAN frame packing/unpacking (see `struct can_frame` in <linux/can.h>)
can_frame_fmt = "=IB3x8s"


def build_can_frame(can_id, data):
    # TODO length really from data?
    can_dlc = len(data)
    data = data.ljust(8, b'\x00')
    return pack(can_frame_fmt, can_id, can_dlc, data)


def dissect_can_frame(frame):
    """

    :rtype: ReceivedMessage
    """
    can_id, can_dlc, data = unpack(can_frame_fmt, frame)
    return ReceivedMessage(ident=can_id, length=can_dlc, data=data[:can_dlc])


class SocketCAN(DriverABC):
    closed = False

    def __init__(self, device):
        # create a raw socket
        self.socket = socket(AF_CAN, SOCK_RAW, CAN_RAW)
        # bind socket to the given CAN interface
        self.socket.bind((device,))
        super(SocketCAN, self).__init__()

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
            raise CANopenException('Error reading from socket.')
        return dissect_can_frame(cf)

    def send(self, msg):
        try:
            self.socket.send(build_can_frame(can_id=msg.ident, data=msg.data))
        except error:
            print('Error sending CAN frame')

    def close(self):
        self.closed = True
        self.socket.close()
