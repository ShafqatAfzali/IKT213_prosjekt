from tkinter import *

import cv2

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

    menu_bar = Menu(main_window)

    canvas = Canvas(main_frame, bg="black")
    canvas.pack(fill=BOTH, expand=YES)

    canvas.bind("<Configure>", lambda event: update_display_image(state))

    state = State()
    state.canvas = canvas
    state.main_window = main_window

    create_main_menu(state, menu_bar)
    create_shapes_menu(menu_bar, canvas)
    create_image_menu(state, menu_bar)

    menu_bar.add_command(label="Test", command=lambda: cv2.imshow("", state.cv_image_full))
    menu_bar.add_command(label="Test2", command=lambda: cv2.imshow("", state.selection_mask))
    main_window.config(menu=menu_bar)

    main_window.mainloop()