import argparse
from canopen.canopen import CANopen
import canopen


def main():
    parser = argparse.ArgumentParser(description='EVA')
    parser.add_argument('dev', metavar='<CAN device name>', help='CAN device name')
    parser.add_argument('-i', default=42, type=int, choices=range(1, 128), required=False, help='canopen Node ID')
    args = parser.parse_args()

    print('Starting EVA')

    # create a raw socket and bind it to the given CAN interface
    co = canopen.canopen.CANopen(args.dev, args.i)
    co.send(0x01, b'\x01\x02\x03')

    while True:
        id, len, data = co.recv()
        type = id & 0xFF80
        nodeId = id - type
        print('Received: type=%x, nodeId=%x, can_dlc=%x, data=%s' % (type, nodeId, len, data))

if __name__ == '__main__':
    main()
