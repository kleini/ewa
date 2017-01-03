import sys

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window


class Display(BoxLayout):
    gauge = ObjectProperty(None)
    slider = ObjectProperty(None)

    def set_gauge(self, value):
        print(self.gauge.size)
        self.gauge.value = value


class DisplayApp(App):
    def build(self):
        return Display()

def main():
    Window.size = (800, 480)
    DisplayApp().run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
