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
    unit = NumericProperty(1.2)
    value = BoundedNumericProperty(0, min=0, max=150, errorvalue=0)
    mypath = os.path.dirname(os.path.abspath(inspect.getsourcefile(dummy)))
    file_gauge = StringProperty(mypath + os.sep + 'kilogramms.png')
    file_needle = StringProperty(mypath + os.sep + 'needle.png')

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
        # images are 1024 x 1024, but only top 552 pixels contain the gauge
        height = min(self.height, self.width * 552 / 1024)
        width = min(self.width, self.height * 1024 / 552)

        # modify size first otherwise center placing is done with old size
        self.scat_gauge.size = (width, width)
        self.scat_gauge.center = (self.center_x, self.y + height - width / 2)
        # image positioning relative to scat_gauge and not to window and again first size to have correct center
        # positioning
        self.img_gauge.size = self.scat_gauge.size
        self.img_gauge.center = (self.scat_gauge.width / 2, self.scat_gauge.height / 2)

        self.scat_needle.size = self.scat_gauge.size
        self.scat_needle.center = self.scat_gauge.center
        self.img_needle.size = self.scat_needle.size
        self.img_needle.center = (self.scat_needle.width / 2, self.scat_needle.height / 2)
        self._turn()

    def _turn(self):
        self.scat_needle.rotation = 90 - (self.value * self.unit)
