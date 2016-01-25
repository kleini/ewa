import argparse
import signal
import sys

from canopen.canopen import CANopen


co = CANopen()


def handler(signum, frame):
    co.stop()


def logger(message):
    type = message.ident & 0xFF80
    node_id = message.ident - type
    print('Received: type=%x, nodeId=%x, dlc=%x, data=%s' % (type, node_id, message.length, message.data))


def main():
    signal.signal(signal.SIGINT, handler)
    parser = argparse.ArgumentParser(description='EVA')
    parser.add_argument('dev', metavar='<CAN device name>', help='CAN device name')
    parser.add_argument('-i', default=42, type=int, choices=range(1, 128), required=False, help='canopen Node ID')
    args = parser.parse_args()

    print('Starting EVA')

    co.start(args.dev, args.i)
    co.register(handler=logger)
    # TODO non-sense send command
    co.send(0x01, b'\x01\x02\x03')
    return 0


if __name__ == '__main__':
    sys.exit(main())
