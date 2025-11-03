import tkinter as tk
from tkinter import colorchooser, simpledialog
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

    # Allow pan with Shift + Left Mouse (laptop users)
    def shift_pan(event):
        if event.state & 0x0001:  # Shift key
            do_pan(event)

    # -------------------- Eraser --------------------
    def start_eraser():
        state.brush_mode = "erase"
        if state.canvas is not None:
            state.canvas.bind("<B1-Motion>", erase_draw)
            state.canvas.bind("<ButtonRelease-1>", stop_erase)

    def erase_draw(event):
        if state.cv_image_full is None:
            return
        cords = canvas_to_full_image_cords(state, [(event.x, event.y)])
        (x, y) = cords[0]
        cv2.circle(state.cv_image_full, (x, y), state.brush_size, (255, 255, 255), -1)
        update_display_image(state)

    def stop_erase(event):
        if state.canvas is not None:
            state.canvas.unbind("<B1-Motion>")
        update_display_image(state)

    # -------------------- Eyedropper Color Picker --------------------
    def pick_color_eyedropper(event=None):
        if state.cv_image_full is None:
            return
        state.canvas.bind("<Button-1>", eyedrop_click)

    def eyedrop_click(event):
        cords = canvas_to_full_image_cords(state, [(event.x, event.y)])
        (x, y) = cords[0]
        color = state.cv_image_full[y, x].tolist()  # BGR
        state.brush_color = tuple(color[::-1])  # convert to RGB
        print("Picked color:", state.brush_color)
        state.canvas.unbind("<Button-1>")

    # -------------------- Paint Brush with Patterns --------------------
    def start_brush(pattern="solid"):
        global brush_active
        brush_active = True
        state.brush_pattern = pattern
        state.canvas.bind("<B1-Motion>", draw_brush)
        state.canvas.bind("<ButtonRelease-1>", stop_brush)
        print("Brush pattern:", pattern)

    def draw_brush(event):
        if state.cv_image_full is None:
            return

        cords = canvas_to_full_image_cords(state, [(event.x, event.y)])
        (x, y) = cords[0]

        color = state.brush_color[::-1]  # to BGR
        if state.brush_pattern == "dotted":
            if (x + y) % 10 < 5:
                cv2.circle(state.cv_image_full, (x, y), state.brush_size, color, -1)
        elif state.brush_pattern == "striped":
            if x % 10 < 5:
                cv2.circle(state.cv_image_full, (x, y), state.brush_size, color, -1)
        else:
            cv2.circle(state.cv_image_full, (x, y), state.brush_size, color, -1)

        update_display_image(state)

    def stop_brush(event):
        global brush_active
        brush_active = False
        state.canvas.unbind("<B1-Motion>")
        update_display_image(state)

    # -------------------- Text Tool --------------------
    def enable_text_mode():
        global text_mode_active
        text_mode_active = True
        state.canvas.bind("<Button-1>", place_text_click)
        print("Click anywhere to place text...")

    def place_text_click(event):
        global text_mode_active
        if not text_mode_active:
            return
        text = simpledialog.askstring("Add Text", "Enter text:")
        if not text:
            return

        cords = canvas_to_full_image_cords(state, [(event.x, event.y)])
        (x, y) = cords[0]
        cv2.putText(state.cv_image_full, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, state.brush_color[::-1], 2)
        update_display_image(state)
        text_mode_active = False
        state.canvas.unbind("<Button-1>")

    # -------------------- Filters --------------------
    def apply_filter(func):
        state.operations.append((func, [], {"selection_mask": state.selection_mask}))
        update_display_image(state)

    def gaussian_filter(img, selection_mask=None):
        if img is None:
            return img
        blur = cv2.GaussianBlur(img, (5, 5), 0)
        return blur

    def sobel_filter(img, selection_mask=None):
        if img is None:
            return img
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        sobel = cv2.convertScaleAbs(cv2.magnitude(sobelx, sobely))
        return cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)

    def binary_filter(img, selection_mask=None):
        if img is None:
            return img
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    def histogram_threshold(img, selection_mask=None):
        if img is None:
            return img
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    # -------------------- Menu Setup --------------------
    tools_menu = tk.Menu(menu_bar, tearoff=0)
    tools_menu.add_command(label="Zoom In", command=lambda: zoom(0.25))
    tools_menu.add_command(label="Zoom Out", command=lambda: zoom(-0.25))
    tools_menu.add_command(label="Eraser", command=start_eraser)
    tools_menu.add_command(label="Eyedropper", command=pick_color_eyedropper)
    tools_menu.add_command(label="Brush (Solid)", command=lambda: start_brush("solid"))
    tools_menu.add_command(label="Brush (Dotted)", command=lambda: start_brush("dotted"))
    tools_menu.add_command(label="Brush (Striped)", command=lambda: start_brush("striped"))
    tools_menu.add_command(label="Text Tool", command=enable_text_mode)

    filters_menu = tk.Menu(menu_bar, tearoff=0)
    filters_menu.add_command(label="Gaussian Filter", command=lambda: apply_filter(gaussian_filter))
    filters_menu.add_command(label="Sobel Filter", command=lambda: apply_filter(sobel_filter))
    filters_menu.add_command(label="Binary Filter", command=lambda: apply_filter(binary_filter))
    filters_menu.add_command(label="Histogram Threshold", command=lambda: apply_filter(histogram_threshold))

    tools_menu.add_cascade(label="Filters", menu=filters_menu)
    menu_bar.add_cascade(label="Tools", menu=tools_menu)

    # Bindings
    state.canvas.bind("<MouseWheel>", lambda e: zoom(step=0.25 if e.delta > 0 else -0.25, event=e))
    state.canvas.bind("<ButtonPress-2>", start_pan)
    state.canvas.bind("<B2-Motion>", do_pan)
    state.canvas.bind("<B1-Motion>", shift_pan)
