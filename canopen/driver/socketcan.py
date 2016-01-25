import canopen
import socket
import struct


class SocketCAN:

    # CAN frame packing/unpacking (see `struct can_frame` in <linux/can.h>)
    can_frame_fmt = "=IB3x8s"

    def __init__(self, device):
        # create a raw socket and bind it to the given CAN interface
        self.s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.s.bind((device,))

    def dissect_can_frame(self, frame):
        can_id, can_dlc, data = struct.unpack(self.can_frame_fmt, frame)
        return canopen.canopen.ReceivedMessage(ident=can_id, length=can_dlc, data=data[:can_dlc])

    def recv(self):
        try:
            cf, addr = self.s.recvfrom(16)
        except socket.error:
            raise canopen.canopen.CANopenException('Error reading from socket.')
        return self.dissect_can_frame(cf)

    def build_can_frame(self, can_id, data):
        can_dlc = len(data)
        data = data.ljust(8, b'\x00')
        return struct.pack(self.can_frame_fmt, can_id, can_dlc, data)

    def send(self, node_id, data):
        try:
            self.s.send(self.build_can_frame(node_id, data))
        except socket.error:
            print('Error sending CAN frame')

    def close(self):
        self.s.close()
