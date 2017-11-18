import argparse
import canopen
import signal
import sys
import time
from canopen import nmt
from display import DisplayApp
from enum import Enum
from threading import Thread


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
        self.mainThread = Thread(target=self.mainloop)
        self.monitorThread = None
        self.heartbeat = False

    def start(self, args):
        self.display = DisplayApp(args.d)
        self.network = canopen.Network()
        self.network.connect(bustype='socketcan', channel=args.dev)
        self.controller = self.network.add_node(7, 'CANopenSocket.eds')
        # main EVA thread here
        self.mainThread.start()
        # blocks until the UI ends
        self.display.run()

    def stop(self):
        self.run = False
        if self.mainThread:
            self.mainThread.join()
            self.mainThread = None
        if self.controller:
            self.controller.pdo.tx[1].stop()
            self.controller.nmt.state = 'STOPPED'
            self.controller = None
        if self.network:
            self.network.disconnect()
            self.network = None
        if self.display:
            self.display.stop()
            self.display = None

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
        self.connected(False)
        if self.monitorThread:
            self.monitorThread.join()
            self.monitorThread = None
        nmt_state = None
        try:
            nmt_state = self.controller.nmt.wait_for_heartbeat(0.1)
        except canopen.nmt.NmtError as e:
            pass
        if nmt_state:
            self.connected(True)
            return State.INIT
        return State.OFFLINE

    def init(self):
        self.controller.nmt.state = 'PRE-OPERATIONAL'
        self.controller.sdo['Producer heartbeat time'].raw = 100
        self.controller.pdo.tx[1].clear()
        self.controller.pdo.tx[1].add_variable(0x2110, 1)
        self.controller.pdo.tx[1].trans_type = 254
        self.controller.pdo.tx[1].event_timer = 1000
        self.controller.pdo.tx[1].enabled = True
        self.controller.pdo.save()
        self.controller.pdo.tx[1].add_callback(callback=self.received)
        self.controller.nmt.state = 'OPERATIONAL'
        if self.monitorThread:
            print('Monitor thread not gone')
        else:
            self.monitorThread = Thread(target=self.monitor_heartbeat)
            self.monitorThread.start()
        return State.ONLINE

    def online(self):
        # self.controller.pdo.tx[1].wait_for_reception()
        # speed = self.controller.pdo.tx[1]['Variable Int32.cycles per second'].phys
        # print('Received PDO: %s' % speed)
        time.sleep(0.1)
        if self.heartbeat:
            return State.ONLINE
        else:
            return State.OFFLINE

    def received(self, message):
        for var in message:
            self.display.display.set_torque(var.raw)

    def monitor_heartbeat(self):
        while True:
            nmt_state = None
            try:
                nmt_state = self.controller.nmt.wait_for_heartbeat(0.2)
            except canopen.nmt.NmtError as e:
                pass
            if nmt_state:
                self.connected(True)
            else:
                self.connected(False)
                break

    def connected(self, connected):
        if self.display:
            if self.display.display:
                self.display.display.connected(connected)
        self.heartbeat = connected


eva = Eva()


def handler(signum, frame):
    print('Stopping EVA')
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
    eva.stop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
