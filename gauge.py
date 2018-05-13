import inspect
import os
import logging
import traceback
from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter


class DummyClass:
    pass


class Gauge(Widget):
    _dummy = DummyClass
    _unit = NumericProperty(1.2)
    _value = BoundedNumericProperty(0, min=0, max=150, errorvalue=0)
    _mypath = os.path.dirname(os.path.abspath(inspect.getsourcefile(_dummy)))
    _file_gauge = StringProperty(_mypath + os.sep + 'kilogramms.png')
    _file_needle = StringProperty(_mypath + os.sep + 'needle.png')

    def __init__(self, **kwargs):
        super(Gauge, self).__init__(**kwargs)

        self._scat_gauge = Scatter(do_scale=False, do_translation=False, do_rotation=False)
        self._img_gauge = Image(source=self._file_gauge)

        self._scat_needle = Scatter(do_scale=False, do_translation=False, do_rotation=False)
        self._img_needle = Image(source=self._file_needle)

        self._scat_gauge.add_widget(widget=self._img_gauge)
        self.add_widget(widget=self._scat_gauge)

        self._scat_needle.add_widget(widget=self._img_needle)
        self.add_widget(widget=self._scat_needle)

        self.bind(pos=self._update)
        self.bind(size=self._update)
        self.bind(_value=self._turn)

    def _update(self, *args):
        try:
            # images are 1024 x 1024, but only top 552 pixels contain the gauge
            height = min(self.height, self.width * 552 / 1024)
            width = min(self.width, self.height * 1024 / 552)

            # modify size first otherwise center placing is done with old size
            self._scat_gauge.size = (width, width)
            self._scat_gauge.center = (self.center_x, self.y + height - width / 2)
            # image positioning relative to scat_gauge and not to window and again first size to have correct center
            # positioning
            self._img_gauge.size = self._scat_gauge.size
            self._img_gauge.center = (self._scat_gauge.width / 2, self._scat_gauge.height / 2)

            self._scat_needle.size = self._scat_gauge.size
            self._scat_needle.center = self._scat_gauge.center
            self._img_needle.size = self._scat_needle.size
            self._img_needle.center = (self._scat_needle.width / 2, self._scat_needle.height / 2)
            self._turn()
        except BaseException as e:
            logging.error(traceback.format_exc())

    def _turn(self, *args):
        try:
            self._scat_needle.rotation = 90 - (self._value * self._unit)
        except BaseException as e:
            logging.error(traceback.format_exc())

    def set_value(self, value):
        try:
            self._value = value
            self._turn()
        except BaseException as e:
            logging.error(traceback.format_exc())

    def get_value(self):
        return self._value
