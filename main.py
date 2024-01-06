import serial
import keyboard
import time
import sys

s = serial.Serial('COM7', 1_000_000)

gas = 0
brake = 0
turn_angle = 0
last = 502
value = None


def set_color(red, green, blue, port):
    b = bytearray(b'LED\n')
    b.append(red)
    b.append(green)
    b.append(blue)
    port.write(b)
    port.flush()
    time.sleep(0.01)


def unhandled_exception(exc_type, exc_value, exc_traceback):
    set_color(128, 0, 0, s)
    s.flush()
    raise exc_value


sys.excepthook = unhandled_exception


def buffered_read(port, sep=b'\r\n'):
    while True:
        port.write(b'ready\n')
        port.flush()
        time.sleep(0.1)

        if port.in_waiting != 0:
            val = port.read(4)
            if val == b'OK\r\n':
                break

    GAS_FLAG = 0x0002
    BRAKE_FLAG = 0x0001
    SHIFT_UP_FLAG = 0x0004
    SHIFT_DOWN_FLAG = 0x0008
    TURN_FLAG = 0xFFC0
    V_FLAG = 0xFF0000
    V_OFFSET = 16
    TURN_OFFSET = 6

    while True:
        buffer = port.read(3)
        byte_val = list(map(int, list(buffer)))
        value = (byte_val[2] << 16) + (byte_val[0] << 8) + byte_val[1]
        gas = value & GAS_FLAG != 0
        brake = value & BRAKE_FLAG != 0
        shift_up = value & SHIFT_UP_FLAG != 0
        shift_down = value & SHIFT_DOWN_FLAG != 0
        turn = (value & TURN_FLAG) >> TURN_OFFSET
        vertical = (value & V_FLAG) >> V_OFFSET
        yield gas, brake, shift_up, shift_down, (turn - 522), vertical


# 11000001

pulse_count = 0
last_movement = 0
last_shift_change = 0
gas_pressed = False
brake_pressed = False
left_turn_pressed = False
right_turn_pressed = False
shift_down_pressed = False
shift_up_pressed = False

for gas, brake, shift_up, shift_down, turn, vertical in buffered_read(s):
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

    if turn < -5:
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
        pulse_count = (pulse_count + 1) % max(1, (50 + turn // 10))
    elif turn > 5:
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
        pulse_count = (pulse_count + 1) % max(1, (50 - turn // 10))
    else:
        keyboard.release('d')
        keyboard.release('a')
        left_turn_pressed = False
        right_turn_pressed = False
