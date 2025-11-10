import sys
import os

from menues.AI_white_exposure_menu import create_ai_white_exposure_menu
from menues.adjustment_menu import create_adjustment_menu
from menues.test_menu import create_test_menu

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tkinter import *
from classes.state import State
from helpers.image_render import update_display_image
from menues.tools_menu import create_tools_menu
from menues.main_menu import create_main_menu
from menues.image_menu import create_image_menu
from menues.colors_menu import create_colors_menu
from menues.shapes_menu import create_shapes_menu
from menues.local_menu import create_local_menu


if __name__ == "__main__":
    main_window = Tk()
    main_window.title("IKT213 Photo looksmaxer")
    main_window.geometry("600x600")
    main_window.configure(background="black")

    main_frame = Frame(main_window, bg="black")
    # noinspection PyTypeChecker
    main_frame.pack(fill=BOTH, expand=YES)

    canvas = Canvas(main_frame, bg="black")
    # noinspection PyTypeChecker
    canvas.pack(side=LEFT, fill=BOTH, expand=YES)
    canvas.bind("<Configure>", lambda event: update_display_image(state))
    canvas.focus_set()

    state = State()
    state.canvas = canvas
    state.main_window = main_window
    state.main_frame = main_frame


    menu_bar = Menu(main_window)

    create_main_menu(state, menu_bar)
    create_image_menu(state, menu_bar)
    create_tools_menu(state, menu_bar)
    create_shapes_menu(state, menu_bar)
    create_colors_menu(state, menu_bar)
    create_adjustment_menu(state, menu_bar)
    create_local_menu(state, menu_bar)
    create_ai_white_exposure_menu(state, menu_bar)
    main_window.config(menu=menu_bar)
    main_window.mainloop()