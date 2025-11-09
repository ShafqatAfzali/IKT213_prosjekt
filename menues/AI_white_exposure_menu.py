from tkinter import Menu

import cv2
import numpy as np

import torch
from torchvision import transforms
from PIL import Image

from classes.state import State
from helpers.image_render import update_display_image


def create_ai_white_exposure_menu(state: State, menu_bar):
    def predict_gains():
        pass

    def set_gains(b,g,r):
        state.adjustment_values["b_gain"] = b
        state.adjustment_values["g_gain"] = g
        state.adjustment_values["r_gain"] = r

    def apply_auto():
        r,g,b = predict_gains()
        state.operations.append([set_gains, [], {"b": b, "g": g, "r": r}])
        state.redo_stack.clear()
        update_display_image(state)


    ai_white_exposure_menu = Menu(menu_bar, tearoff=0)
    ai_white_exposure_menu.add_command(label="Test", command=apply_auto)
    ai_white_exposure_menu.add_command(label="AAAHHH", command=predict_gains)
    menu_bar.add_cascade(label="White exposure", menu=ai_white_exposure_menu)