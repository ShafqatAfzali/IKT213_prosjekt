import json
from pathlib import Path
from tkinter import OptionMenu, StringVar, BOTH, Button

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
def create_preset_menu(state: State, adjustment_panel):
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

    def save_current_preset():
        name = f"MyPreset{len(load_presets()) + 1}"
        save_preset(name, state.adjustment_values.copy())
        refresh_presets()

    def delete_preset(name: str):
        presets = load_presets()
        if name in presets:
            del presets[name]
            PRESET_FILE.write_text(json.dumps(presets, indent=2))


    def set_preset(image, in_preset):
        for key, value in in_preset.items():
            state.adjustment_values[key] = value

        return image

    def apply_preset():
        presets = get_presets()
        name = preset_var.get()
        if name not in presets:
            return
        adjustments = presets[name]
        state.operations.append((set_preset, [adjustments], {}))
        state.redo_stack.clear()
        update_display_image(state)

    def get_presets():
        presets = {**BUILTIN_PRESETS, **load_presets()}
        return presets

    def refresh_presets():
        presets = get_presets()
        preset_var.set("Select preset")
        preset_menu["menu"].delete(0, "end")
        for name in presets:
            preset_menu["menu"].add_command(label=name, command=lambda n=name: preset_var.set(n))
        return presets

    preset_var = StringVar()
    preset_var.set("Select preset")

    preset_menu = OptionMenu(adjustment_panel, preset_var, "")
    preset_menu.pack(fill=BOTH, pady=5)

    Button(adjustment_panel, text="Apply Preset", command=apply_preset).pack(fill=BOTH, pady=5)
    Button(adjustment_panel, text="Save Preset", command=save_current_preset).pack(fill=BOTH, pady=5)

    refresh_presets()
