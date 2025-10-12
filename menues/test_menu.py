# TODO: Remove in final
import cv2
from cv2 import imshow

from classes.state import State
from tkinter import Menu

from other.helper_functions import update_display_image

def create_test_menu(state: State, menu_bar):
    def show_selection_mask():
        if state.selection_mask is None:
            return
        imshow("mask", state.selection_mask)

    def open_file():
        file_path = r"images/lambo.png"
        state.current_file_path = file_path
        state.original_image = cv2.imread(file_path)
        state.cv_image_full = state.original_image.copy()
        update_display_image(state)



    test_menu = Menu(menu_bar, tearoff=0)
    test_menu.add_command(label="Show mask", command=show_selection_mask)
    test_menu.add_command(label="Open lambo", command=open_file)
    state.canvas.bind_all("<Control-a>", lambda _: open_file())

    menu_bar.add_cascade(label="Test", menu=test_menu)

