import cv2
import numpy as np
import torch
from PIL import Image

from Deep_White_Balance.PyTorch.arch import deep_wb_single_task
from Deep_White_Balance.PyTorch.utilities.deepWB import deep_wb
import Deep_White_Balance.PyTorch.utilities.utils as utls

from classes.state import State
from helpers.image_render import update_display_image


def create_ai_white_exposure_menu(state: State, menu_bar):
    def to_linear(img):
        if not isinstance(img, np.ndarray):
            img = np.array(img)

        img = img.astype(np.float32) / 255.0
        return np.power(img, 2.2)

    def predict_gains():
        net_awb = deep_wb_single_task.deepWBnet()
        device = torch.device('cpu')
        net_awb.to(device=device)
        net_awb.load_state_dict(torch.load("Deep_White_Balance/PyTorch/models/net_awb.pth", map_location=device))
        net_awb.eval()

        rgb_image = cv2.cvtColor(state.cv_image_full, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_image)
        out_awb = deep_wb(pil_img, task="awb", net_awb=net_awb, device=device, s=656)
        result_awb = utls.to_image(out_awb)

        orig_lin = to_linear(rgb_image)
        corr_lin = to_linear(result_awb)

        mean_orig = orig_lin.mean(axis=(0, 1))
        mean_corr = corr_lin.mean(axis=(0, 1))

        rgb_gain = mean_corr / (mean_orig + 1e-8)

        rgb_gain /= rgb_gain.mean()
        return rgb_gain.tolist()


    def set_gains(image, b,g,r):
        state.adjustment_values["b_gain"] = b
        state.adjustment_values["g_gain"] = g
        state.adjustment_values["r_gain"] = r
        return image

    def apply_auto():
        [r,g,b] = predict_gains()

        state.operations.append([set_gains, [], {"b": b, "g": g, "r": r}])
        state.redo_stack.clear()
        update_display_image(state)


    menu_bar.add_command(label="Auto white balance", command=apply_auto)
