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

def apply_grayscale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_tone_curve(image, strength=0.3):
    if strength == 0:
        return image
    # Simple S-curve tone mapping
    lut = np.arange(256, dtype=np.float32)
    lut = 255 / (1 + np.exp(-strength * (lut - 128) / 32))
    lut = np.clip(lut, 0, 255).astype(np.uint8)
    return cv2.LUT(image, lut)

def apply_vignette(image, strength=0.0):
    if strength <= 0:
        return image
    rows, cols = image.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols * strength)
    kernel_y = cv2.getGaussianKernel(rows, rows * strength)
    mask = kernel_y * kernel_x.T
    mask = mask / mask.max()
    return np.clip(image * mask[..., None], 0, 255).astype(np.uint8)

def adjustment(state: State, image):
    vals = state.preview_values if state.preview_values is not None else state.adjustment_values

    if vals.get("contrast", 1.0) != 1.0 or vals.get("brightness", 0) != 0:
        image = cv2.convertScaleAbs(image, alpha=vals.get("contrast", 1.0), beta=vals.get("brightness", 0))

    image = adjust_saturation(image, vals.get("saturation", 1.0))
    image = adjust_exposure(image, vals.get("exposure", 1.0))
    image = set_white_balance_temperature(image, vals.get("white_balance", 0))

    if vals.get("grayscale", False):
        image = apply_grayscale(image)

    image = apply_tone_curve(image, vals.get("tone_curve_strength", 0.0))
    image = apply_vignette(image, vals.get("vignette_strength", 0.0))

    return image