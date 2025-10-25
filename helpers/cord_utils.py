from classes.state import State

def canvas_to_image_offset(state):
    """
    Return top-left offset of the image on the canvas.\n
    :returns: w_offset, h_offset
    """
    c_w, c_h = state.canvas.winfo_width(), state.canvas.winfo_height()
    h, w = state.cv_image_display.shape[:2]
    w_offset, h_offset = (c_w - w) / 2, (c_h - h) / 2
    return w_offset, h_offset

def clamp(v, lo, hi):
    """
    :param v:
    :param lo:
    :param hi:
    :return: max(lo, min(v, hi))
    """
    return max(lo, min(v, hi))

def clamp_to_image(state, x, y):
    """Clamp a canvas coordinate to the visible image area."""
    w_off, h_off = canvas_to_image_offset(state)
    h, w = state.cv_image_display.shape[:2]
    clamped_x = clamp(x, w_off, (w_off + w))
    clamped_y = clamp(y, h_off, (h_off + h))
    return clamped_x, clamped_y

def canvas_to_full_image_cords(state: State, cords: list, cropping=False):
    """Convert canvas coordinates to full-image coordinates, clamped inside image."""
    zoom = state.zoom
    x_off, y_off = state.offset_x, state.offset_y
    pad_x, pad_y = canvas_to_image_offset(state)

    if not cropping and state.crop_metadata:
        crop = state.crop_metadata
        crop_x0, crop_y0, crop_x1, crop_y1 = crop['x0'], crop['y0'], crop['x1'], crop['y1']
    else:
        crop_x0 = crop_y0 = 0
        h, w, _ = state.cv_image_full.shape
        crop_x1, crop_y1 = w, h

    img_cords = []
    for x, y in cords:
        # subtract padding to get coordinates relative to displayed image
        rel_x = x - pad_x
        rel_y = y - pad_y

        # convert to full image coords using zoom and pan
        img_x = (x_off + rel_x / zoom) + crop_x0
        img_y = (y_off + rel_y / zoom) + crop_y0

        # clamp inside image
        img_x = int(clamp(img_x, 0, crop_x1))
        img_y = int(clamp(img_y, 0, crop_y1))
        img_cords.append((img_x, img_y))

    return img_cords

def full_image_cords_to_canvas_cords(state: State, cords, cropping=False):
    """
    Convert full image coordinates to canvas coordinates.

    """
    w_off, h_off = canvas_to_image_offset(state)
    img_x_off, img_y_off = state.offset_x, state.offset_y  # zoom/pan offsets

    if not cropping and state.crop_metadata:
        crop = state.crop_metadata
        crop_x0, crop_y0 = crop['x0'], crop['y0']
    else:
        crop_x0 = crop_y0 = 0

    canvas_cords = []
    for x, y in cords:
        # remove zoom/pan offset, then scale
        disp_x = (x - crop_x0 - img_x_off) * state.zoom
        disp_y = (y - crop_y0 - img_y_off) * state.zoom

        # add canvas padding
        canvas_cords.append((disp_x + w_off, disp_y + h_off))

    return canvas_cords