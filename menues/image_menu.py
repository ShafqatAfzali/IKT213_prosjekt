from tkinter import Menu, simpledialog

import cv2
import numpy as np

from other.helper_functions import update_display_image, scale_to_full_image_cords, canvas_to_image_cords_xy_sets, \
    clamp_to_image, canvas_to_image_offset, get_display_scale, full_image_cords_to_display
from other.image_rotation import rotate_90_degree_clockwise, rotate_90_degree_counter_clockwise, flip_horizontal, flip_vertical
from classes.state import State

# NOTE TO SELF: Tidy up

def create_image_menu(state: State, menu_bar):
    def reset_selection():
        state.canvas.unbind("<Escape>")
        for line_id in state.selection_shape_ids:
            state.canvas.delete(line_id)
        state.selection_points.clear()
        state.selection_shape_ids.clear()
        state.selection_mask = None

    def create_mask_from_points(points):
        if points is None or len(points) < 1:
            return None
        pts = np.array(points, np.int32)
        mask = np.zeros(state.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        return mask

    def apply_image_operation(func):
        state.operations.append((func, [], {}))
        update_display_image(state)

# ---------- Rectangle ----------
    def start_rectangle(event):
        reset_selection()

        x,y = clamp_to_image(state, event.x, event.y)

        w_offset, h_offset = canvas_to_image_offset(state)
        [(x_full, y_full)] = scale_to_full_image_cords(state, [(x-w_offset,y-h_offset)])

        state.selection_points = [(x_full, y_full), (x_full, y_full)]

        rect_id = state.canvas.create_rectangle((x,y), (x,y), outline="red", width=2)
        state.selection_shape_ids = [rect_id]

        state.canvas.bind("<B1-Motion>", update_rectangle)
        state.canvas.bind("<ButtonRelease-1>", finish_rectangle)

    def update_rectangle(event):
        x,y = clamp_to_image(state, event.x, event.y)
        w_offset, h_offset = canvas_to_image_offset(state)
        [(x_full, y_full)] = scale_to_full_image_cords(state, [(x-w_offset,y-h_offset)])

        state.selection_points[1] = (x_full, y_full)

        scale = get_display_scale(state)
        offset_x, offset_y = canvas_to_image_offset(state)

        (x0_full, y0_full) = state.selection_points[0]

        x0_disp = x0_full * scale + offset_x
        y0_disp = y0_full * scale + offset_y

        state.canvas.coords(state.selection_shape_ids[0],x0_disp, y0_disp, x, y)
    def finish_rectangle(event):
        state.canvas.unbind("<Button-1>")
        state.canvas.unbind("<B1-Motion>")
        state.canvas.unbind("<ButtonRelease-1>")
        p1, p2 = state.selection_points
        # create mask with a point in each of the 4 corners of the rectangle
        state.selection_mask = create_mask_from_points([(p1[0], p1[1]), (p2[0], p1[1]), (p2[0], p2[1]), (p1[0], p2[1])])
        state.canvas.bind("<Escape>", lambda _: reset_selection())

    # ---------- Lasso -------------
    def start_lasso(event):
        reset_selection()
        state.canvas.bind("<B1-Motion>", add_lasso_point)
        state.canvas.bind("<ButtonRelease-1>", finish_lasso)

    def add_lasso_point(event):
        x, y = clamp_to_image(state, event.x, event.y)

        w_offset, h_offset = canvas_to_image_offset(state)
        [(x_full, y_full)] = scale_to_full_image_cords(state, [(x - w_offset, y - h_offset)])
        scale = get_display_scale(state)

        state.selection_points.append((x_full, y_full))

        if len(state.selection_points) > 1:
            (x0_full, y0_full) = state.selection_points[-2]
            x0_disp = x0_full * scale + w_offset
            y0_disp = y0_full * scale + h_offset

            line_id = state.canvas.create_line((x0_disp, y0_disp), (x,y), fill="red",
                                               width=2)
            state.selection_shape_ids.append(line_id)

    def finish_lasso(event):
        state.canvas.unbind("<B1-Motion>")
        state.canvas.unbind("<ButtonRelease-1>")
        if len(state.selection_points) > 2:
            p1_full = state.selection_points[0]
            p2_full = state.selection_points[-1]

            disp_cords = full_image_cords_to_display(state, {p1_full, p2_full})


            line_id = state.canvas.create_line(disp_cords[1], disp_cords[0],
                fill="red", width=2)
            state.selection_shape_ids.append(line_id)
        state.selection_mask = create_mask_from_points(state.selection_points)
        state.canvas.bind("<Escape>", lambda _: reset_selection())

# ---------- Polygon ----------
    def start_polygon():
        reset_selection()
        state.canvas.bind("<Button-1>", add_polygon_point)
        state.canvas.bind("<Motion>", update_polygon)
        state.canvas.bind("<Button-3>", finish_polygon)

    def add_polygon_point(event):
        x, y = clamp_to_image(state, event.x, event.y)

        w_offset, h_offset = canvas_to_image_offset(state)
        [(x_full, y_full)] = scale_to_full_image_cords(state, [(x - w_offset, y - h_offset)])
        scale = get_display_scale(state)

        state.selection_points.append((x_full, y_full))

        if len(state.selection_points) > 1:
            (x0_full, y0_full) = state.selection_points[-2]
            x0_disp = x0_full * scale + w_offset
            y0_disp = y0_full * scale + h_offset

            state.canvas.coords(state.selection_shape_ids[-1], (x0_disp, y0_disp), (x,y))
        line_id = state.canvas.create_line((x,y), (x,y), fill="red", width=2)
        state.selection_shape_ids.append(line_id)

    def update_polygon(event):
        if len(state.selection_shape_ids) < 1:
            return
        mouse_pos = clamp_to_image(state, event.x, event.y)
        [p0] = full_image_cords_to_display(state, [state.selection_points[-1]])
        state.canvas.coords(state.selection_shape_ids[-1], p0, *mouse_pos)

    def finish_polygon(event):
        state.canvas.unbind("<Button-1>")
        state.canvas.unbind("<Button-3>")
        state.canvas.unbind("<Motion>")

        if len(state.selection_points) > 2:
            [p0, p1] = full_image_cords_to_display(state, [state.selection_points[-1], state.selection_points[0]])

            state.canvas.coords(state.selection_shape_ids[-1], p0, p1)

        state.selection_mask = create_mask_from_points(state.selection_points)
        state.canvas.bind("<Escape>", lambda _: reset_selection())


# ---------- Crop ----------
    def start_crop():
        reset_selection()
        state.canvas.bind("<Button-1>", begin_crop)
        state.canvas.bind("<B1-Motion>", draw_crop_rectangle)
        state.canvas.bind("<ButtonRelease-1>", finish_crop)

    def begin_crop(event):
        p = clamp_to_image(state, event.x, event.y)
        state.selection_points = [p, p]
        rect_id = state.canvas.create_rectangle(*p, *p, outline="blue", width=2)
        state.selection_shape_ids = [rect_id]

    def draw_crop_rectangle(event):
        state.selection_points[1] = clamp_to_image(state, event.x, event.y)
        state.canvas.coords(state.selection_shape_ids[0], *state.selection_points[0], *state.selection_points[1])

    def finish_crop(event):
        state.canvas.unbind("<B1-Motion>")
        state.canvas.unbind("<Button-1>")
        state.canvas.unbind("<ButtonRelease-1>")

        (x1, y1), (x2, y2) = [clamp_to_image(state, *p) for p in state.selection_points]
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        [(x1, y1), (x2, y2)] = canvas_to_image_cords_xy_sets(state, [(x1, y1), (x2, y2)])
        [(x1, y1), (x2, y2)] = scale_to_full_image_cords(state, [(x1, y1), (x2, y2)])

        state.operations.append((crop_image, [x1, y1, x2, y2], {}))
        reset_selection()
        update_display_image(state)

    def crop_image(image, x1, y1, x2, y2):
        cropped = state.cv_image_full[y1:y2, x1:x2]
        if cropped.size == 0:
            print("Invalid crop ")
            return image
        return cropped

    def resize_image(image, new_w, new_h):
        if new_w and new_h:
            image = cv2.resize(image, (new_w, new_h))
            return image
        return image

    def apply_resize():
        h, w = state.cv_image_full.shape[:2]
        new_w = simpledialog.askinteger("Resize", "Enter new width:", initialvalue=w, minvalue=1)
        new_h = simpledialog.askinteger("Resize", "Enter new height:", initialvalue=h, minvalue=1)
        state.operations.append((resize_image, [new_w, new_h], {}))
        update_display_image(state)

    menu_image = Menu(menu_bar, tearoff=0)

    menu_select = Menu(menu_image, tearoff=0)
    menu_select.add_command(label="Rectangle", command=lambda: state.canvas.bind("<Button-1>", start_rectangle))
    menu_select.add_command(label="Lasso", command=lambda: state.canvas.bind("<Button-1>", start_lasso))
    menu_select.add_command(label="Polygon", command=lambda: start_polygon())
    menu_select.add_command(label="Crop", command=lambda: start_crop())
    menu_select.add_command(label="Resize", command=apply_resize)
    menu_image.add_cascade(label="Select", menu=menu_select)

    menu_rotate = Menu(menu_image, tearoff=0)
    menu_rotate.add_command(label="Rotate CW",
                            command=lambda: apply_image_operation(rotate_90_degree_clockwise))
    menu_rotate.add_command(label="Rotate CCW",
                            command=lambda: apply_image_operation(rotate_90_degree_counter_clockwise))
    menu_rotate.add_command(label="Flip Vertically",
                            command=lambda: apply_image_operation(flip_vertical))
    menu_rotate.add_command(label="Flip Horizontal",
                            command=lambda: apply_image_operation(flip_horizontal))
    menu_image.add_cascade(label="Rotate", menu=menu_rotate)

    menu_bar.add_cascade(label="Image", menu=menu_image)
