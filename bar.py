import logging
from kivy.lang import Builder
from kivy.properties import (
    BoundedNumericProperty,
    ListProperty,
    ObjectProperty
)
from kivy.uix.widget import Widget


Builder.load_string('''
<Bar>:
    _label: label
    canvas:
        Color:
            rgba: root.background_color
        Rectangle:
            pos: root.pos
            size: root.size
        Color:
            rgba: root.color
        Rectangle:
            pos: (self.x+2, self.y+2)
            size: ((self.width-4)*self.value/100., self.height-4)
    Label:
        center: root.center
        color: [0, 0, 0, 1]
        bold: True
        id: label
''')


class Bar(Widget):
    background_color = ListProperty([0, 0, 0, 1])
    color = ListProperty([1, 1, 1, 1])
    value = BoundedNumericProperty(0., min=0., max=100.)
    _label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Bar, self).__init__(**kwargs)
        self.bind(value=self._update)

    def _update(self, *args):
        self._label.text = '{:3.0f}%'.format(self.value)