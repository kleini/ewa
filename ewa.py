import argparse
import canopen
import logging
import signal
import sys
import time
import traceback
from bmslistener import BMSListener
from canopen import nmt
from display import DisplayApp
from epaper import PaperDisplay
from enum import Enum
from forcemapping import ForceMapping
from ropespeed import RopeSpeed
from threading import Thread


class State(Enum):
    OFFLINE = 0
    INIT = 1
    ONLINE = 2


class Ewa(object):
    def __init__(self):
        self._PDO = False
        self._mapping = ForceMapping()
        self._display = None
        self._epaper = None
        self._run = True
        self._state = State.OFFLINE
        self._network = None
        self._controller = None
        self._main_thread = Thread(target=self.mainloop)
        self._read = False
        self._read_thread = None
        self._monitor_thread = None
        self._heartbeat = False
        self._received_data = False

    def start(self, args):
        self._devel = args.d
        self._mapping.read()
        self._display = DisplayApp(args.d, self._mapping)
        self._epaper = PaperDisplay()
        self._network = canopen.Network()
        self._network.listeners = self._network.listeners + [BMSListener(self._display)]
        self._network.connect(bustype='socketcan', channel=args.dev)
        self._controller = self._network.add_node(7, 'CANopenSocket.eds')
        # main EWA thread here
        self._main_thread.start()
        # blocks until the UI ends
        try:
            self._display.run()
        except BaseException as e:
            logging.error(traceback.format_exc())

    def stop(self):
        self._run = False
        self._read = False
        self._mapping.write()
        if self._monitor_thread:
            self._monitor_thread.join()
            self._monitor_thread = None
        if self._read_thread:
            self._read_thread.join()
            self._read_thread = None
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
        if self._epaper:
            self._epaper.stop()
            self._epaper = None
        if self._display:
            self._display.stop()
            self._display = None

    def mainloop(self):
        next_state = State.OFFLINE
        while self._run:
            # print('%s' % self._state)
            if State.OFFLINE == self._state:
                next_state = self.offline()
            if State.INIT == self._state:
                next_state = self.init()
            if State.ONLINE == self._state:
                next_state = self.online()
            self._state = next_state

    def offline(self):
        if not self._PDO:
            if self._read:
                self._read = False
                print('Stop')
                self._read_thread.join()
                self._read_thread = None
        self.connected(False)
        if self._monitor_thread:
            self._monitor_thread.join()
            self._monitor_thread = None
        nmt_state = None
        try:
            self._controller.nmt.state = 'PRE-OPERATIONAL'
            self._controller.sdo['Producer heartbeat time'].raw = 1000
        except canopen.sdo.SdoCommunicationError as e:
            logging.exception('Failed to configure heartbeat.')
        except BaseException as e:
            logging.error(traceback.format_exc())
        try:
            nmt_state = self._controller.nmt.wait_for_heartbeat(0.1)
        except canopen.nmt.NmtError as e:
            pass
        if nmt_state:
            self.connected(True)
            return State.INIT
        return State.OFFLINE

    def init(self):
        # TODO somewhere here SDO timeouts may occur.
        self._controller.nmt.state = 'PRE-OPERATIONAL'
        try:
            self._controller.sdo['Producer heartbeat time'].raw = 1000
        except canopen.sdo.SdoCommunicationError as e:
            logging.info('Failed to configure heartbeat.')
        if self._PDO:
            try:
                self._controller.pdo.read()
            except canopen.sdo.SdoCommunicationError as e:
                logging.info('Failed to read PDO configuration.')
            self._controller.pdo.tx[1].clear()
            # TODO replace with Throttle_Command 0x3216, subindex 0 length 2 readonly
            self._controller.pdo.tx[1].add_variable(0x2110, 1)
            # Asynchronous PDO. If one process variable changes, the data is transfered.
            self._controller.pdo.tx[1].trans_type = 254
            # Transmit at least every 1000 milliseconds.
            self._controller.pdo.tx[1].event_timer = 1000
            self._controller.pdo.tx[1].enabled = True
            self._controller.pdo.tx[1].add_callback(callback=self.received)
            try:
                self._controller.pdo.save()
            except canopen.sdo.SdoCommunicationError as e:
                logging.info('Failed to save PDO configuration.')
        else:
            if not self._read:
                self._read = True
                logging.debug('Starting read thread')
                self._read_thread = Thread(target=self.read)
                self._read_thread.start()
        # TODO With the initialisation problem the emulator will not go back into operational mode and we get no data.
        self._controller.nmt.state = 'OPERATIONAL'
        if self._monitor_thread:
            print('Monitor thread not gone')
        else:
            self._monitor_thread = Thread(target=self.monitor_heartbeat)
            self._monitor_thread.start()
        return State.ONLINE

    def read(self):
        count = 0
        while self._read:
            try:
                value = self._controller.sdo[0x3216].raw
                self.show_data(value)
            except canopen.sdo.SdoError:
                if not self._devel:
                    logging.exception('Reading Throttle_Command failed')
            try:
                value = self._controller.sdo[0x3207].raw
                self.show_rpm(value)
            except canopen.sdo.SdoError:
                if not self._devel:
                    logging.exception('Reading RPM failed')
            if count >= 10:
                try:
                    value = self._controller.sdo[0x320b].raw
                    self.show_motor_temperature(value)
                except canopen.sdo.SdoError:
                    if not self._devel:
                        logging.exception('Reading motor temperature failed')
                try:
                    value = self._controller.sdo[0x322a].raw
                    self.show_controller_temperature(value)
                except canopen.sdo.SdoError:
                    if not self._devel:
                        logging.exception('Reading controller temperature failed')
                try:
                    value = self._controller.sdo[0x324d].raw
                    self.show_voltage(value)
                except canopen.sdo.SdoError:
                    if not self._devel:
                        logging.exception('Reading voltage failed')
                count = 0
            time.sleep(0.1)
            count += 1

    def online(self):
        """
        Just monitor the heartbeat and change state accordingly. Make the main thread sleep running through the states.
        """
        time.sleep(0.1)
        if self._heartbeat:
            return State.ONLINE
        else:
            return State.OFFLINE

    def received(self, message):
        for var in message:
            self.show_data(var.raw)

    def show_data(self, value):
        logging.debug('Throttle_Command: ' + str(value))
        self._received_data = True
        if self._display:
            self._display.set_measure(value)
            self._display.set_torque(self._mapping.map(value))
        if self._epaper:
            self._epaper.set_torque(self._mapping.map(value))

    def show_rpm(self, value):
        if value > 32767:
            value -= 65536
        logging.debug('RPM: ' + str(value))
        self._received_data = True
        speed = RopeSpeed.calculate_speed(value)
        logging.debug('Rope speed: ' + str(speed))
        if self._display:
            self._display.set_rpm(value)
            self._display.set_rope_speed(speed)

    def show_motor_temperature(self, value):
        value /= 10
        logging.debug('Motor temperature ' + str(value))
        self._received_data = True
        if self._display:
            self._display.set_motor_temperature(value)

    def show_controller_temperature(self, value):
        value /= 10
        logging.debug('Controller temperature ' + str(value))
        self._received_data = True
        if self._display:
            self._display.set_controller_temperature(value)

    def show_voltage(self, value):
        value /= 100.0
        logging.debug('Voltage {:3.2f}V'.format(value))
        if self._display:
            self._display.set_voltage(value)

    def monitor_heartbeat(self):
        while self._run:
            nmt_state = None
            self._received_data = False
            try:
                nmt_state = self._controller.nmt.wait_for_heartbeat(1.2)
            except canopen.nmt.NmtError as e:
                pass
            if nmt_state or self._received_data:
                self.connected(True)
            else:
                self.connected(False)
                break

    def connected(self, connected):
        if self._display:
            self._display.connected(connected)
        self._heartbeat = connected


ewa = Ewa()


def handler(signum, frame):
    ewa.stop()


def main():
    signal.signal(signal.SIGINT, handler)
    parser = argparse.ArgumentParser(description='EWA')
    parser.add_argument('dev', metavar='<CAN device name>', help='CAN device name')
    parser.add_argument('-i', default=42, type=int, choices=range(1, 127), required=False, help='canopen Node ID')
    parser.add_argument('-d', action="store_true")
    args, left = parser.parse_known_args()
    sys.argv = sys.argv[:1] + left

    logging.basicConfig()
    some_logger = logging.getLogger('canopen.network')
    some_logger.setLevel(logging.DEBUG)
    some_logger.addHandler(logging.StreamHandler())

    ewa.start(args)
    ewa.stop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
