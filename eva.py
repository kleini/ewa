import argparse
import socket
import struct
import CANopen

# CAN frame packing/unpacking (see `struct can_frame` in <linux/can.h>)
can_frame_fmt = "=IB3x8s"


def dissect_can_frame(frame):
    can_id, can_dlc, data = struct.unpack(can_frame_fmt, frame)
    return (can_id, can_dlc, data[:can_dlc])


def main():
    parser = argparse.ArgumentParser(description='EVA')
    parser.add_argument('dev', metavar='<CAN device name>', help='CAN device name')
    parser.add_argument('-i', default=42, type=int, choices=range(1, 128), required=False, help='CANopen Node ID')
    args = parser.parse_args()

    # create a raw socket and bind it to the given CAN interface
    co = CANopen.init(args.dev, args.i)
    s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    s.bind((args.dev,))

    while True:
        cf, addr = s.recvfrom(16)
        id, len, data = dissect_can_frame(cf)
        type = id & 0xFF80
        nodeId = id - type
        print('Received: type=%x, nodeId=%x, can_dlc=%x, data=%s' % (type, nodeId, len, data))

if __name__ == '__main__':
    main()
