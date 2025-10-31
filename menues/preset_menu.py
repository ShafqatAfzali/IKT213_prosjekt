import json
from pathlib import Path
from tkinter import Menu
from classes.state import State
from helpers.image_render import update_display_image

BUILTIN_PRESETS = {
    "vintage": {
        "contrast": 1.05,
        "brightness": 5,
        "saturation": 0.85,
        "white_balance": 15,
        "tone_curve_strength": 0.5,
        "vignette_strength": 0.25,
        "grayscale": False,
    },
    "cinematic": {
        "contrast": 1.2,
        "brightness": -3,
        "saturation": 0.9,
        "white_balance": -5,
        "tone_curve_strength": 0.8,
        "vignette_strength": 0.15,
        "grayscale": False,
    },
    "bw": {
        "contrast": 1.1,
        "brightness": 0,
        "saturation": 0.0,
        "white_balance": 0,
        "tone_curve_strength": 0.4,
        "vignette_strength": 0.0,
        "grayscale": True,
    },
}


PRESET_FILE = Path("data/presets.json")

def load_presets():
    if PRESET_FILE.exists():
        try:
            return json.loads(PRESET_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_preset(name: str, adjustments: dict):
    presets = load_presets()
    presets[name] = adjustments
    PRESET_FILE.write_text(json.dumps(presets, indent=2))

def delete_preset(name: str):
    presets = load_presets()
    if name in presets:
        del presets[name]
        PRESET_FILE.write_text(json.dumps(presets, indent=2))


def create_preset_menu(state: State, menu_bar):
    def set_preset(image, in_preset):
        for key, value in in_preset.items():
            state.adjustment_values[key] = value

        return image

    def apply_preset(in_preset):
        print(in_preset)
        state.operations.append((set_preset, [in_preset], {}))
        state.redo_stack.clear()
        update_display_image(state)

