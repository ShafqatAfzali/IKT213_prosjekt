from tkinter import Menu, Scale, Toplevel
from classes.state import State
from helpers.image_render import update_display_image


def create_adjustment_menu(state: State, menu_bar):
    def create_adjustment_slider(label, key, min_val, max_val, resolution=1.0):
        def on_drag(value):
            state.preview_adjust = True
            state.preview_values[key] = type(state.adjustment_values[key])(value)
            update_display_image(state)

        def set_adjustment_value(image, value, key):
            state.adjustment_values[key] = value
            return image

        def on_release():
            state.preview_adjust = False
            value = state.preview_values[key]
            state.operations.append((set_adjustment_value, [value, key], {}))
            state.redo_stack.clear()
            update_display_image(state)

        def open_slider_window():
            win = Toplevel(state.main_window)
            win.title(label)
            slider = Scale(
                win,
                from_=min_val,
                to=max_val,
                resolution=resolution,
                orient="horizontal",
                command=lambda v: on_drag(v),
            )
            slider.set(state.adjustment_values[key])
            slider.pack()
            slider.bind("<ButtonRelease-1>", lambda e: on_release())

        return open_slider_window

    adjustment_menu = Menu(menu_bar, tearoff=0)
    adjustment_menu.add_command(label="Brightness", command=create_adjustment_slider("Brightness", "brightness", -100, 100, 1))
    adjustment_menu.add_command(label="Contrast", command=create_adjustment_slider("Contrast", "contrast", 0.5, 2.0, 0.1))
    adjustment_menu.add_command(label="Saturation", command=create_adjustment_slider("Saturation", "saturation", 0.0, 2.0, 0.1))
    adjustment_menu.add_command(label="Exposure", command=create_adjustment_slider("Exposure", "exposure", 0.5, 2.0, 0.1))
    adjustment_menu.add_command(label="White balance", command=create_adjustment_slider("White Balance", "white_balance", -100, 100, 1))
    menu_bar.add_cascade(label="Adjustment", menu=adjustment_menu)