from tkinter import Menu

import cv2
import torch
from PIL import Image

from Deep_White_Balance.PyTorch.arch import deep_wb_single_task
from Deep_White_Balance.PyTorch.utilities.deepWB import deep_wb
import Deep_White_Balance.PyTorch.utilities.utils as utls

from classes.state import State
from helpers.image_render import update_display_image


def create_ai_white_exposure_menu(state: State, menu_bar):
    def predict_gains():
        net_awb = deep_wb_single_task.deepWBnet()
        device = torch.device('cpu')
        net_awb.to(device=device)
        net_awb.load_state_dict(torch.load("Deep_White_Balance/PyTorch/models/net_awb.pth", map_location=device))
        net_awb.eval()

        resized_image = cv2.resize(state.cv_image_full, (656, 656))
        rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_image)
        out_awb = deep_wb(pil_img, task="awb", net_awb=net_awb, device=device, s=656)
        result_awb = utls.to_image(out_awb)
        result_awb.save('AAAAAAAAAAAAAAAAAA_AWB.png')



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
    ai_white_exposure_menu.add_command(label="AAAHHH", command=predict_gains)
    menu_bar.add_cascade(label="White exposure", menu=ai_white_exposure_menu)