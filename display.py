import logging
import traceback
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.widget import Widget


Builder.load_file('display.kv')


class Connected(Widget):
    def __init__(self, **kwargs):
        super(Connected, self).__init__(**kwargs)
        with self.canvas:
            self.color = Color(1, 0, 0)
            self._circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.draw, size=self.draw)

    def connected(self, connected):
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
    _force_label = ObjectProperty(None)
    _connected_color = ObjectProperty(None)

    def connected(self, connected):
        self._connected_color.connected(connected)

    def set_torque(self, value):
        try:
            self._force_label.text = "      "
            self._force_label.text = str(value) + " kg"
            # don't fall into errorvalue
            if value > 150:
                value = 150
            elif value < 0:
                value = 0
            self._force_gauge.set_value(value)
        except BaseException as e:
            logging.error(traceback.format_exc())


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
    pass


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
        self._force_measure_label.text = str(value)

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
    pass


class Display(ScreenManager):
    pass


class DisplayApp(App):
    def __init__(self, devel, mapping):
        self._devel = devel
        self._mapping = mapping
        self._tow = None
        self._calibrate = None
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
        display.add_widget(Service())
        display.add_widget(Battery())
        display.current = 'battery'
        return display

    def connected(self, connected):
        if self._tow:
            self._tow.connected(connected)

    def set_measure(self, value):
        if self._calibrate:
            self._calibrate.set_measure(value)

    def set_torque(self, value):
        if self._tow:
            self._tow.set_torque(value)

    def set_motor_temperature(self, value):
        pass

    def set_controller_temperature(self, value):
        pass

    def set_voltage(self, value):
        pass

    def set_charge_level(self, value):
        pass

    def set_minimum_voltage(self, value):
        pass

    def set_min_cell_address(self, value):
        pass
