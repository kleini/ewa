import argparse
import canopen
import signal
import sys
from canopen import nmt
from display import DisplayApp
from enum import Enum
from threading import Thread
from time import sleep


class State(Enum):
    OFFLINE = 0
    INIT = 1
    ONLINE = 2


class Eva(object):
    def __init__(self):
        self.display = None
        self.run = True
        self.state = State.OFFLINE
        self.network = None
        self.controller = None
        self.thread = Thread(target=self.mainloop)

    def start(self, args):
        self.display = DisplayApp(args.d)
        self.network = canopen.Network()
        self.network.connect(bustype='socketcan', channel=args.dev)
        self.controller = self.network.add_node(7, 'CANopenSocket.eds')
        # main EVA thread here
        self.thread.start()
        # blocks until the UI ends
        self.display.run()
        print('Value %d' % self.display.display.torque_gauge.value)

    def stop(self):
        self.run = False
        self.thread.join()
        self.controller.pdo.tx[1].stop()
        self.controller.nmt.state = 'STOPPED'
        # TODO shutdown PDO
        self.network.disconnect()
        self.display.stop()

    def mainloop(self):
        next_state = State.OFFLINE
        while self.run:
            if State.OFFLINE == self.state:
                next_state = self.offline()
            if State.INIT == self.state:
                next_state = self.init()
            if State.ONLINE == self.state:
                next_state = self.online()
            self.state = next_state

    def offline(self):
        nmt_state = None
        try:
            nmt_state = self.controller.nmt.wait_for_heartbeat(10)
        except canopen.nmt.NmtError as e:
            print(e)
        if nmt_state:
            return State.INIT
        return State.OFFLINE

    def init(self):
        self.controller.nmt.state = 'PRE-OPERATIONAL'
        self.controller.sdo['Producer heartbeat time'].raw = 1000
        self.controller.pdo.tx[1].clear()
        self.controller.pdo.tx[1].add_variable(0x2110, 1)
        self.controller.pdo.tx[1].trans_type = 254
        self.controller.pdo.tx[1].event_timer = 1000
        self.controller.pdo.tx[1].enabled = True
        self.controller.pdo.save()
        self.controller.pdo.tx[1].add_callback(callback=self.received)
        self.controller.nmt.state = 'OPERATIONAL'
        return State.ONLINE

    def online(self):
        self.controller.pdo.tx[1].wait_for_reception()
        # speed = self.controller.pdo.tx[1]['Variable Int32.cycles per second'].phys
        # print('Received PDO: %s' % speed)
        return State.ONLINE

    def received(self, message):
        for var in message:
            self.display.display.set_torque(var.raw)


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
