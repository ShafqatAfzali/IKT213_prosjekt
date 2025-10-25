from tkinter import Menu, simpledialog

import cv2
import numpy as np

from helpers.menu_utils import add_menu_command_with_hotkey
from helpers.image_render import update_display_image
from helpers.cord_utils import clamp_to_image, full_image_cords_to_canvas_cords, canvas_to_full_image_cords
from helpers.image_transform import rotate_90_degree_clockwise, rotate_90_degree_counter_clockwise, flip_horizontal, flip_vertical
from classes.state import State

# NOTE TO SELF: Tidy up

def create_image_menu(state: State, menu_bar):
    def reset_selection():
        state.canvas.unbind("<Escape>")
        for line_id in state.shape_ids:
            state.canvas.delete(line_id)
        state.shape_points.clear()
        state.shape_ids.clear()
        state.selection_mask = None

    def create_mask_from_points(points):
        if points is None or len(points) < 1:
            return None
        pts = np.array(points, np.int32)
        mask = np.zeros(state.original_image.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        return mask

    def apply_image_operation(func):
        state.operations.append((func, [], {}))
        state.redo_stack.clear()
        update_display_image(state)

# ---------- Rectangle ----------
    def start_rectangle(event):
        reset_selection()

        x,y = clamp_to_image(state, event.x, event.y)

        [(x_full, y_full)] = canvas_to_full_image_cords(state, [(x, y)])

        state.shape_points = [(x_full, y_full), (x_full, y_full)]

        rect_id = state.canvas.create_rectangle((x,y), (x,y), outline="red", width=2)
        state.shape_ids = [rect_id]

        state.canvas.bind("<B1-Motion>", update_rectangle)
        state.canvas.bind("<ButtonRelease-1>", finish_rectangle)

    def update_rectangle(event):
        x,y = clamp_to_image(state, event.x, event.y)
        [(x_full, y_full)] = canvas_to_full_image_cords(state, [(x, y)])

        state.shape_points[1] = (x_full, y_full)

        [(x0_disp, y0_disp)] = full_image_cords_to_canvas_cords(state, [state.shape_points[0]])

        state.canvas.coords(state.shape_ids[0], x0_disp, y0_disp, x, y)
    def finish_rectangle(event):
        state.canvas.unbind("<Button-1>")
        state.canvas.unbind("<B1-Motion>")
        state.canvas.unbind("<ButtonRelease-1>")
        p1, p2 = state.shape_points
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

        [(x_full, y_full)] = canvas_to_full_image_cords(state, [(x, y)])

        state.shape_points.append((x_full, y_full))

        if len(state.shape_points) > 1:
            [(x0_disp, y0_disp)] = full_image_cords_to_canvas_cords(state, [state.shape_points[-2]])

            line_id = state.canvas.create_line((x0_disp, y0_disp), (x,y), fill="red",
                                               width=2)
            state.shape_ids.append(line_id)

    def finish_lasso(event):
        state.canvas.unbind("<B1-Motion>")
        state.canvas.unbind("<ButtonRelease-1>")
        if len(state.shape_points) > 2:
            p1_full = state.shape_points[0]
            p2_full = state.shape_points[-1]

            disp_cords = full_image_cords_to_canvas_cords(state, {p1_full, p2_full})


            line_id = state.canvas.create_line(disp_cords[1], disp_cords[0],
                fill="red", width=2)
            state.shape_ids.append(line_id)
        state.selection_mask = create_mask_from_points(state.shape_points)
        state.canvas.bind("<Escape>", lambda _: reset_selection())

# ---------- Polygon ----------
    def start_polygon():
        reset_selection()
        state.canvas.bind("<Button-1>", add_polygon_point)
        state.canvas.bind("<Motion>", update_polygon)
        state.canvas.bind("<Button-3>", finish_polygon)

    def add_polygon_point(event):
        x, y = clamp_to_image(state, event.x, event.y)

        [(x_full, y_full)] = canvas_to_full_image_cords(state, [(x, y)])
        state.shape_points.append((x_full, y_full))

        if len(state.shape_points) > 1:
            [(x0_disp, y0_disp)] = full_image_cords_to_canvas_cords(state, [state.shape_points[-2]])
            state.canvas.coords(state.shape_ids[-1], (x0_disp, y0_disp), (x, y))
        line_id = state.canvas.create_line((x,y), (x,y), fill="red", width=2)
        state.shape_ids.append(line_id)

    def update_polygon(event):
        if len(state.shape_ids) < 1:
            return
        mouse_pos = clamp_to_image(state, event.x, event.y)
        [p0] = full_image_cords_to_canvas_cords(state, [state.shape_points[-1]])
        state.canvas.coords(state.shape_ids[-1], p0, *mouse_pos)

    def finish_polygon(event):
        state.canvas.unbind("<Button-1>")
        state.canvas.unbind("<Button-3>")
        state.canvas.unbind("<Motion>")

        if len(state.shape_points) > 2:
            [p0, p1] = full_image_cords_to_canvas_cords(state, [state.shape_points[-1], state.shape_points[0]])

            state.canvas.coords(state.shape_ids[-1], p0, p1)

        state.selection_mask = create_mask_from_points(state.shape_points)
        state.canvas.bind("<Escape>", lambda _: reset_selection())


# ---------- Crop ----------
    # TODO: Store crop points as full_image coordinates, wil fix zoom and crop issues
    def start_crop():
        reset_selection()
        state.cropping = True
        if state.crop_metadata:
            cm = state.crop_metadata
            x0_full, y0_full, x1_full, y1_full = cm['x0'], cm['y0'], cm['x1'], cm['y1']
            update_display_image(state, cropping=True)
            state.shape_points = [(x0_full, y0_full), (x1_full, y1_full)]
            [(x0, y0), (x1, y1)] = full_image_cords_to_canvas_cords(state, [(x0_full, y0_full), (x1_full, y1_full)], cropping=True)
            rect_id = state.canvas.create_rectangle(x0,y0,x1,y1, outline="blue", width=2)
            state.shape_ids = [rect_id]
            draw_crop_overlay()
        else:
            h,w,_ = state.cv_image_full.shape
            x0_full, y0_full = 0,0
            x1_full, y1_full = w,h
            state.shape_points = [(x0_full, y0_full), (x1_full, y1_full)]
            [(x0_can,y0_can), (x1_can, y1_can)] = full_image_cords_to_canvas_cords(state, [(0, 0), (w, h)])
            rect_id = state.canvas.create_rectangle((x0_can,y0_can), (x1_can, y1_can), outline="blue", width=2)
            state.shape_ids = [rect_id]


        state.canvas.bind("<Button-1>", begin_crop_drag)
        state.canvas.bind("<B1-Motion>", move_crop_corner)
        state.canvas.bind("<Control-q>", finish_crop_drag)

    def begin_crop_drag(event):
        x, y = event.x, event.y
        pts = state.shape_points
        d0 = (x - pts[0][0]) ** 2 + (y - pts[0][1]) ** 2
        d1 = (x - pts[1][0]) ** 2 + (y - pts[1][1]) ** 2
        state.active_corner = 0 if d0 < d1 else 1

    def draw_crop_overlay():
        """Draws a dark transparent overlay outside the current crop rectangle."""
        state.canvas.delete("crop_overlay")

        if not state.shape_points:
            return

        (x0_full, y0_full), (x1_full, y1_full) = state.shape_points
        (x0_can, y0_can), (x1_can, y1_can) = (
            full_image_cords_to_canvas_cords(state, [(x0_full, y0_full), (x1_full, y1_full)], cropping=True))
        print(f"1.{x0_can=}\t{y0_can=}\t{x1_can=}\t{y1_can=}")
        c_width = state.canvas.winfo_width()
        c_height = state.canvas.winfo_height()

        # Four rectangles around the crop area
        rects = [
            (0, 0, c_width, y0_can),  # top
            (0, y0_can, x0_can, y1_can),  # left
            (x1_can, y0_can, c_width, y1_can),  # right
            (0, y1_can, c_width, c_height)  # bottom
        ]

        for (x0_, y0_, x1_, y1_) in rects:
            state.canvas.create_rectangle(
                x0_, y0_, x1_, y1_,
                fill="black",
                stipple="gray25",  # makes it semi-transparent
                width=0,
                tags="crop_overlay"
            )

        if state.shape_ids:
            state.canvas.tag_raise(state.shape_ids[0])

    def move_crop_corner(event):
        if hasattr(state, "active_corner"):
            pts_can = full_image_cords_to_canvas_cords(state, state.shape_points, cropping=True)
            print(f"{pts_can=}")
            pts_can[state.active_corner] = clamp_to_image(state, event.x, event.y)
            state.shape_points = canvas_to_full_image_cords(state, pts_can, cropping=True)
            state.canvas.coords(state.shape_ids[0], *pts_can[0], *pts_can[1])
            draw_crop_overlay()

    def finish_crop_drag(event):
        if not state.shape_points:
            return
        (x0, y0), (x1, y1) = state.shape_points
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))

        state.operations.append((apply_crop, [x0, y0, x1, y1], {}))
        state.cropping = False
        state.canvas.delete("crop_overlay")
        state.canvas.unbind("<Button-1>")
        state.canvas.unbind("<B1-Motion>")
        state.canvas.unbind("<ButtonRelease-1>")
        reset_selection()
        update_display_image(state)

    def apply_crop(image, x0, y0, x1, y1):
        state.crop_metadata = {'x0': int(x0), 'y0': int(y0), 'x1': int(x1), 'y1': int(y1)}
        return image

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
        state.redo_stack.clear()
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
    add_menu_command_with_hotkey(state=state, menu=menu_rotate, label="Rotate CW",
                                 command=lambda: apply_image_operation(rotate_90_degree_clockwise),
                                 hotkey="Control+e")
    menu_rotate.add_command(label="Rotate CCW",
                            command=lambda: apply_image_operation(rotate_90_degree_counter_clockwise))
    menu_rotate.add_command(label="Flip Vertically",
                            command=lambda: apply_image_operation(flip_vertical))
    menu_rotate.add_command(label="Flip Horizontal",
                            command=lambda: apply_image_operation(flip_horizontal))
    menu_image.add_cascade(label="Rotate", menu=menu_rotate)

    menu_bar.add_cascade(label="Image", menu=menu_image)
