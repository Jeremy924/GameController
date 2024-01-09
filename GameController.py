import serial
import time
import sys


class GameController:
    current_controller = None

    def __init__(self):
        self.port = serial.Serial('COM7', 1_000_000)
        self.analog_inputs = ['LEFT_VRX', 'LEFT_VRY', 'RIGHT_VRX', 'RIGHT_VRY']

    @classmethod
    def set_current_controller(cls, controller):
        cls.current_controller = controller

    @classmethod
    def get_current_controller(cls):
        return cls.current_controller

    def set_color(self, red, green, blue):
        set_color(red, green, blue, self.port)

    def start_input(self):
        port = self.port
        GameController.current_controller = self
        while True:
            port.write(b'ready\n')
            port.flush()
            time.sleep(0.1)

            if port.in_waiting != 0:
                val = port.read(4)
                if val == b'OK\r\n':
                    break

        LEFT_JS_BUTTON = 0x02
        RIGHT_BUTTON = 0x04
        RIGHT_JS_BUTTON = 0x08
        last_input = None

        while True:
            buffer = port.read(5)
            byte_val = list(map(int, list(buffer)))
            left_vrx = byte_val[0]
            left_vry = byte_val[1]
            right_vrx = byte_val[2]
            right_vry = byte_val[3]
            left_pressed = byte_val[4] & 1 == 1
            right_pressed = byte_val[4] & RIGHT_BUTTON != 0
            left_js_pressed = byte_val[4] & LEFT_JS_BUTTON != 0
            right_js_pressed = byte_val[4] & RIGHT_JS_BUTTON != 0

            last_input = ControllerInput(left_vrx, left_vry, right_vrx, right_vry, left_pressed, right_pressed,
                                         left_js_pressed, right_js_pressed, last_input)
            yield last_input


class ControllerInput:
    def __init__(self, left_vrx, left_vry, right_vrx, right_vry, left_pressed,
                 right_pressed, left_js_pressed, right_js_pressed, last):
        self.inputs = {'LEFT_VRX': left_vrx, 'LEFT_VRY': left_vry, 'RIGHT_VRX': right_vrx, 'RIGHT_VRY': right_vry,
                       'LEFT_BUTTON': left_pressed, 'RIGHT_BUTTON': right_pressed, 'LEFT_JS_BUTTON': left_js_pressed,
                       'RIGHT_JS_BUTTON': right_js_pressed}
        self.analog_inputs = ['LEFT_VRX', 'LEFT_VRY', 'RIGHT_VRX', 'RIGHT_VRY']
        self.last = last
        self.changes = {}
        for key in self.inputs:
            if (last is None or self.inputs[key] != last.inputs[
                key] and key not in self.analog_inputs or key in self.analog_inputs
                    and abs(self.inputs[key] - last.inputs[key]) > 0):
                self.changes[key] = self.inputs[key]

    def __str__(self):
        return str(self.changes)


def set_color(red, green, blue, port):
    b = bytearray(b'LED\n')
    b.append(red)
    b.append(green)
    b.append(blue)
    port.write(b)
    port.flush()


def unhandled_exception(exc_type, exc_value, exc_traceback):
    if GameController.current_controller is None:
        raise exc_value

    if GameController.current_controller is not None:
        GameController.current_controller.set_color(128, 0, 0)
        GameController.current_controller.port.flush()
    raise exc_value


sys.excepthook = unhandled_exception
