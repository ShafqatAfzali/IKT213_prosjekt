from tkinter import Menu, simpledialog

import cv2
import numpy as np

from other.helper_functions import *
from other.image_rotation import *
from classes.state import State


def create_image_menu(state: State, menu_bar):
    def apply_image_operation(func):
        state.cv_image_full = func(state.cv_image_full)
        update_display_image(state)

    # TODO: Right-click to remove selection

    def reset_selection():
        for line_id in state.selection_shape_ids:
            state.canvas.delete(line_id)
        state.selection_points = []
        state.selection_shape_ids = []
        state.selection_mask = None

    def start_rectangle(event):
        reset_selection()
        state.selection_points.append(clamp_to_image(state, event.x, event.y))
        state.selection_points.append(state.selection_points[0])
        rect_id = state.canvas.create_rectangle(*state.selection_points[0], *state.selection_points[1],
                                                outline="red", width=2)
        state.selection_shape_ids.append(rect_id)
        state.canvas.bind("<B1-Motion>", update_rectangle)
        state.canvas.bind("<ButtonRelease-1>", finish_rectangle)

    def update_rectangle(event):
        state.selection_points[1] = clamp_to_image(state, event.x, event.y)
        state.canvas.coords(state.selection_shape_ids[0], *state.selection_points[0], *state.selection_points[1])

    def finish_rectangle(event):
        state.canvas.unbind("<B1-Motion>")
        state.canvas.unbind("<ButtonRelease-1>")
        image_cords = canvas_to_image_cords(state, state.selection_points)
        scaled_image_cords = scale_up_cords(state, image_cords)

        x1, y1 = scaled_image_cords[0]
        x2, y2 = scaled_image_cords[1]
        pts = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], np.int32)

        mask = np.zeros(state.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        state.selection_mask = mask

    # TODO: Combine lasso and poly
    def start_lasso(event):
        reset_selection()

        state.canvas.bind("<B1-Motion>", add_lasso_point)
        state.canvas.bind("<ButtonRelease-1>", finish_lasso)

    def add_lasso_point(event):
        x, y = clamp_to_image(state, event.x, event.y)
        state.selection_points.append((x, y))
        if len(state.selection_points) > 1:
            line_id = state.canvas.create_line(state.selection_points[-2], state.selection_points[-1], fill="red",
                                               width=2)
            state.selection_shape_ids.append(line_id)

    def finish_lasso(event):
        state.canvas.unbind("<B1-Motion>")

        if len(state.selection_points) > 2:
            line_id = state.canvas.create_line(state.selection_points[-1],state.selection_points[0],
                fill="red", width=2)
            state.selection_shape_ids.append(line_id)

        image_cords = canvas_to_image_cords(state, state.selection_points)
        scaled_image_cords = scale_up_cords(state, image_cords)
        pts = np.array(scaled_image_cords, np.int32)
        mask = np.zeros(state.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)

        state.selection_mask = mask

    def start_polygon():
        reset_selection()

        state.canvas.bind("<Button-1>", add_polygon_point)
        state.canvas.bind("<Motion>", update_polygon)
        state.canvas.bind("<Button-3>", finish_polygon)

    def add_polygon_point( event):
        x, y = clamp_to_image(state, event.x, event.y)
        state.selection_points.append((x, y))

        if len(state.selection_points) > 1:
            state.canvas.coords(state.selection_shape_ids[-1], *state.selection_points[-2], *state.selection_points[-1])

        state.selection_shape_ids.append(
            state.canvas.create_line(state.selection_points[-1], state.selection_points[-1], fill="red", width=2))

    def update_polygon( event):
        if len(state.selection_shape_ids) < 1:
            return
        mouse_pos = clamp_to_image(state, event.x, event.y)
        state.canvas.coords(state.selection_shape_ids[-1], *state.selection_points[-1], *mouse_pos)

    def finish_polygon( event):
        state.canvas.unbind("<Button-1>")
        state.canvas.unbind("<Button-3>")
        state.canvas.unbind("<Motion>")

        if len(state.selection_points) > 2:
            state.canvas.coords(state.selection_shape_ids[-1], *state.selection_points[-1], *state.selection_points[0])

        image_cords = canvas_to_image_cords(state, state.selection_points)
        scaled_image_cords = scale_up_cords(state, image_cords)
        pts = np.array(scaled_image_cords, np.int32)
        mask = np.zeros(state.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        state.selection_mask = mask

    def start_crop():
        reset_selection()
        state.canvas.bind("<Button-1>", begin_crop)
        state.canvas.bind("<B1-Motion>", draw_crop_rectangle)
        state.canvas.bind("<ButtonRelease-1>", finish_crop)

    def begin_crop(event):
        state.selection_points.append(clamp_to_image(state, event.x, event.y))
        state.selection_points.append(state.selection_points[0])

        state.selection_shape_ids.append(
            state.canvas.create_rectangle(*state.selection_points[0], *state.selection_points[1], outline="blue", width=2))

    def draw_crop_rectangle(event):
        state.selection_points[1] = clamp_to_image(state, event.x, event.y)
        state.canvas.coords(state.selection_shape_ids[0], *state.selection_points[0], *state.selection_points[1])

    def finish_crop(event):
        state.canvas.unbind("<B1-Motion>")
        state.canvas.unbind("<Button-1>")
        state.canvas.unbind("<ButtonRelease-1>")

        x1, y1 = state.selection_points[0]
        x2, y2 = event.x, event.y

        x1, y1 = clamp_to_image(state, x1, y1)
        x2, y2 = clamp_to_image(state, x2, y2)

        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        [(x1, y1), (x2, y2)] = canvas_to_image_cords(state, [(x1, y1), (x2, y2)])
        [(x1, y1), (x2, y2)] = scale_up_cords(state, [(x1, y1), (x2, y2)])

        cropped = state.cv_image_full[y1:y2, x1:x2]
        if cropped.size == 0:
            print("Invalid crop ")
            return

        state.cv_image_full = cropped

        update_display_image(state)

    def resize_image():
        h, w = state.cv_image_full.shape[:2]
        new_w = simpledialog.askinteger("Resize", "Enter new width:", initialvalue=w, minvalue=1)
        new_h = simpledialog.askinteger("Resize", "Enter new height:", initialvalue=h, minvalue=1)
        if new_w and new_h:
            state.cv_image_full = cv2.resize(state.cv_image_full, (new_w, new_h))
            update_display_image(state)

    menu_image = Menu(menu_bar, tearoff=0)

    menu_select = Menu(menu_image, tearoff=0)
    menu_select.add_command(label="Rectangle", command=lambda: state.canvas.bind("<Button-1>", start_rectangle))
    menu_select.add_command(label="Lasso", command=lambda: state.canvas.bind("<Button-1>", start_lasso))
    menu_select.add_command(label="Polygon", command=lambda: start_polygon())
    menu_select.add_command(label="Crop", command=lambda: start_crop())
    menu_select.add_command(label="Resize", command=resize_image)
    menu_image.add_cascade(label="Select", menu=menu_select)

    menu_rotate = Menu(menu_image, tearoff=0)
    menu_rotate.add_command(label="Rotate CW",
                            command=lambda: apply_image_operation(rotate_90_degree_clockwise))
    menu_rotate.add_command(label="Rotate CCW",
                            command=lambda: apply_image_operation(
                                rotate_90_degree_counter_clockwise))
    menu_rotate.add_command(label="Flip Vertically",
                            command=lambda: apply_image_operation(flip_vertical))
    menu_rotate.add_command(label="Flip Horizontal",
                            command=lambda: apply_image_operation(flip_horizontal))
    menu_image.add_cascade(label="Rotate", menu=menu_rotate)

    menu_bar.add_cascade(label="Image", menu=menu_image)
