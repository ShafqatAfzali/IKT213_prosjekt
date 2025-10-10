import cv2
from PIL import Image, ImageTk

from classes.state import State


def cv2_to_tk(cv_img):
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cv_img_rgb)
    return ImageTk.PhotoImage(pil_img)

def update_display_image(state: State):
    if state.cv_image_full is None:
        return

    c_width, c_height = state.canvas.winfo_width(), state.canvas.winfo_height()
    h, w, _ = state.cv_image_full.shape

    scale = min(c_width / w, c_height / h)
    new_w, new_h = int(w * scale), int(h * scale)

    state.cv_image_display = cv2.resize(state.cv_image_full, (new_w, new_h), interpolation=cv2.INTER_AREA)

    state.tk_image = cv2_to_tk(state.cv_image_display)

    if hasattr(state, "background_image_id"):
        state.canvas.itemconfig(state.background_image_id, image=state.tk_image)
        state.canvas.coords(state.background_image_id, c_width // 2, c_height // 2)
    else:
        state.background_image_id = state.canvas.create_image(
            c_width // 2, c_height // 2, image=state.tk_image, anchor="center", tags="background_image"
        )
        state.canvas.tag_lower("background_image_id")


    if len(state.selection_points) >= 2 and state.selection_shape_ids:
        disp_cords = full_image_cords_to_display(state, state.selection_points)
        disp_cords.append(disp_cords[0])

        for i, shape_id in enumerate(state.selection_shape_ids):
            state.canvas.coords(shape_id, disp_cords[i], disp_cords[i+1])

def get_display_scale(state: State):
    h_full, w_full, _ = state.cv_image_full.shape
    h_display, w_display, _ = state.cv_image_display.shape

    scale = min(w_display / w_full,  h_display / h_full)
    return scale

def canvas_to_image_cords(state: State, cords):
    c_width = state.canvas.winfo_width()
    c_height = state.canvas.winfo_height()
    h, w = state.cv_image_display.shape[:2]

    x0 = (c_width - w) / 2
    y0 = (c_height - h) / 2

    result = []
    for x, y in cords:
        img_x = x - x0
        img_y = y - y0
        img_x = max(0, min(img_x, w - 1))
        img_y = max(0, min(img_y, h - 1))
        result.append((int(img_x), int(img_y)))
    return result

def clamp_to_image(state, x, y):
    c_width, c_height = state.canvas.winfo_width(), state.canvas.winfo_height()
    h, w = state.cv_image_display.shape[:2]

    x0 = (c_width - w) / 2
    y0 = (c_height - h) / 2
    x1 = x0 + w
    y1 = y0 + h

    clamped_x = max(x0, min(x, x1))
    clamped_y = max(y0, min(y, y1))

    return clamped_x, clamped_y

def canvas_to_image_offset(state):
    c_width, c_height = state.canvas.winfo_width(), state.canvas.winfo_height()
    h, w = state.cv_image_display.shape[:2]
    w_offset = (c_width - w) / 2
    h_offset = (c_height - h) / 2

    return w_offset, h_offset

def scale_to_full_image_cords(state, cords):
    h_full, w_full, _ = state.cv_image_full.shape
    h_display, w_display, _ = state.cv_image_display.shape

    scale = w_full / w_display

    scaled_cords = []

    for x,y in cords:
        new_x = int(x * scale)
        new_y = int(y * scale)
        points = (new_x, new_y)
        scaled_cords.append(points)

    return scaled_cords

def full_image_cords_to_display(state: State, coords):
    display_cords = []
    scale = get_display_scale(state)
    w_offset, h_offset = canvas_to_image_offset(state)

    for x,y in coords:
        x_disp = x * scale + w_offset
        y_disp = y * scale + h_offset
        display_cords.append((x_disp,y_disp))

    return display_cords