import argparse
import signal
import sys
from display import DisplayApp


class Eva(object):
    def __init__(self):
        self.display = None

    def start(self, args):
        self.display = DisplayApp(args.d)
        self.display.run()

    def stop(self):
        self.display.stop()


eva = Eva()


def handler(signum, frame):
    eva.stop()


def main():
    signal.signal(signal.SIGINT, handler)
    parser = argparse.ArgumentParser(description='EVA')
    parser.add_argument('dev', metavar='<CAN device name>', help='CAN device name')
    parser.add_argument('-i', default=42, type=int, choices=range(1, 127), required=False, help='canopen Node ID')
    parser.add_argument('-d', action="store_true")
    args, left = parser.parse_known_args()
    sys.argv = sys.argv[:1] + left

    print('Starting EVA')
    eva.start(args)
    return 0


if __name__ == '__main__':
    sys.exit(main())
