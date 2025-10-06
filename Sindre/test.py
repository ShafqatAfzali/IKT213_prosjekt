from tkinter import *

import cv2

from shafqat.shapes import create_shapes_menu
from Erling.main_menyer import create_main_menu
from Sindre.Image_menu import create_image_menu
from Sindre.helper_functions import cv2_to_tk

main_window = Tk()
main_window.title("IKT213 Photo looksmaxer")
main_window.geometry("600x600")
main_window.configure(background="black")

main_frame = Frame(main_window, bg="black")
main_frame.pack(fill=BOTH, expand=YES)

menu_bar = Menu(main_window)

canvas = Canvas(main_frame, bg="black")
canvas.pack(fill=BOTH, expand=YES)

cv_image_full = cv2.imread("./img.png")
cv_image_display = cv_image_full
tk_background_image = cv2_to_tk(cv_image_display)
canvas.create_image(0, 0, anchor="nw", image=tk_background_image)

state = {
    "cv_image_full": cv_image_full,
    "cv_image_display": cv_image_display,
    "canvas": canvas,
    "tk_image": tk_background_image,
    "selection_points": [],
    "selection_shape_ids": [],
    "selection_mask": None
}

create_main_menu(menu_bar, canvas, main_window)
create_shapes_menu(menu_bar, canvas)
create_image_menu(state, menu_bar)

menu_bar.add_command(label="Test", command=lambda: cv2.imshow("", state["cv_image_full"]))
menu_bar.add_command(label="Test2", command=lambda: cv2.imshow("", state["selection_mask"]))
main_window.config(menu=menu_bar)

main_window.mainloop()