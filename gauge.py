import inspect
import os

from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter


class DummyClass:
    pass


class Gauge(Widget):
    dummy = DummyClass
    unit = NumericProperty(1.8)
    value = BoundedNumericProperty(0, min=0, max=100, errorvalue=0)
    mypath = os.path.dirname(os.path.abspath(inspect.getsourcefile(dummy)))
    file_gauge = StringProperty(mypath + os.sep + "gauge.png")
    file_needle = StringProperty(mypath + os.sep + "needle.png")

    def __init__(self, **kwargs):
        super(Gauge, self).__init__(**kwargs)

        self.scat_gauge = Scatter(do_scale=False, do_translation=False, do_rotation=False)
        self.img_gauge = Image(source=self.file_gauge)

        self.scat_needle = Scatter(do_scale=False, do_translation=False, do_rotation=False)
        self.img_needle = Image(source=self.file_needle)

        self.scat_gauge.add_widget(widget=self.img_gauge)
        self.add_widget(widget=self.scat_gauge)

        self.scat_needle.add_widget(widget=self.img_needle)
        self.add_widget(widget=self.scat_needle)

        self.bind(pos=self._update)
        self.bind(size=self._update)
        self.bind(value=self._turn)

    def _update(self, *args):
        self.scat_gauge.size = (self.width, self.width)
        self.scat_gauge.pos = (self.x, self.y + self.height - self.width)
        self.img_gauge.size = self.scat_gauge.size
        self.img_gauge.center = (self.scat_gauge.width / 2, self.scat_gauge.height / 2)

        self.scat_needle.size = self.scat_gauge.size
        self.scat_needle.center = self.scat_gauge.center
        self.img_needle.size = self.scat_needle.size
        self.img_needle.center = (self.scat_needle.width / 2, self.scat_needle.height / 2)
        self._turn()

    def _turn(self, *args):
        self.scat_needle.rotation = (50 * self.unit) - (self.value * self.unit)
