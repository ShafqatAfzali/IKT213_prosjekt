import cv2

from .image_conversion import cv2_to_tk
from .cord_utils import full_image_cords_to_canvas_cords, clamp
from classes.state import State

def render_pipeline(state: State):
    last_cache_idx = max([idx for idx in state.cached_images if idx <= len(state.operations)-1],default=-1)

    if last_cache_idx >= 0:
        image = state.cached_images[last_cache_idx].copy()
        start_idx = last_cache_idx + 1
    else:
        image = state.original_image.copy()
        start_idx = 0

    for i in range(start_idx, len(state.operations)):
        func, args, kwargs = state.operations[i]
        image = func(image, *args, **kwargs)

        if (i+1) % 5 == 0:
            state.cached_images[i] = image.copy()

    if state.preview_brush_mask is not None:
        mask = state.preview_brush_mask
        color = state.brush_color
        for c in range(3):
            image[mask == 255, c] = color[::-1][c]

    if state.crop_metadata:
        cm = state.crop_metadata
        image = image[cm['y0']:cm['y1'], cm['x0']:cm['x1']]

    state.cv_image_full = image
    return image

def update_display_image(state: State):
    if state.cv_image_full is None:
        return

    image = render_pipeline(state)

    c_width, c_height = state.canvas.winfo_width(), state.canvas.winfo_height()
    h, w, _ = image.shape

    view_w = int(c_width / state.zoom)
    view_h = int(c_height / state.zoom)
    x0 = int(state.offset_x)
    y0 = int(state.offset_y)
    x1 = x0 + view_w
    y1 = y0 + view_h

    zoom_crop = image[y0:y1, x0:x1]

    display_w = int(zoom_crop.shape[1] * state.zoom)
    display_h = int(zoom_crop.shape[0] * state.zoom)
    resized_for_zoom = cv2.resize(zoom_crop, (display_w, display_h), interpolation=cv2.INTER_AREA)

    state.cv_image_display = resized_for_zoom
    state.tk_image = cv2_to_tk(resized_for_zoom)

    if hasattr(state, "background_image_id"):
        state.canvas.itemconfig(state.background_image_id, image=state.tk_image)
        state.canvas.coords(state.background_image_id, c_width // 2, c_height // 2)
    else:
        state.background_image_id = state.canvas.create_image(
            c_width // 2, c_height // 2, image=state.tk_image, anchor="center", tags="background_image"
        )
        state.canvas.tag_lower("background_image_id")


    if len(state.selection_points) >= 2 and state.selection_shape_ids:
        disp_cords = full_image_cords_to_canvas_cords(state, state.selection_points)
        disp_cords.append(disp_cords[0])

        for i, shape_id in enumerate(state.selection_shape_ids):
            state.canvas.coords(shape_id, disp_cords[i], disp_cords[i+1])