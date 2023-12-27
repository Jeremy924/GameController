import json

import GameController


class KeyMapper:
    def __init__(self, key_map_json: dict):
        self.controller = GameController.GameController()
        self.keys_down = set()

        groups = {}

        for group, value in key_map_json.items():
            current_key_map = {}

            for controller_input, mapped_key in value.items():
                current_key_map[frozenset(controller_input.split('&'))] = frozenset(mapped_key.split('&'))

            groups[group] = current_key_map
        # exec('self.set_led(0, 0, 100)')
        self.groups = groups

    def connect(self):
        for next_instance in self.controller.start_input():
            if str(next_instance) != '{}':
                print(next_instance)

    def set_led(self, red, green, blue):
        self.controller.set_color(red, green, blue)

    def on_input(self, controller_input: GameController.ControllerInput):
        if str(controller_input.changes) != '{}':
            print(controller_input.changes)


a = KeyMapper(json.load(open('forza_keymap.json')))
a.connect()
