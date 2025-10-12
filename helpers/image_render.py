import cv2
from .image_conversion import cv2_to_tk
from .cord_utils import full_image_cords_to_display_image
from classes.state import State

# TODO: Add cache_images to not go through every operation every time, will become slow
def render_pipeline(state: State):
    image = state.original_image.copy()
    for func, args, kwargs in state.operations:
        image = func(image, *args, **kwargs)

    if state.preview_mask is not None:
        mask = state.preview_mask
        color = state.brush_color
        for c in range(3):  # BGR channels
            image[mask == 255, c] = color[::-1][c]

    state.cv_image_full = image
    return image

def update_display_image(state: State):
    if state.cv_image_full is None:
        return

    c_width, c_height = state.canvas.winfo_width(), state.canvas.winfo_height()
    h, w, _ = state.cv_image_full.shape

    scale = min(c_width / w, c_height / h)
    new_w, new_h = int(w * scale), int(h * scale)

    state.cv_image_display = render_pipeline(state)
    state.cv_image_display = cv2.resize(state.cv_image_display, (new_w, new_h), interpolation=cv2.INTER_AREA)
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
        disp_cords = full_image_cords_to_display_image(state, state.selection_points)
        disp_cords.append(disp_cords[0])

        for i, shape_id in enumerate(state.selection_shape_ids):
            state.canvas.coords(shape_id, disp_cords[i], disp_cords[i+1])