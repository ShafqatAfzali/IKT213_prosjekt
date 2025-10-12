import tkinter as tk
from tkinter import colorchooser, simpledialog
import cv2
import numpy as np

from classes.state import State
from helpers.image_render import update_display_image
from helpers.image_conversion import cv2_to_tk
from helpers.cord_utils import canvas_to_image_cords, display_image_cords_to_full_image

# Brush state
brush_active = False


def create_tools_menu(state: State, menu_bar):
    # TODO: Find way to work with update_display_image auto resize and preferably move around the image
    def zoom_in():
        if state.cv_image_full is not None:
            state.cv_image_full = cv2.pyrUp(state.cv_image_full)
            state.tk_image = cv2_to_tk(state.cv_image_full)
            state.canvas.delete("all")
            c_width, c_height = state.canvas.winfo_width(), state.canvas.winfo_height()
            state.canvas.create_image(c_width // 2, c_height // 2, image=state.tk_image, anchor="center")

    def zoom_out():
        if state.cv_image_full is not None:
            state.cv_image_full = cv2.pyrDown(state.cv_image_full)
            state.tk_image = cv2_to_tk(state.cv_image_display)
            state.canvas.delete("all")
            c_width, c_height = state.canvas.winfo_width(), state.canvas.winfo_height()
            state.canvas.create_image(c_width // 2, c_height // 2, image=state.tk_image, anchor="center")

    # TODO: Change to remove brush lines instead of whole canvas?
    def erase():
        if state.cv_image_full is not None:
            state.cv_image_full = None
            state.current_image_tk = None
            state.current_file_path = None
            state.canvas.delete("all")

    def pick_color():
        color = colorchooser.askcolor()[0]  # (R,G,B)
        if color:
            state.brush_color = tuple(map(int, color))
            print("Brush color picked:", state.brush_color)

    # TOD: How to turn off after use
    counter = None

    def start_brush():
        global brush_active, counter
        state.preview_mask = np.zeros_like(state.cv_image_full[:, :, 0], dtype=np.uint8)
        brush_active = True

        if state.canvas is not None:
            state.canvas.bind("<B1-Motion>", draw_brush)  # mouse drag
            state.canvas.bind("<ButtonRelease-1>", stop_brush)
        print("Brush mode ON")
        counter = 0


    def draw_brush(event):
        global counter
        if state.cv_image_full is None:
            return

        image_cords = canvas_to_image_cords(state, [(event.x, event.y)])
        scaled_image_cords = display_image_cords_to_full_image(state, image_cords)
        (x, y) = scaled_image_cords[0]

        cv2.circle(state.preview_mask, (x, y), state.brush_size, 255, -1)

        update_display_image(state)

    def stop_brush(event):
        global brush_active
        brush_active = False
        if state.canvas is not None:
            state.canvas.unbind("<B1-Motion>")
        print("Brush mode OFF")


        # store single brush operation
        def apply_brush(image, mask=None, color=None):
            result = image.copy()
            if mask is not None and color is not None:
                for c in range(3):  # BGR channels
                    result[mask == 255, c] = color[::-1][c]
            return result

        state.operations.append((apply_brush, [], {"mask": state.preview_mask.copy(), "color": state.brush_color}))
        state.preview_mask = None
        update_display_image(state)


    def set_size(size):
        state.brush_size = size
        print("Brush size set to", size)

    # TODO: Place text at specific location?
    def add_text():
        if state.cv_image_full is None:
            return
        text = simpledialog.askstring("Input", "Enter text:")
        if not text:
            return

        def draw_text(image, text):
            result = image.copy()
            cv2.putText(result, text, (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return result

        state.operations.append((draw_text, [], {"text": text}))
        update_display_image(state)

    # === Filters ===
    def apply_filter(func):
        state.operations.append((func, [], {"selection_mask": state.selection_mask}))
        update_display_image(state)

    def gaussian_filter(image, selection_mask = None):
        if image is None:
            return image

        gaussian_blur = cv2.GaussianBlur(image, (5, 5), 0)

        if selection_mask is not None:
            image[selection_mask == 255] = gaussian_blur[selection_mask == 255]
        else:
            image = gaussian_blur
        return image

    def sobel_filter(image, selection_mask = None):
        if image is None:
            return image

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        sobel = cv2.magnitude(sobelx, sobely)
        sobel = cv2.convertScaleAbs(sobel)
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
        binary_rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)

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

    tools_menu = tk.Menu(menu_bar, tearoff=0)
    tools_menu.add_command(label="Zoom In", command=zoom_in)
    tools_menu.add_command(label="Zoom Out", command=zoom_out)
    tools_menu.add_command(label="Erase", command=erase)
    tools_menu.add_command(label="Color Picker", command=pick_color)
    tools_menu.add_command(label="Paint Brush", command=start_brush)
    tools_menu.add_command(label="Text Box", command=add_text)
    tools_menu.add_separator()
    tools_menu.add_command(label="Gaussian Filter", command=lambda: apply_filter(gaussian_filter))
    tools_menu.add_command(label="Sobel Filter", command=lambda: apply_filter(sobel_filter))
    tools_menu.add_command(label="Binary Filter", command=lambda: apply_filter(binary_filter))
    tools_menu.add_command(label="Histogram Threshold", command=lambda: apply_filter(histogram_threshold))
    tools_menu.add_separator()
    #tools_menu.add_command(label="Choose Brush Color", command=pick_color)
    #tools_menu.add_command(label="Brush Size 5", command=lambda: set_size(5))
    #tools_menu.add_command(label="Brush Size 10", command=lambda: set_size(10))
    menu_bar.add_cascade(label="Tools", menu=tools_menu)