import serial
import keyboard
import time
import sys

current_controller = None


class GameController:
    def __init__(self):
        self.port = serial.Serial('COM7', 1_000_000)

    def set_color(self, red, green, blue):
        set_color(red, green, blue, self.port)

    def start_input(self):
        port = self.port
        global current_controller
        current_controller = self
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
        self.inputs = {'left_vrx': left_vrx, 'left_vry': left_vry, 'right_vrx': right_vrx, 'right_vry': right_vry,
                       'left_pressed': left_pressed, 'right_pressed': right_pressed, 'left_js_pressed': left_js_pressed,
                       'right_js_pressed': right_js_pressed}
        self.analog_inputs = ['left_vrx', 'left_vry', 'right_vrx', 'right_vry']
        self.last = last
        self.changes = {}
        for key in self.inputs:
            if (last is None or self.inputs[key] != last.inputs[key] and key not in self.analog_inputs or key in self.analog_inputs
                    and abs(self.inputs[key] - last.inputs[key]) > 5):
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
    time.sleep(0.01)


def unhandled_exception(exc_type, exc_value, exc_traceback):
    if current_controller is None:
        raise exc_value

    set_color(128, 0, 0, current_controller)
    current_controller.flush()
    raise exc_value


sys.excepthook = unhandled_exception


def old():
    pulse_count = 0
    last_movement = 0
    last_shift_change = 0
    gas_pressed = False
    brake_pressed = False
    left_turn_pressed = False
    right_turn_pressed = False
    shift_down_pressed = False
    shift_up_pressed = False

    gc = GameController()

    for controls in gc.start_input():
        vertical = controls.inputs['right_vry']
        turn = (controls.inputs['left_vrx'] << 2) - 524
        shift_up = controls.inputs['right_js_pressed']
        shift_down = controls.inputs['left_js_pressed']
        gas = vertical < 100
        brake = vertical > 140

        if gas:
            if not gas_pressed:
                keyboard.press('w')
                gas_pressed = True
        else:
            if gas_pressed:
                keyboard.release('w')
                gas_pressed = False
        if brake:
            if not brake_pressed:
                keyboard.press('s')
                brake_pressed = True
        else:
            if brake_pressed:
                keyboard.release('s')
                brake_pressed = False

        if shift_up:
            if not shift_up_pressed:
                keyboard.press("'")
                shift_up_pressed = True
        else:
            if shift_up_pressed:
                keyboard.release("'")
                shift_up_pressed = False

        if shift_down:
            if not shift_down_pressed:
                shift_down_pressed = True
                keyboard.press('/')
        else:
            if shift_down_pressed:
                keyboard.release('/')
                shift_down_pressed = False

        if turn > 5:
            right_turn_pressed = False
            if last_movement == 1:
                pulse_count = 0
            last_movement = 2
            keyboard.release('a')
            if pulse_count == 0:
                if not left_turn_pressed:
                    keyboard.press('d')
                    left_turn_pressed = True
            elif pulse_count == 30:
                if left_turn_pressed:
                    keyboard.release('d')
                    left_turn_pressed = False
            pulse_count = (pulse_count + 1) % max(1, (80 - turn // 10))
        elif turn < -5:
            left_turn_pressed = False
            if last_movement == 2:
                pulse_count = 0
            last_movement = 1
            keyboard.release('d')
            if pulse_count == 0:
                if not right_turn_pressed:
                    keyboard.press('a')
                    right_turn_pressed = True
            elif pulse_count == 30:
                if right_turn_pressed:
                    keyboard.release('a')
                    right_turn_pressed = False
            pulse_count = (pulse_count + 1) % max(1, (80 + turn // 10))
        else:
            keyboard.release('d')
            keyboard.release('a')
            left_turn_pressed = False
            right_turn_pressed = False

old()
