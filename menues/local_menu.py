from tkinter import Menu
import numpy as np

from classes.state import State
from helpers.image_render import update_display_image
from helpers.cord_utils import canvas_to_full_image_cords


# ----- Opprett Local-meny -----
def create_local_menu(state, menu_bar):
    local_menu = Menu(menu_bar, tearoff=0)
    local_menu.add_command(label="Gradient", command=lambda: activate_local_tool(state, "gradient"))
    local_menu.add_command(label="Radial Filter", command=lambda: activate_local_tool(state, "radial"))
    menu_bar.add_cascade(label="Local", menu=local_menu)


# ----- Aktiver verktøy -----
def activate_local_tool(state, tool_name):
    print(f"Activated local tool: {tool_name}")
    state.active_tool = tool_name

    c = state.canvas
    c.unbind("<B1-Motion>")
    c.unbind("<Button-1>")
    c.unbind("<ButtonRelease-1>")

    if tool_name == "gradient":
        c.bind("<Button-1>", lambda e: start_gradient(e, state))
        c.bind("<ButtonRelease-1>", lambda e: get_gradient_mask(e, state))

    elif tool_name == "radial":
        c.bind("<Button-1>", lambda e: start_radial(e, state))
        c.bind("<ButtonRelease-1>", lambda e: apply_radial(e, state))

# ---- Gradient -----
_gradient_start = None

def start_gradient(event, state):
    global _gradient_start
    _gradient_start = canvas_to_full_image_cords(state, [(event.x, event.y)])

def get_gradient_mask(event, state):
    global _gradient_start
    if _gradient_start is None or state.cv_image_full is None:
        return

    [(x0, y0)] = _gradient_start
    [(x1, y1)] = canvas_to_full_image_cords(state, [(event.x, event.y)])

    h, w = state.cv_image_full.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]

    dx, dy = x1 - x0, y1 - y0
    length = dx * dx + dy * dy
    if length == 0:
        _gradient_start = None
        return

    # Beregn gradient
    t = ((xx - x0) * dx + (yy - y0) * dy) / length
    mask = np.clip(t, 0.0, 1.0).astype(np.float32)

    apply_gradient(state, mask)

    _gradient_start = None


def set_gradient(image, mask):
    image = image.astype(np.float32)
    factor = 0.7 + 0.5 * mask[:, :, None]
    image = image * factor

    image = np.clip(image, 0, 255).astype(np.uint8)
    return image

def apply_gradient(state: State, mask):
    state.operations.append([set_gradient, [mask], {}])
    state.redo_stack.clear()
    update_display_image(state)

# ---- Radial Filter ----
_radial_start = None

def start_radial(event, state):
    global _radial_start
    _radial_start = (event.x, event.y)
    print(f"Radial start: {_radial_start}")

def apply_radial(event, state):
    global _radial_start
    if _radial_start is None or state.cv_image_full is None:
        return

    # Convert both start and end from canvas → image coordinates
    [(x0, y0)] = canvas_to_full_image_cords(state, [_radial_start])
    [(x1, y1)] = canvas_to_full_image_cords(state, [(event.x, event.y)])
    radius = int(((x1 - x0)**2 + (y1 - y0)**2)**0.5)

    print(f"Radial filter applied at ({x0}, {y0}) with radius {radius}")

    # --- Convert to float for smoother brightness control ---
    img = state.cv_image_full.astype(np.float32) / 255.0
    h, w, _ = img.shape

    # Create a soft circular mask
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((X - x0)**2 + (Y - y0)**2)
    mask = np.clip(1 - (dist / radius), 0, 1)  # 1 = center, 0 = edge

    # Increase brightness within the circle (adjust 'strength' as needed)
    strength = 0.6
    img[:, :, 0] = np.clip(img[:, :, 0] + mask * strength, 0, 1)
    img[:, :, 1] = np.clip(img[:, :, 1] + mask * strength, 0, 1)
    img[:, :, 2] = np.clip(img[:, :, 2] + mask * strength, 0, 1)

    # Convert back to uint8 (for OpenCV compatibility)
    img = (img * 255).astype(np.uint8)

    # Update the image in the app window
    #state.cv_image_full = img
    update_display_image(state)

    _radial_start = None


