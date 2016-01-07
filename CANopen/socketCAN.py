import socket
import struct
from CANopen.driver import driver

class socketCAN(driver):

    can_frame_fmt = "=IB3x8s"

    def __init__(self, device):
        self.s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.s.bind((device,))

    def build_can_frame(can_id, data):
        can_dlc = len(data)
        data = data.ljust(8, b'\x00')
        return struct.pack(socketCAN.can_frame_fmt, can_id, can_dlc, data)

    @property
    def send(self):
        self.s.send(self.build_can_frame(0x01, b'\x01\x02\x03'))
