import tkinter as tk
from tkinter import simpledialog
import cv2
import numpy as np

from classes.state import State
from helpers.image_render import update_display_image
from helpers.cord_utils import canvas_to_full_image_cords, clamp

brush_active = False
text_mode_active = False


def create_tools_menu(state: State, menu_bar):

    # -------------------- Zoom & Pan --------------------
    def zoom(step: float = 0.25, event=None):
        if state.cv_image_full is None:
            return

        old_zoom = state.zoom
        new_zoom = clamp(old_zoom + step, state.min_zoom, state.max_zoom)
        if new_zoom == old_zoom:
            return

        c_w, c_h = state.canvas.winfo_width(), state.canvas.winfo_height()
        nx, ny = (event.x / c_w, event.y / c_h) if event else (0.5, 0.5)

        view_w_old, view_h_old = c_w / old_zoom, c_h / old_zoom
        img_x = state.zoom_offset_x + nx * view_w_old
        img_y = state.zoom_offset_y + ny * view_h_old

        view_w_new, view_h_new = c_w / new_zoom, c_h / new_zoom
        state.zoom_offset_x = img_x - nx * view_w_new
        state.zoom_offset_y = img_y - ny * view_h_new

        h, w, _ = state.cv_image_full.shape
        state.zoom_offset_x = clamp(state.zoom_offset_x, 0, max(0, w - view_w_new))
        state.zoom_offset_y = clamp(state.zoom_offset_y, 0, max(0, h - view_h_new))

        state.zoom = new_zoom
        update_display_image(state)

    def start_pan(event):
        state.pan_start = (event.x, event.y)

    def do_pan(event):
        dx = (event.x - state.pan_start[0]) / state.zoom
        dy = (event.y - state.pan_start[1]) / state.zoom
        state.zoom_offset_x -= int(dx)
        state.zoom_offset_y -= int(dy)

        h, w, _ = state.cv_image_full.shape
        c_width, c_height = state.canvas.winfo_width(), state.canvas.winfo_height()
        view_w, view_h = int(c_width / state.zoom), int(c_height / state.zoom)

        state.zoom_offset_x = clamp(state.zoom_offset_x, 0, max(0, w - view_w))
        state.zoom_offset_y = clamp(state.zoom_offset_y, 0, max(0, h - view_h))

        state.pan_start = (event.x, event.y)
        update_display_image(state)

    # -------------------- Eyedropper Tool --------------------
    def pick_color_eyedropper():
        if state.cv_image_full is None:
            return
        print("Click anywhere to pick a color...")
        state.canvas.bind("<Button-1>", eyedrop_click)

    def eyedrop_click(event):
        cords = canvas_to_full_image_cords(state, [(event.x, event.y)])
        (x, y) = cords[0]
        color = state.cv_image_full[y, x].tolist()
        state.brush_color = tuple(color[::-1])  # BGR -> RGB
        print("Picked color:", state.brush_color)
        state.canvas.unbind("<Button-1>")

    # -------------------- Eraser --------------------
    def start_eraser():
        global brush_active
        brush_active = True
        state.brush_mode = "erase"
        state.canvas.bind("<B1-Motion>", erase_draw)
        state.canvas.bind("<ButtonRelease-1>", stop_erase)

    def erase_draw(event):
        if state.cv_image_full is None:
            return

        [(x,y)] = canvas_to_full_image_cords(state, [(event.x, event.y)])

        def apply_erase(image):
            result = image.copy()
            cv2.circle(result, (x, y), state.brush_size, (255, 255, 255), -1)
            return result

        state.operations.append((apply_erase, [], {}))
        update_display_image(state)

    def stop_erase(event):
        state.canvas.unbind("<B1-Motion>")
        update_display_image(state)

    # -------------------- Paint Brush --------------------
    def activate_brush(pattern: str):
        state.canvas.bind("<Button-1>", lambda p=pattern: start_brush(pattern))
        state.canvas.bind("<B1-Motion>", draw_brush)
        state.canvas.bind("<ButtonRelease-1>", brush_released)
        state.canvas.bind("<Button-3>", stop_brush)

    def start_brush(pattern="solid"):
        global brush_active
        brush_active = True

        state.preview_brush_mask = np.zeros((*state.cv_image_full.shape[:2], 4), dtype=np.uint8)
        state.preview_brush_mask[..., 3] = 0
        print("Brush pattern:", pattern)

    def draw_brush(event):
        if state.cv_image_full is None:
            return

        image_cords = canvas_to_full_image_cords(state, [(event.x, event.y)])
        (x, y) = image_cords[0]
        color_bgr = state.brush_color[::-1]

        if state.brush_pattern == "dotted":
            if (x + y) % 10 < 5:
                cv2.circle(state.preview_brush_mask, (x, y), state.brush_size, (*color_bgr, 255), -1)
        elif state.brush_pattern == "striped":
            if x % 10 < 5:
                cv2.circle(state.preview_brush_mask, (x, y), state.brush_size, (*color_bgr, 255), -1)
        else:
            cv2.circle(state.preview_brush_mask, (x, y), state.brush_size, (*color_bgr, 255), -1)

        update_display_image(state)

    def brush_released(event):
        def apply_brush(image, mask):
            alpha_mask = mask[..., 3] > 0
            image[alpha_mask] = mask[..., :3][alpha_mask]
            return image
        state.operations.append((apply_brush, [], {"mask": state.preview_brush_mask.copy()}))
        state.preview_brush_mask = None
        state.redo_stack.clear()
        update_display_image(state)


    def stop_brush(event):
        global brush_active
        brush_active = False
        state.canvas.unbind("<Button-1>")
        state.canvas.unbind("<B1-Motion>")
        state.canvas.unbind("<ButtonRelease-1>")
        state.canvas.unbind("<Button-3>")
        update_display_image(state)

    # -------------------- Text Placement --------------------
    def enable_text_mode():
        global text_mode_active
        text_mode_active = True
        state.canvas.bind("<Button-1>", place_text_click)
        print("Click to place text...")

    def place_text_click(event):
        global text_mode_active
        if not text_mode_active:
            return

        text = simpledialog.askstring("Add Text", "Enter text:")
        if not text:
            return

        cords = canvas_to_full_image_cords(state, [(event.x, event.y)])
        (x, y) = cords[0]

        def apply_text(image):
            result = image.copy()
            cv2.putText(result, text, (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, state.brush_color[::-1], 2)
            return result

        state.operations.append((apply_text, [], {}))
        update_display_image(state)
        text_mode_active = False
        state.canvas.unbind("<Button-1>")

    # -------------------- Filters --------------------
    def apply_filter(func):
        state.operations.append((func, [], {"selection_mask": state.selection_mask}))
        state.redo_stack.clear()
        update_display_image(state)

    def gaussian_filter(image, selection_mask=None):
        if image is None:
            return image
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        if selection_mask is not None:
            image[selection_mask == 255] = blurred[selection_mask == 255]
        else:
            image = blurred
        return image

    def sobel_filter(image, selection_mask=None):
        if image is None:
            return image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        sobel = cv2.convertScaleAbs(cv2.magnitude(sobelx, sobely))
        sobel_rgb = cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)
        if selection_mask is not None:
            image[selection_mask == 255] = sobel_rgb[selection_mask == 255]
        else:
            image = sobel_rgb
        return image

    def binary_filter(image, selection_mask=None):
        if image is None:
            return image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        binary_rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        if selection_mask is not None:
            image[selection_mask == 255] = binary_rgb[selection_mask == 255]
        else:
            image = binary_rgb
        return image

    def histogram_threshold(image, selection_mask=None):
        if image is None:
            return image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh_rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        if selection_mask is not None:
            image[selection_mask == 255] = thresh_rgb[selection_mask == 255]
        else:
            image = thresh_rgb
        return image

    def median_filter(image, selection_mask=None):
        if image is None:
            return image
        blurred = cv2.medianBlur(image, 5)
        if selection_mask is not None:
            image[selection_mask == 255] = blurred[selection_mask == 255]
        else:
            image = blurred
        return image

    def guided_filter(image, selection_mask=None):
        if image is None:
            return image
        img_float = image.astype(np.float32) / 255.0
        guided = cv2.ximgproc.guidedFilter(img_float, img_float, radius=8, eps=0.04)
        guided = (guided * 255).astype(np.uint8)
        if selection_mask is not None:
            image[selection_mask == 255] = guided[selection_mask == 255]
        else:
            image = guided
        return image

    def sharpen(image, selection_mask=None):
        if image is None:
            return image
        strength = 1.5
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        sharpened = cv2.addWeighted(image, strength, blurred, -0.5 * strength, 0)
        if selection_mask is not None:
            image[selection_mask == 255] = sharpened[selection_mask == 255]
        else:
            image = sharpened
        return image

    # -------------------- Menu Setup --------------------
    tools_menu = tk.Menu(menu_bar, tearoff=0)
    tools_menu.add_command(label="Zoom In", command=lambda: zoom(0.25))
    tools_menu.add_command(label="Zoom Out", command=lambda: zoom(-0.25))
    tools_menu.add_command(label="Eraser", command=start_eraser)
    tools_menu.add_command(label="Eyedropper", command=pick_color_eyedropper)
    tools_menu.add_command(label="Brush (Solid)", command=lambda: activate_brush("solid"))
    tools_menu.add_command(label="Brush (Dotted)", command=lambda: activate_brush("dotted"))
    tools_menu.add_command(label="Brush (Striped)", command=lambda: activate_brush("striped"))
    tools_menu.add_command(label="Text Tool", command=enable_text_mode)

    filters_menu = tk.Menu(menu_bar, tearoff=0)
    filters_menu.add_command(label="Gaussian Filter", command=lambda: apply_filter(gaussian_filter))
    filters_menu.add_command(label="Sobel Filter", command=lambda: apply_filter(sobel_filter))
    filters_menu.add_command(label="Binary Filter", command=lambda: apply_filter(binary_filter))
    filters_menu.add_command(label="Histogram Threshold", command=lambda: apply_filter(histogram_threshold))
    filters_menu.add_command(label="Median Blur", command=lambda: apply_filter(median_filter))
    filters_menu.add_command(label="Guided Filter", command=lambda: apply_filter(guided_filter))
    filters_menu.add_command(label="Sharpen", command=lambda: apply_filter(sharpen))

    tools_menu.add_cascade(label="Filters", menu=filters_menu)
    menu_bar.add_cascade(label="Tools", menu=tools_menu)

    # -------------------- Bindings --------------------
    state.canvas.bind("<MouseWheel>", lambda e: zoom(step=0.25 if e.delta > 0 else -0.25, event=e))
    state.canvas.bind("<ButtonPress-2>", start_pan)
    state.canvas.bind("<B2-Motion>", do_pan)
    state.canvas.bind("<Shift-ButtonPress-1>", start_pan)
    state.canvas.bind("<Shift-B1-Motion>", do_pan)
