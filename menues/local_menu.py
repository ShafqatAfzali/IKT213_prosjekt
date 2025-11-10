from tkinter import Menu
from PIL import Image, ImageDraw
import cv2
import numpy as np
from helpers.image_render import update_display_image


def canvas_to_image_coords(state, x, y):
    """Convert canvas coordinates to full image coordinates based on zoom and offsets."""

    # Get zoom and offsets
    zoom = state.zoom
    offset_x = state.zoom_offset_x
    offset_y = state.zoom_offset_y

    # Get canvas size
    c_width = state.canvas.winfo_width()
    c_height = state.canvas.winfo_height()

    # Translate canvas coordinate to image space
    img_x = int(x / zoom + offset_x)
    img_y = int(y / zoom + offset_y)

    return img_x, img_y


# ----- Hjelpefunksjon: Canvas → Bildekoordinater ------
def canvas_to_image(x_canvas: int, y_canvas: int, state):
    """
    Konverterer musekoordinater fra canvas til koordinater i cv_image_full.
    Tar hensyn til at bildet er sentrert (anchor='center') og zoom.
    """
    if state.cv_image_full is None:
        return 0, 0

    h_img, w_img = state.cv_image_full.shape[:2]
    c_w, c_h = state.canvas.winfo_width(), state.canvas.winfo_height()

    # Beregn hvor bildet starter (fordi det er sentrert)
    display_w, display_h = int(w_img * state.zoom), int(h_img * state.zoom)
    img_x0 = (c_w - display_w) // 2
    img_y0 = (c_h - display_h) // 2

    # Juster musekoordinater til bildekoordinater
    x_img = (x_canvas - img_x0) / max(state.zoom, 1e-6)
    y_img = (y_canvas - img_y0) / max(state.zoom, 1e-6)

    # Begrens til bildet
    x_img = int(np.clip(x_img, 0, w_img - 1))
    y_img = int(np.clip(y_img, 0, h_img - 1))
    return x_img, y_img


# ----- Opprett Local-meny -----
def create_local_menu(state, menu_bar):
    local_menu = Menu(menu_bar, tearoff=0)
    local_menu.add_command(label="Brush", command=lambda: activate_local_tool(state, "brush"))
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

    if tool_name == "brush":
        c.bind("<B1-Motion>", lambda e: draw_brush(e, state))

    elif tool_name == "gradient":
        c.bind("<Button-1>", lambda e: start_gradient(e, state))
        c.bind("<B1-Motion>", lambda e: preview_gradient(e, state))
        c.bind("<ButtonRelease-1>", lambda e: apply_gradient(e, state))

    elif tool_name == "radial":
        c.bind("<Button-1>", lambda e: start_radial(e, state))
        c.bind("<ButtonRelease-1>", lambda e: apply_radial(e, state))


# ---- Brush -----
def draw_brush(event, state):
    if state.cv_image_full is None:
        print("No image loaded!")
        return

    # Convert from canvas → full image coordinates
    x, y = canvas_to_image_coords(state, event.x, event.y)
    brush_size = state.brush_size
    color = state.brush_color  # (r, g, b)

    # Convert to PIL Image
    if isinstance(state.cv_image_full, np.ndarray):
        img = Image.fromarray(cv2.cvtColor(state.cv_image_full, cv2.COLOR_BGR2RGB))
    else:
        img = state.cv_image_full

    draw = ImageDraw.Draw(img)
    draw.ellipse((x - brush_size, y - brush_size, x + brush_size, y + brush_size), fill=color)

    # Convert back to numpy (OpenCV format)
    state.cv_image_full = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    update_display_image(state)



# ---- Gradient -----
_gradient_start = None

def start_gradient(event, state):
    global _gradient_start
    _gradient_start = canvas_to_image(event.x, event.y, state)
    print("Gradient start:", _gradient_start)

def preview_gradient(event, state):
    pass  # kan brukes senere til forhåndsvisning

def apply_gradient(event, state):
    global _gradient_start
    if _gradient_start is None or state.cv_image_full is None:
        return

    x0, y0 = _gradient_start
    x1, y1 = canvas_to_image(event.x, event.y, state)

    img = state.cv_image_full.astype(np.float32)
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]

    dx, dy = x1 - x0, y1 - y0
    length2 = dx * dx + dy * dy
    if length2 == 0:
        _gradient_start = None
        return

    # Beregn gradient
    t = ((xx - x0) * dx + (yy - y0) * dy) / length2
    mask = np.clip(t, 0.0, 1.0).astype(np.float32)

    # Lysne mot sluttpunktet
    factor = 0.7 + 0.5 * mask[:, :, None]
    img = img * factor

    state.cv_image_full = np.clip(img, 0, 255).astype(np.uint8)
    state.active_tool = "gradient"
    update_display_image(state)

    print(f"Gradient applied from {x0, y0} to {x1, y1}")
    _gradient_start = None

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
    x0, y0 = canvas_to_image_coords(state, *_radial_start)
    x1, y1 = canvas_to_image_coords(state, event.x, event.y)
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
    state.cv_image_full = img
    update_display_image(state)

    _radial_start = None


