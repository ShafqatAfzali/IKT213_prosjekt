from tkinter import Frame, Label, Scale, BOTH, RIGHT, HORIZONTAL
from classes.state import State
from helpers.image_render import update_display_image
from menues.preset_menu import create_preset_menu


def create_adjustment_menu(state: State, menu_bar):
    panel_width = 250

    def toggle_adjustment_panel():
        # If already open, close it
        if hasattr(state, "adjustment_panel") and state.adjustment_panel.winfo_exists():
            state.adjustment_panel.destroy()
            delattr(state, "adjustment_panel")
            return

        # Create new panel
        adjustment_panel = Frame(state.main_frame, bg="#222", width=panel_width)
        # noinspection PyTypeChecker
        adjustment_panel.pack(side=RIGHT, fill=BOTH)

        def add_slider(label, key, min_val, max_val, resolution=1.0):
            Label(adjustment_panel, text=label, bg="#2b2b2b", fg="white").pack()
            # noinspection PyTypeChecker
            slider = Scale(
                adjustment_panel,
                from_=min_val,
                to=max_val,
                resolution=resolution,
                orient=HORIZONTAL,
                command=lambda v: on_drag(v, key),
            )
            slider.set(state.adjustment_values[key])
            slider.pack(fill="x")
            slider.bind("<ButtonPress-1>", lambda e, k=key: start_preview(k))
            slider.bind("<ButtonRelease-1>", lambda e: on_release(key))

        def start_preview(key):
            state.preview_values = state.adjustment_values.copy()

        def on_drag(value, key):
            if state.preview_values is None:
                return
            state.preview_values[key] = type(state.adjustment_values[key])(value)
            update_display_image(state)

        def set_adjustment_value(image, value, key):
            state.adjustment_values[key] = value
            return image

        def on_release(key):
            value = state.preview_values[key]
            state.operations.append((set_adjustment_value, [value, key], {}))
            state.preview_values = None
            state.redo_stack.clear()
            update_display_image(state)

        # Add sliders
        add_slider("Brightness", "brightness", -100, 100, 1)
        add_slider("Contrast", "contrast", 0.5, 2.0, 0.1)
        add_slider("Saturation", "saturation", 0.0, 2.0, 0.1)
        add_slider("Exposure", "exposure", 0.5, 2.0, 0.1)
        add_slider("White balance", "white_balance", -100, 100, 1)

        create_preset_menu(state, adjustment_panel)

    menu_bar.add_command(label="Adjustment", command=toggle_adjustment_panel)
