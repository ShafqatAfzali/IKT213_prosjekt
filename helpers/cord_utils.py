from classes.state import State

def get_full_to_display_image_scale(state: State):
    """Return scale factor from full image to displayed image."""
    h_full, w_full, _ = state.cv_image_full.shape
    h_display, w_display, _ = state.cv_image_display.shape
    scale = min(w_display / w_full,  h_display / h_full)
    return scale

def canvas_to_image_offset(state):
    """Return top-left offset of the image on the canvas."""
    c_w, c_h = state.canvas.winfo_width(), state.canvas.winfo_height()
    h, w = state.cv_image_display.shape[:2]
    w_offset, h_offset = (c_w - w) / 2, (c_h - h) / 2
    return w_offset, h_offset

def canvas_to_image_cords(state: State, cords: list):
    """Convert canvas coordinates to image coordinates, clamped inside image."""
    w_off, h_off = canvas_to_image_offset(state)
    h, w = state.cv_image_display.shape[:2]
    return [
        (
            max(0, min(int(x - w_off), w - 1)),
            max(0, min(int(y - h_off), h - 1))
        )
        for x, y in cords
    ]

def clamp_to_image(state, x, y):
    """Clamp a canvas coordinate to the visible image area."""
    w_off, h_off = canvas_to_image_offset(state)
    h, w = state.cv_image_display.shape[:2]
    clamped_x = max(w_off, min(x, w_off + w))
    clamped_y = max(h_off, min(y, h_off + h))
    return clamped_x, clamped_y

def display_image_cords_to_full_image(state, cords):
    """Convert display image coordinates to full image coordinates."""
    h_full, w_full, _ = state.cv_image_full.shape
    h_disp, w_disp, _ = state.cv_image_display.shape
    scale = w_full / w_disp
    return [(int(x * scale), int(y * scale)) for x, y in cords]

def full_image_cords_to_display_image(state: State, coords):
    """Convert full image coordinates to display image coordinates on canvas."""
    scale = get_full_to_display_image_scale(state)
    w_off, h_off = canvas_to_image_offset(state)
    return [(x * scale + w_off, y * scale + h_off) for x, y in coords]