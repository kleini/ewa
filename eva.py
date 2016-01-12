import argparse
import signal

from canopen.canopen import CANopen, CANopenException


class EVA:
    def main(self):
        parser = argparse.ArgumentParser(description='EVA')
        parser.add_argument('dev', metavar='<CAN device name>', help='CAN device name')
        parser.add_argument('-i', default=42, type=int, choices=range(1, 128), required=False, help='canopen Node ID')
        args = parser.parse_args()

        print('Starting EVA')

        # create a raw socket and bind it to the given CAN interface
        self.co = CANopen(args.dev, args.i)
        # TODO non-sense send command
        self.co.send(0x01, b'\x01\x02\x03')

        while True:
            try:
                id, len, data = self.co.recv()
            except CANopenException:
                break
            type = id & 0xFF80
            node_id = id - type
            print('Received: type=%x, nodeId=%x, can_dlc=%x, data=%s' % (type, node_id, len, data))

    def delete(self):
        self.co.delete()


def handler(signum, frame):
    eva.delete(self=eva)

if __name__ == '__main__':
    eva = EVA
    signal.signal(signal.SIGINT, handler)
    eva.main(self=eva)
