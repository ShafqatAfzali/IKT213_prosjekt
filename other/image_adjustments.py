import cv2
import numpy as np

from classes.state import State


def adjust_saturation(image, value):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= value
    hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def adjust_exposure(image, value):
    return np.clip(image.astype(np.float32) * value, 0, 255).astype(np.uint8)

def set_white_balance_temperature(image, temp):
    r_gain = 1.0 + (temp / 200)
    b_gain = 1.0 - (temp / 200)
    return adjust_white_balance(image, r_gain=r_gain, b_gain=b_gain)

def adjust_white_balance(image, r_gain=1.0, g_gain=1.0, b_gain=1.0):
    balanced = image.astype(np.float32)
    balanced[...,0] *= b_gain
    balanced[...,1] *= g_gain
    balanced[...,2] *= r_gain
    return np.clip(balanced, 0, 255).astype(np.uint8)

def adjustment(state: State, image):
    vals = state.preview_values if state.preview_adjust else state.adjustment_values

    if vals["contrast"] != 1.0 or vals["brightness"] != 0:
        image = cv2.convertScaleAbs(image, alpha=vals["contrast"], beta=vals["brightness"])

    image = adjust_saturation(image, vals["saturation"])
    image = adjust_exposure(image, vals["exposure"])
    image = set_white_balance_temperature(image, vals["white_balance"])

    return image