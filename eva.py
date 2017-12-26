import argparse
import canopen
import json
import io
import logging
import os.path
import signal
import sys
import time
from canopen import nmt
from display import DisplayApp
from enum import Enum
from threading import Thread


class ForceMapping(object):
    def __init__(self):
        self._map = {0: 0, 50: 0, 60: 0, 70: 0, 80: 0, 90: 0, 100: 0, 130: 0}

    def configure(self, key, value):
        if key in self._map:
            self._map[key] = value
        else:
            raise Exception('No such key ' + key)

    def write(self):
        file = io.open("mapping.json", "wb")
        json.dump(self._map, file)
        file.close()

    def read(self):
        if os.path.isfile("mapping.json"):
            file = io.open("mapping.json", "rb")
            self._map = json.load(file)
            file.close()


class State(Enum):
    OFFLINE = 0
    INIT = 1
    ONLINE = 2


class Eva(object):
    def __init__(self):
        self._mapping = ForceMapping()
        self._display = None
        self._run = True
        self._state = State.OFFLINE
        self._network = None
        self._controller = None
        self._main_thread = Thread(target=self.mainloop)
        self._monitor_thread = None
        self._heartbeat = False

    def start(self, args):
        self._mapping.read()
        self._display = DisplayApp(args.d)
        self._network = canopen.Network()
        self._network.connect(bustype='socketcan', channel=args.dev)
        self._controller = self._network.add_node(7, 'CANopenSocket.eds')
        # main EVA thread here
        self._main_thread.start()
        # blocks until the UI ends
        self._display.run()

    def stop(self):
        self._run = False
        self._mapping.write()
        if self._monitor_thread:
            self._monitor_thread.join()
            self._monitor_thread = None
        if self._main_thread:
            self._main_thread.join()
            self._main_thread = None
        if self._controller:
            self._controller.pdo.tx[1].stop()
            self._controller.nmt.state = 'STOPPED'
            self._controller = None
        if self._network:
            self._network.disconnect()
            self._network = None
        if self._display:
            self._display.stop()
            self._display = None

    def mainloop(self):
        next_state = State.OFFLINE
        while self._run:
            if State.OFFLINE == self._state:
                next_state = self.offline()
            if State.INIT == self._state:
                next_state = self.init()
            if State.ONLINE == self._state:
                next_state = self.online()
            self._state = next_state

    def offline(self):
        self.connected(False)
        if self._monitor_thread:
            self._monitor_thread.join()
            self._monitor_thread = None
        nmt_state = None
        try:
            nmt_state = self._controller.nmt.wait_for_heartbeat(0.1)
        except canopen.nmt.NmtError as e:
            pass
        if nmt_state:
            self.connected(True)
            return State.INIT
        return State.OFFLINE

    def init(self):
        self._controller.nmt.state = 'PRE-OPERATIONAL'
        self._controller.sdo['Producer heartbeat time'].raw = 100
        self._controller.pdo.tx[1].clear()
        self._controller.pdo.tx[1].add_variable(0x2110, 1)
        self._controller.pdo.tx[1].trans_type = 254
        self._controller.pdo.tx[1].event_timer = 1000
        self._controller.pdo.tx[1].enabled = True
        self._controller.pdo.save()
        self._controller.pdo.tx[1].add_callback(callback=self.received)
        self._controller.nmt.state = 'OPERATIONAL'
        if self._monitor_thread:
            print('Monitor thread not gone')
        else:
            self._monitor_thread = Thread(target=self.monitor_heartbeat)
            self._monitor_thread.start()
        return State.ONLINE

    def online(self):
        # self.controller.pdo.tx[1].wait_for_reception()
        # speed = self.controller.pdo.tx[1]['Variable Int32.cycles per second'].phys
        # print('Received PDO: %s' % speed)
        time.sleep(0.1)
        if self._heartbeat:
            return State.ONLINE
        else:
            return State.OFFLINE

    def received(self, message):
        for var in message:
            self._display.display.set_torque(var.raw)

    def monitor_heartbeat(self):
        while self._run:
            nmt_state = None
            try:
                nmt_state = self._controller.nmt.wait_for_heartbeat(0.2)
            except canopen.nmt.NmtError as e:
                pass
            if nmt_state:
                self.connected(True)
            else:
                self.connected(False)
                break

    def connected(self, connected):
        if self._display:
            if self._display.display:
                self._display.display.connected(connected)
        self._heartbeat = connected


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

    logging.basicConfig()
    some_logger = logging.getLogger('canopen.network')
    some_logger.setLevel(logging.DEBUG)
    some_logger.addHandler(logging.StreamHandler())

    eva.start(args)
    eva.stop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
