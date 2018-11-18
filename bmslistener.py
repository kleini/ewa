import can
import logging
import struct


class BMSListener(can.Listener):
    _bms_id = 1

    def __init__(self, display):
        super(BMSListener, self).__init__()
        self._display = display

    def on_message_received(self, msg):
        if msg.is_error_frame or msg.is_remote_frame:
            return
        try:
            self.process(msg.arbitration_id, msg.data, msg.timestamp)
        except Exception as e:
            logging.error(str(e))

    def process(self, can_id, data, timestamp):
        if 310 + self._bms_id == can_id:
            voltage, current, energy, reserved, defect_cell_count = struct.unpack_from('>3H2B', bytes(data))
            voltage = voltage / 100.0
            logging.debug(
                'Voltage {:3.2f}V, Current {:d}A, Energy {:d}Ah, defect cells {:d}'.format(voltage, current, energy,
                                                                                           defect_cell_count))
            self._display.set_voltage(voltage)
        if 311 + self._bms_id == can_id:
            min_voltage, min_cell_address, max_voltage, max_cell_address, reserved, cell_count = struct.unpack_from(
                '>HBH3B', bytes(data))
            min_voltage /= 100.0
            max_voltage /= 100.0
            logging.debug('Minimum Voltage {:1.2f}V cell {:d}, maximum voltage {:1.2f}V cell: {:d}, cells {:d}'.format(
                min_voltage, min_cell_address, max_voltage, max_cell_address, cell_count))
            self._display.set_min_cell_address_voltage(min_cell_address, min_voltage)
        if 312 + self._bms_id == can_id:
            average_temperature, max_temperature, min_temperature, reserved, reserved, reserved, min_temp_cell_address, max_temp_cell_address = struct.unpack_from(
                '8B', bytes(data))
            logging.debug(
                u'Average temperature {:d}\u00b0C, hottest temperature {:d}\u00b0C cell {:d}, coldest temperature {:d}\u00b0C, cell {:d}'.format(
                    average_temperature, max_temperature, max_temp_cell_address, min_temperature,
                    min_temp_cell_address))
        if 313 + self._bms_id == can_id:
            low_limit, current_limit, capacity, charge_level = struct.unpack_from('>4H', bytes(data))
            capacity /= 10.0
            charge_level /= 10.0
            logging.debug('Capacity {:3.1f}Ah, Charge level {:3.1f}%'.format(capacity, charge_level))
            self._display.set_charge_level(charge_level)
        if 314 + self._bms_id == can_id:
            address, voltage, temperature = struct.unpack_from('>BHB', bytes(data))
            voltage /= 100.0
            logging.debug(u'Cell {:d} {:3.2f}V {:d}\u00b0C'.format(address, voltage, temperature))
