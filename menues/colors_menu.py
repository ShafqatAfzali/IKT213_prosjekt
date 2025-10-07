from tkinter import *
from tkinter import colorchooser

from classes.state import State


def create_colors_menu(state: State, menu_bar):
    def choose_color():
        color = colorchooser.askcolor(title="Velg farge")[0]
        if color:
            state.brush_color = color

    def set_brush_size(brush_size):
        state.brush_size = brush_size

    colors_menu = Menu(menu_bar, tearoff=0)
    size_menu = Menu(colors_menu, tearoff=0)
    for size in [2, 5, 10, 15, 20, 30]:
        size_menu.add_radiobutton(label=f"{size}px", command=lambda s=size: set_brush_size(s))
    colors_menu.add_cascade(label="Penselstørrelse", menu=size_menu)

    colors_menu.add_command(label="Velg farge", command=choose_color)

    menu_bar.add_cascade(label="Colors", menu=colors_menu)
