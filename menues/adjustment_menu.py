from tkinter import Menu, Scale, Toplevel

from classes.state import State
from helpers.image_render import update_display_image


def create_adjustment_menu(state: State, menu_bar):
    def open_brightness_window():
        win = Toplevel(state.main_window)
        win.title("Brightness")
        slider = Scale(
            win, from_=-100, to=100, orient="horizontal",
            command=lambda v: on_brightness_change(int(v))
        )
        slider.set(state.brightness_value)
        slider.pack()

    def on_brightness_change(value):
        state.brightness_value = value
        update_display_image(state)

    adjustment_menu = Menu(menu_bar, tearoff=0)
    adjustment_menu.add_command(label="Brightness", command=open_brightness_window)
    menu_bar.add_cascade(label="Adjustment", menu=adjustment_menu)