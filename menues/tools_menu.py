import tkinter as tk
from tkinter import colorchooser, simpledialog
import cv2

from classes.state import State
from other.helper_functions import update_display_image, cv2_to_tk, canvas_to_image_cords, scale_up_cords

# Brush state
brush_active = False
brush_color = (255, 0, 0)  # default red
brush_size = 5


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

    def erase():
        if state.cv_image_full is not None:
            state.cv_image_full = None
            state.current_image_tk = None
            state.current_file_path = None
            state.canvas.delete("all")

    def pick_color():
        global brush_color
        color = colorchooser.askcolor()[0]  # (R,G,B)
        if color:
            brush_color = tuple(map(int, color))
            print("Brush color picked:", brush_color)

    def start_brush():
        global brush_active
        brush_active = True
        if state.canvas is not None:
            state.canvas.bind("<B1-Motion>", draw_brush)  # mouse drag
            state.canvas.bind("<ButtonRelease-1>", stop_brush)
        print("Brush mode ON")

    def draw_brush(event):
        global brush_color, brush_size
        if state.cv_image_full is not None:
            image_cords = canvas_to_image_cords(state, [(event.x, event.y)])
            scaled_image_cords = scale_up_cords(state, image_cords)
            (x, y) = scaled_image_cords[0]

            cv2.circle(state.cv_image_full, (x,y), brush_size, brush_color[::-1], -1)
            update_display_image(state)

    def stop_brush(event):
        global brush_active
        brush_active = False
        if state.canvas is not None:
            state.canvas.unbind("<B1-Motion>")
        print("Brush mode OFF")

    def set_brush_size(size):
        global brush_size
        brush_size = size
        print("Brush size set to", size)

    def add_text():
        if state.cv_image_full is not None:
            text = simpledialog.askstring("Input", "Enter text:")
            if text:
                cv2.putText(state.cv_image_full, text, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                update_display_image(state)

    # === Filters ===
    def gaussian_filter():
        if state.cv_image_full is not None:
            state.cv_image_full = cv2.GaussianBlur(state.cv_image_full, (5, 5), 0)
            update_display_image(state)

    def sobel_filter():
        if state.cv_image_full is not None:
            gray = cv2.cvtColor(state.cv_image_full, cv2.COLOR_BGR2GRAY)
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
            sobel = cv2.magnitude(sobelx, sobely)
            sobel = cv2.convertScaleAbs(sobel)
            state.cv_image_full = cv2.cvtColor(sobel, cv2.COLOR_GRAY2RGB)
            update_display_image(state)

    def binary_filter():
        if state.cv_image_full is not None:
            gray = cv2.cvtColor(state.cv_image_full, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
            state.cv_image_full = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
            update_display_image(state)

    def histogram_threshold():
        if state.cv_image_full is not None:
            gray = cv2.cvtColor(state.cv_image_full, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(
                gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            state.cv_image_full = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
            update_display_image(state)

    tools_menu = tk.Menu(menu_bar, tearoff=0)
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
    menu_bar.add_cascade(label="Tools", menu=tools_menu)