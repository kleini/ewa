from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.pagelayout import PageLayout
from kivy.graphics import Color, Ellipse
from kivy.uix.widget import Widget


class Connected(Widget):
    def __init__(self, **kwargs):
        super(Connected, self).__init__(**kwargs)
        with self.canvas:
            self.color = Color(1, 0, 0)
            self.circle = Ellipse(pos=self.pos, size=self.size)
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
        self.circle.pos = self.pos
        self.circle.size = self.size


class Display(PageLayout):
    _force_gauge = ObjectProperty(None)
    force_label = ObjectProperty(None)
    force_measure_label = ObjectProperty(None)
    max_force_select = ObjectProperty(None)
    force_select_display = ObjectProperty(None)
    connected_color = ObjectProperty(None)

    def set_torque(self, value):
        self.force_label.text = str(value) + " kg"
        # don't fall into errorvalue
        if value > 150:
            value = 150
        elif value < 0:
            value = 0
        self._force_gauge.value = value

    def biplace(self, value):
        if value:
            self.max_force_select.disabled = True
            self.select_force(130)
        else:
            self.max_force_select.disabled = False
            self.select_force(self.max_force_select.value)

    def select_force(self, value):
        self.force_select_display.text = str(value) + " kg"

    def connected(self, connected):
        self.connected_color.connected(connected)


class DisplayApp(App):
    def __init__(self, devel):
        self.devel = devel
        self.display = None
        super(DisplayApp, self).__init__()

    def build(self):
        if self.devel:
            Window.size = (800, 480)
        self.display = Display()
        return self.display
