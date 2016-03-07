import sys

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner


class DisplayWidget(Widget):
    gauge = ObjectProperty(None)
    slider = ObjectProperty(None)


    def __init__(self, **kwargs):
        super(DisplayWidget, self).__init__(**kwargs)
        self.gauge.value = self.slider.value


class DisplayApp(App):
    def build(self):
        return DisplayWidget()


def main():
    DisplayApp().run()
    return 0


if __name__ == '__main__':
    sys.exit(main())