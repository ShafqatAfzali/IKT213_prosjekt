import tkinter as tk
from tkinter import colorchooser, simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np

# Globals
canvas = None
tk_image = None
current_image = None

# Brush state
brush_active = False
brush_color = (255, 0, 0)  # default red
brush_size = 5


def open_tools_menu(root, canvas_ref, image_ref):
    """
    Waxaa wacaya main.py si Tools menu loogu daro menubar
    """
    global canvas, current_image
    canvas = canvas_ref
    current_image = image_ref

    tools_menu = tk.Menu(root, tearoff=0)
    tools_menu.add_command(label="Zoom In", command=zoom_in)
    tools_menu.add_command(label="Zoom Out", command=zoom_out)
    tools_menu.add_command(label="Erase", command=erase)
    tools_menu.add_command(label="Color Picker", command=pick_color)
    tools_menu.add_command(label="Paint Brush", command=start_brush)
    tools_menu.add_command(label="Text Box", command=add_text)
    tools_menu.add_separator()
    tools_menu.add_command(label="Gaussian Filter", command=gaussian_filter)
    tools_menu.add_command(label="Sobel Filter", command=sobel_filter)
    tools_menu.add_command(label="Binary Filter", command=binary_filter)
    tools_menu.add_command(label="Histogram Threshold", command=histogram_threshold)
    tools_menu.add_separator()
    tools_menu.add_command(label="Choose Brush Color", command=pick_color)
    tools_menu.add_command(label="Brush Size 5", command=lambda: set_brush_size(5))
    tools_menu.add_command(label="Brush Size 10", command=lambda: set_brush_size(10))
    return tools_menu


# Helper update
def update_canvas(img):
    global canvas, tk_image, current_image
    current_image = img
    tk_image = ImageTk.PhotoImage(img)
    canvas.config(image=tk_image)
    canvas.image = tk_image


# === Tools ===
def zoom_in():
    global current_image
    if current_image is not None:
        w, h = current_image.size
        new_img = current_image.resize((w * 2, h * 2))
        update_canvas(new_img)


def zoom_out():
    global current_image
    if current_image is not None:
        w, h = current_image.size
        new_img = current_image.resize((max(1, w // 2), max(1, h // 2)))
        update_canvas(new_img)


def erase():
    global current_image
    if current_image is not None:
        w, h = current_image.size
        white = Image.new("RGB", (w, h), (255, 255, 255))
        update_canvas(white)


def pick_color():
    global brush_color
    color = colorchooser.askcolor()[0]  # (R,G,B)
    if color:
        brush_color = tuple(map(int, color))
        print("Brush color picked:", brush_color)


def start_brush():
    global brush_active
    brush_active = True
    if canvas is not None:
        canvas.bind("<B1-Motion>", draw_brush)   # mouse drag
        canvas.bind("<ButtonRelease-1>", stop_brush)
    print("Brush mode ON")


def draw_brush(event):
    global current_image, brush_color, brush_size
    if current_image is not None:
        cv_img = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
        cv2.circle(cv_img, (event.x, event.y), brush_size, brush_color[::-1], -1)
        pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        update_canvas(pil_img)


def stop_brush(event):
    global brush_active
    brush_active = False
    if canvas is not None:
        canvas.unbind("<B1-Motion>")
    print("Brush mode OFF")


def set_brush_size(size):
    global brush_size
    brush_size = size
    print("Brush size set to", size)


def add_text():
    global current_image
    if current_image is not None:
        text = simpledialog.askstring("Input", "Enter text:")
        if text:
            cv_img = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
            cv2.putText(cv_img, text, (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
            update_canvas(pil_img)


# === Filters ===
def gaussian_filter():
    global current_image
    if current_image is not None:
        cv_img = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
        blurred = cv2.GaussianBlur(cv_img, (5, 5), 0)
        pil_img = Image.fromarray(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB))
        update_canvas(pil_img)


def sobel_filter():
    global current_image
    if current_image is not None:
        cv_img = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        sobel = cv2.magnitude(sobelx, sobely)
        sobel = cv2.convertScaleAbs(sobel)
        sobel_rgb = cv2.cvtColor(sobel, cv2.COLOR_GRAY2RGB)
        pil_img = Image.fromarray(sobel_rgb)
        update_canvas(pil_img)


def binary_filter():
    global current_image
    if current_image is not None:
        cv_img = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        binary_rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
        pil_img = Image.fromarray(binary_rgb)
        update_canvas(pil_img)


def histogram_threshold():
    global current_image
    if current_image is not None:
        cv_img = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        thresh_rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
        pil_img = Image.fromarray(thresh_rgb)
        update_canvas(pil_img)
