from tkinter import *

from menues.tools_menu import create_tools_menu
from shafqat.shapes import create_shapes_menu
from menues.main_menyer import create_main_menu
from menues.image_menu import create_image_menu
from classes.state import State
from other.helper_functions import update_display_image

if __name__ == "__main__":
    main_window = Tk()
    main_window.title("IKT213 Photo looksmaxer")
    main_window.geometry("600x600")
    main_window.configure(background="black")

    main_frame = Frame(main_window, bg="black")
    main_frame.pack(fill=BOTH, expand=YES)


    canvas = Canvas(main_frame, bg="black")
    canvas.pack(fill=BOTH, expand=YES)


    state = State()
    state.canvas = canvas
    state.main_window = main_window

    canvas.bind("<Configure>", lambda event: update_display_image(state))

    menu_bar = Menu(main_window)
    create_main_menu(state, menu_bar)
    create_image_menu(state, menu_bar)
    create_tools_menu(state, menu_bar)
    create_shapes_menu(menu_bar, state.canvas)

    main_window.config(menu=menu_bar)

    main_window.mainloop()