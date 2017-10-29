import sys

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.pagelayout import PageLayout


class Display(PageLayout):
    torque_gauge = ObjectProperty(None)
    force_select_button = ObjectProperty(None)
    max_force_select = ObjectProperty(None)
    force_select_display = ObjectProperty(None)

    def set_torque(self, value):
        self.torque_gauge.value = value

    def biplace(self, value):
        if value:
            self.max_force_select.disabled = True
            self.select_force(130)
        else:
            self.max_force_select.disabled = False
            self.select_force(self.max_force_select.value)

    def select_force(self, value):
        self.force_select_display.text = str(value) + " kg"
        self.force_select_button.text = str(value) + " kg"


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
