import json
import keyboard
import GameController


class KeyBinding:
    def __init__(self, input_match: str, key_binding: str, controller: GameController):
        self.input_match = input_match.split('&')
        self.key_binding = key_binding.split('&')
        self.controller = controller

        self.analog_inputs = ['LEFT_VL', 'LEFT_VR', 'LEFT_VU', 'LEFT_VD', 'RIGHT_VL', 'RIGHT_VR', 'RIGHT_VU',
                              'RIGHT_VD']

        self.pwm = 0

        if self.input_match[0].startswith('#'):
            self.is_analog = True
            if len(self.input_match) != 1:
                raise Exception("Can not match multiple inputs with pulse width modulation")
            self.input_match[0] = self.input_match[0][1:]

            if self.input_match[0] not in self.analog_inputs:
                raise Exception(f"Input {self.input_match[0]} is not an analog input")
        else:
            self.is_analog = False

        self.pressed = [False] * len(self.key_binding)

    def __eq__(self, other):
        return self.input_match == other.input_match

    def __str__(self):
        return f'{self.input_match} -> {self.key_binding}'

    def is_input_match(self, controller_input: GameController.ControllerInput):
        if self.is_analog and self.input_match[0] in controller_input.inputs:
            return controller_input.inputs[self.input_match[0]]
        elif self.is_analog:
            return -1

        state = -1

        for ci in self.input_match:
            if ci not in controller_input.changes:
                return -1
            input_val = controller_input.changes[ci] if ci not in self.analog_inputs or self.is_analog else \
            controller_input.changes[ci] > 5
            if input_val != state and state != -1:
                return -1
            state = input_val

        return state

    def on_press(self):
        for i in range(len(self.key_binding)):
            if self.key_binding[i][0] not in '@\\':
                if not self.pressed[i]:
                    keyboard.press(self.key_binding[i])
                    self.pressed[i] = True

    def on_release(self):
        for i in range(len(self.key_binding)):
            if self.key_binding[i][0] not in '@\\':
                if self.pressed[i]:
                    keyboard.release(self.key_binding[i])
                    self.pressed[i] = False


class KeyMapper:
    def __init__(self, key_map_json: dict):
        self.controller = GameController.GameController()

        self.left_center = (130, 128)
        self.right_center = (128, 128)

        self.current_binding = "main"
        self.key_bindings = {}
        for name, key_binding in key_map_json.items():
            next_key_bindings = []
            for input_match, key in key_binding.items():
                next_key_bindings.append(KeyBinding(input_match, key, self.controller))
            self.key_bindings[name] = next_key_bindings
            # self.key_bindings.append(KeyBinding(input_match, key_binding, self.controller))

    def connect(self):
        old_binding = ['']
        for next_instance in self.controller.start_input():
            if len(next_instance.changes) == 0:
                continue

            changes = next_instance.inputs
            if "LEFT_VRX" in changes:
                changes['LEFT_VL'] = self.left_center[0] - changes['LEFT_VRX']
                changes['LEFT_VR'] = changes['LEFT_VRX'] - self.right_center[0]
            if "LEFT_VRY" in changes:
                changes['LEFT_VU'] = self.left_center[1] - changes['LEFT_VRY']
                changes['LEFT_VD'] = changes['LEFT_VRY'] - self.left_center[1]
            if "RIGHT_VRX" in changes:
                changes['RIGHT_VL'] = self.right_center[0] - changes['RIGHT_VRX']
                changes['RIGHT_VR'] = changes['RIGHT_VRX'] - self.right_center[0]
            if "RIGHT_VRY" in changes:
                changes['RIGHT_VU'] = self.right_center[1] - changes['RIGHT_VRY']
                changes['RIGHT_VD'] = changes['RIGHT_VRY'] - self.right_center[1]

            if self.current_binding != old_binding[-1]:
                old_binding.append(self.current_binding)
                if KeyBinding('INIT', '', None) in self.key_bindings[self.current_binding]:
                    init_binding = None
                    for binding in self.key_bindings[self.current_binding]:
                        if binding == KeyBinding('INIT', '', None):
                            init_binding = binding
                            break
                    for step in init_binding.key_binding:
                        if step[0] == '@':
                            if step == '@return':
                                self.current_binding = old_binding.pop()
                            else:
                                self.current_binding = step[1:]
                            break
                        elif step[0] == '\\':
                            exec('self.' + step[1:])

            for binding in self.key_bindings[self.current_binding]:
                state = binding.is_input_match(next_instance)
                if state == -1:
                    continue
                if state and not binding.is_analog or binding.is_analog and state > 5:
                    for step in binding.key_binding:
                        if step[0] == '@':
                            self.current_binding = step[1:]
                            break
                        elif step[0] == '\\':
                            exec('self.' + step[1:])
                    binding.on_press()
                else:
                    binding.on_release()

    def set_led(self, red, green, blue):
        self.controller.set_color(red, green, blue)

    def on_input(self, controller_input: GameController.ControllerInput):
        if str(controller_input.changes) != '{}':
            print(controller_input.changes)


a = KeyMapper(json.load(open('forza_keymap.json')))
a.connect()
