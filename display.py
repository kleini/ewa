import logging
import traceback
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import (
    Color,
    Ellipse
)
from kivy.properties import (
    ListProperty,
    ObjectProperty
)
from kivy.uix.screenmanager import (
    ScreenManager,
    Screen,
    NoTransition
)
from kivy.uix.widget import Widget


def color(battery_level):
    return [1. - battery_level / 100., battery_level / 100., 0, 1]


def color_voltage(voltage, cells):
    # voltage of a cell can be between 2.6V and 3.55V
    cell_voltage = voltage/cells
    red = (3.55 - cell_voltage) / .95 if cell_voltage >= 2.6 else 1.
    green = (cell_voltage - 2.6) / .95 if cell_voltage >= 2.6 else 0.
    return [red, green, 0, 1]


class Connected(Widget):
    def __init__(self, **kwargs):
        super(Connected, self).__init__(**kwargs)
        with self.canvas:
            self.color = Color(1, 0, 0)
            self._circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.draw, size=self.draw)

    def connected(self, connected):
        old = (1 == self.color.g)
        if old == connected:
            return
        if connected:
            self.color.r = 0
            self.color.g = 1
        else:
            self.color.r = 1
            self.color.g = 0
        self.draw()

    def draw(self, *args):
        self._circle.pos = self.pos
        self._circle.size = self.size


class Tow(Screen):
    _force_gauge = ObjectProperty(None)
    _battery_bar = ObjectProperty(None)
    _force_label = ObjectProperty(None)
    _connected_color = ObjectProperty(None)

    def connected(self, connected):
        self._connected_color.connected(connected)

    def set_torque(self, value):
        old = self._force_gauge.get_value()
        if old == value:
            return
        try:
            # don't fall into errorvalue
            if value > 150:
                value = 150
            elif value < 0:
                value = 0
            self._force_gauge.set_value(value)
        except BaseException as e:
            logging.error(traceback.format_exc())

    def set_torque_kg(self, value):
        self._force_label.text = '      '
        self._force_label.text = '{:d}kg'.format(value)

    def set_battery_level(self, value):
        self._battery_bar.color = color(value)
        self._battery_bar.value = value


class ForceSelect(Screen):
    _max_force_select = ObjectProperty(None)
    _force_select_display = ObjectProperty(None)

    def biplace(self, value):
        if value:
            self._max_force_select.disabled = True
            self.select_force(130)
        else:
            self._max_force_select.disabled = False
            self.select_force(self._max_force_select.value)

    def select_force(self, value):
        self._force_select_display.text = str(value) + " kg"


class Service(Screen):
    _motor_temperature = ObjectProperty(None)
    _controller_temperature = ObjectProperty(None)
    _charge_level = ObjectProperty(None)
    _min_voltage = ObjectProperty(None)
    _min_cell_address = ObjectProperty(None)

    def set_motor_temperature(self, value):
        self._motor_temperature.text = u'{:d}\u00b0C'.format(value)

    def set_controller_temperature(self, value):
        self._controller_temperature.text = u'{:d}\u00b0C'.format(value)

    def set_charge_level(self, level):
        self._charge_level.text = '{:3.1f}%'.format(level)

    def set_min_cell_address_voltage(self, address, voltage):
        self._min_cell_address.text = str(address)
        self._min_voltage.text = '{:1.2f}V'.format(voltage)


class Calibrate(Screen):
    _fifty_label = ObjectProperty(None)
    _sixty_label = ObjectProperty(None)
    _seventy_label = ObjectProperty(None)
    _eighty_label = ObjectProperty(None)
    _ninety_label = ObjectProperty(None)
    _hundret_label = ObjectProperty(None)
    _onethirty_label = ObjectProperty(None)
    _force_measure_label = ObjectProperty(None)
    _label_index = 0

    def __init__(self, mapping, **kwargs):
        super(Calibrate, self).__init__(**kwargs)
        self._mapping = mapping
        self._labels = [(self._fifty_label, 50), (self._sixty_label, 60), (self._seventy_label, 70),
                        (self._eighty_label, 80), (self._ninety_label, 90), (self._hundret_label, 100),
                        (self._onethirty_label, 130)]
        self.read_label()
        self.highlight(self._label_index)

    def read_label(self):
        for (label, key) in self._labels:
            label.text = str(self._mapping.get(key))

    def set_measure(self, value):
        old = self._force_measure_label.text
        new = str(value)
        if old != new:
            self._force_measure_label.text = new

    def take_over(self):
        value = self._force_measure_label.text
        self._labels[self._label_index][0].text = '[color=ff0000]' + value + '[/color]'
        self._mapping.configure(self._labels[self._label_index][1], int(value))

    def previous_label(self):
        next_index = self._label_index - 1
        if next_index < 0:
            next_index = len(self._labels) - 1
        self.highlight(next_index)

    def next_label(self):
        next_index = self._label_index + 1
        if next_index >= len(self._labels):
            next_index = 0
        self.highlight(next_index)

    def highlight(self, next_index):
        text = self._labels[self._label_index][0].text
        if 'color' in text:
            self._labels[self._label_index][0].text = text[14:-8]
        self._label_index = next_index
        self._labels[self._label_index][0].text = '[color=ff0000]' + self._labels[self._label_index][0].text + '[/color]'


class Battery(Screen):
    _voltage = ObjectProperty(None)
    _level = ObjectProperty(None)

    def set_voltage(self, voltage):
        self._voltage.color = color_voltage(voltage, 30.)
        self._voltage.text = '{:3.2f}Volt'.format(voltage)

    def set_charge_level(self, level):
        self._level.color = color(level)
        self._level.text = '{:3.1f}%'.format(level)


class Display(ScreenManager):
    pass


class DisplayApp(App):
    _connected = False
    _calibrate_measure = 0
    _torque = 0
    _motor_temperature = 0
    _controller_temperature = 0
    _battery_voltage = 0.
    _battery_level = 0.
    """Charge level of the battery. Values between 0 and 100"""
    _min_cell_address = 0
    _min_cell_voltage = 0.

    def __init__(self, devel, mapping):
        self._devel = devel
        self._mapping = mapping
        self._tow = None
        self._service = None
        self._calibrate = None
        self._battery = None
        super(DisplayApp, self).__init__()

    def build(self):
        if self._devel:
            Window.size = (800, 480)
        display = Display()
        display.transition = NoTransition()
        self._tow = Tow()
        display.add_widget(self._tow)
        self._calibrate = Calibrate(self._mapping)
        display.add_widget(self._calibrate)
        display.add_widget(ForceSelect())
        self._service = Service()
        display.add_widget(self._service)
        self._battery = Battery()
        display.add_widget(self._battery)
        display.current = 'battery'

        Clock.schedule_interval(lambda *t: self.update(), 0.05)
        Clock.schedule_interval(lambda *t: self.update_slow(), 0.5)
        Clock.schedule_interval(lambda *t: self.update_battery(), 1)

        return display

    def update(self):
        if self._calibrate:
            self._calibrate.set_measure(self._calibrate_measure)
        if self._tow:
            self._tow.connected(self._connected)
            self._tow.set_torque(self._torque)

    def update_slow(self):
        if self._tow:
            self._tow.set_torque_kg(self._torque)

    def update_battery(self):
        if self._service:
            self._service.set_motor_temperature(self._motor_temperature)
            self._service.set_controller_temperature(self._controller_temperature)
            self._service.set_charge_level(self._battery_level)
            self._service.set_min_cell_address_voltage(self._min_cell_address, self._min_cell_voltage)
        if self._battery:
            self._battery.set_voltage(self._battery_voltage)
            self._battery.set_charge_level(self._battery_level)
        if self._tow:
            self._tow.set_battery_level(self._battery_level)

    def connected(self, connected):
        self._connected = connected

    def set_measure(self, value):
        self._calibrate_measure = value

    def set_torque(self, value):
        self._torque = value

    def set_motor_temperature(self, value):
        self._motor_temperature = value

    def set_controller_temperature(self, value):
        self._controller_temperature = value

    def set_voltage(self, value):
        self._battery_voltage = value

    def set_charge_level(self, value):
        self._battery_level = value

    def set_min_cell_address_voltage(self, address, voltage):
        self._min_cell_address = address
        self._min_cell_voltage = voltage
