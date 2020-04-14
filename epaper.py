import time
from PIL import ImageDraw, ImageFont
from threading import Thread

from IT8951 import constants
from IT8951.display import AutoEPDDisplay


class PaperDisplay(object):
    _display = None
    _draw = None
    _run = True
    _torque_old = 0.0
    _torque_new = 0.0
    _rope_speed_old = 0.0
    _rope_speed_new = 0.0
    _temp_motor_old = None
    _temp_motor_new = None
    _temp_controller_old = None
    _temp_controller_new = None
    _temp_battery_old = None
    _temp_battery_new = None
    _battery_level_old = None
    _battery_level_new = None

    def __init__(self):
        self._thread = Thread(target=self.display_loop, name='ePaper display loop')
        self._thread.start()

    def stop(self):
        self._run = False
        self._thread.join()

    def init(self):
        self._display = AutoEPDDisplay()
        self._draw = ImageDraw.Draw(self._display.frame_buf)

    def build(self):
        # general areas
        self._draw.rectangle([(0, 0), (268, 291)], 0xFF, 0x00, 5)
        self._draw.rectangle([(264, 0), (536, 291)], 0xFF, 0x00, 5)
        self._draw.rectangle([(532, 0), (799, 291)], 0xFF, 0x00, 5)
        self._draw.rectangle([(0, 309), (799, 599)], 0xFF, 0x00, 5)
        # battery
        self._draw.rectangle([(549, 39), (750, 107)], 0xFF, 0x00, 5)
        self._draw.rectangle([(746, 52), (763, 91)], 0xFF, 0x00, 5)
        self._draw.point([(549, 39), (750, 39), (549, 107), (750, 107), (763, 52), (763, 91)], 0xFF)
        self._draw.line([(554, 44), (745, 102)], 0x00, 5)
        # powerbar
        self._draw.rectangle([(16, 426), (745, 508)], 0xFF, 0x00, 3)
        self._draw.line([(746, 427), (782, 427)], 0x00, 3)
        self._draw.line([(746, 507), (782, 507)], 0x00, 3)
        self.draw_torque_lines()
        # texts top left
        self._draw.text((12, 8), 'EWA', font=ImageFont.truetype('fonts/Arial_Black.ttf', 48))
        font = ImageFont.truetype('fonts/Arial_Black.ttf', 32)
        self._draw.text((12, 75), 'Temperaturen', font=font)
        self._draw.text((12, 120), 'Motor', font=font)
        self._draw.text((12, 165), 'Controller', font=font)
        self._draw.text((12, 210), 'Batterie', font=font)
        self._draw.text((259 - font.getsize('28°')[0], 120), '28°', font=font)
        self._draw.text((259 - font.getsize('35°')[0], 165), '35°', font=font)
        self._draw.text((259 - font.getsize('46°')[0], 210), '46°', font=font)
        # texts top middle
        self._draw.text((282, 120), 'V Seil', font=font)
        self._draw.text((282, 165), '38 km/h', font=font)
        # texts top right
        self._draw.text((547, 120), 'Batterie', font=font)
        self._draw.text((547, 165), '78%', font=font)
        # texts in bottom box
        self._draw.text((16, 328), 'Zugkraft in kg', font=font)
        font27 = ImageFont.truetype('fonts/Arial_Black.ttf', 27)
        for i in list(range(0, 11)) + [13]:
            self._draw.text((16 + i * 56 - font27.getsize(str(i * 10))[0] / 2, 520), str(i * 10), font=font27)
        self._display.draw_full(constants.DisplayModes.GC16)

    def draw_torque_lines(self):
        for i in range(0, 14):
            self._draw.line([(16 + i * 56, 429), (16 + i * 56, 525)], 0x00)
        self._draw.line([(744, 426), (744, 508)], 0x00, 3)

    def draw_torque(self, value):
        right = value * 5.6
        self._draw.rectangle([(19, 429), (794, 505)], 0xFF)
        if right > 794:
            right = 794
        if right > 3:
            self._draw.rectangle([(19, 429), (16 + right, 505)], 0x70)
        self.draw_torque_lines()
        return value

    def draw_rope_speed(self, value):
        # TODO
        return value

    def draw_motor_temperature(self, value):
        # TODO
        return value

    def draw_controller_temperature(self, value):
        # TODO
        return value

    def draw_battery_temperature(self, value):
        # TODO
        return value

    def draw_battery_level(self, value):
        # TODO
        return value

    def display_loop(self):
        self.init()
        self.build()
        while self._run:
            changed = False
            if self._torque_old != self._torque_new:
                self._torque_old = self.draw_torque(self._torque_new)
                changed = True
            if not changed and self._rope_speed_old != self._rope_speed_new:
                self._rope_speed_old = self.draw_rope_speed(self._rope_speed_new)
                changed = True
            if not changed:
                if self._temp_motor_old != self._temp_motor_new:
                    self._temp_motor_old = self.draw_motor_temperature(self._temp_motor_new)
                    changed = True
                if self._temp_controller_old != self._temp_controller_new:
                    self._temp_controller_old = self.draw_controller_temperature(self._temp_controller_new)
                    changed = True
                if self._temp_battery_old != self._temp_battery_new:
                    self._temp_battery_old = self.draw_battery_temperature(self._temp_battery_new)
                    changed = True
            if not changed:
                if self._battery_level_old != self._battery_level_new:
                    self._battery_level_old = self.draw_battery_level(self._battery_level_new)
                    changed = True
            if changed:
                self._display.draw_partial(constants.DisplayModes.GC16)
            else:
                # TODO put ePaper into sleep mode
                time.sleep(0.1)

    def set_torque(self, value):
        if value > 140:
            value = 140
        if value < 0:
            value = 0
        self._torque_new = value

    def set_rope_speed(self, value):
        self._rope_speed_new = value

    def set_motor_temperature(self, value):
        self._temp_motor_new = value

    def set_controller_temperature(self, value):
        self._temp_controller_new = value

    def set_battery_temperature(self, value):
        self._temp_battery_new = value

    def set_battery_level(self, value):
        self._battery_level_new = value
