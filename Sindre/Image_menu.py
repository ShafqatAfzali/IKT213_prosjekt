from tkinter import Menu, simpledialog

import cv2
import numpy as np

import Sindre.helper_functions as helper

def create_image_menu(tmpState, menu_bar):
    def update_display_image():
        tmpState.cv_image_display = tmpState.cv_image_full
        tmpState.tk_image = helper.cv2_to_tk(tmpState.cv_image_display)
        tmpState.canvas.delete("all")
        tmpState.canvas.create_image(0, 0, anchor="nw", image=tmpState.tk_image)

    def apply_image_operation(func):
        tmpState.cv_image_full = func(tmpState.cv_image_full)
        update_display_image()

    def clamp_to_image(x, y):
        h, w = tmpState.cv_image_display.shape[:2]
        return max(0, min(x, w)), max(0, min(y, h))

    def scale_up_cords(cords):
        h_full, w_full, _ = tmpState.cv_image_full.shape
        h_display, w_display, _ = tmpState.cv_image_display.shape

        scale = w_full / w_display

        scaled_cords = []

        for x,y in cords:
            new_x = int(x * scale)
            new_y = int(y * scale)
            points = (new_x, new_y)
            scaled_cords.append(points)

        return scaled_cords

    def reset_selection():
        for line_id in tmpState.selection_shape_ids:
            tmpState.canvas.delete(line_id)
        tmpState.selection_points = []
        tmpState.selection_shape_ids = []
        tmpState.selection_mask = None

    def start_rectangle(event):
        reset_selection()
        tmpState.selection_points.append(clamp_to_image(event.x, event.y))
        tmpState.selection_points.append(tmpState.selection_points[0])
        rect_id = tmpState.canvas.create_rectangle(*tmpState.selection_points[0], *tmpState.selection_points[1],
                                          outline="red", width=2)
        tmpState.selection_shape_ids.append(rect_id)
        tmpState.canvas.bind("<B1-Motion>", update_rectangle)
        tmpState.canvas.bind("<ButtonRelease-1>", finish_rectangle)

    def update_rectangle(event):
        tmpState.selection_points[1] = clamp_to_image(event.x, event.y)
        tmpState.canvas.coords(tmpState.selection_shape_ids[0], *tmpState.selection_points[0], *tmpState.selection_points[1])

    def finish_rectangle(event):
        tmpState.canvas.unbind("<B1-Motion>")
        tmpState.canvas.unbind("<ButtonRelease-1>")
        tmpState.selection_points = scale_up_cords(tmpState.selection_points)
        x1, y1 = tmpState.selection_points[0]
        x2, y2 = tmpState.selection_points[1]
        pts = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], np.int32)

        mask = np.zeros(tmpState.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        tmpState.selection_mask = mask

    def start_lasso(event):
        reset_selection()

        tmpState.canvas.bind("<B1-Motion>", add_lasso_point)
        tmpState.canvas.bind("<ButtonRelease-1>", finish_lasso)

    def add_lasso_point(event):
        x, y = clamp_to_image(event.x, event.y)
        tmpState.selection_points.append((x, y))
        if len(tmpState.selection_points) > 1:
            line_id = tmpState.canvas.create_line(tmpState.selection_points[-2], tmpState.selection_points[-1], fill="red",
                                              width=2)
            tmpState.selection_shape_ids.append(line_id)

    def finish_lasso(event):
        tmpState.canvas.unbind("<B1-Motion>")

        if len(tmpState.selection_points) > 2:
            line_id = tmpState.canvas.create_line(
                tmpState.selection_points[-1],
                tmpState.selection_points[0],
                fill="red", width=2
            )
            tmpState.selection_shape_ids.append(line_id)

        tmpState.selection_points = scale_up_cords(tmpState.selection_points)
        pts = np.array(tmpState.selection_points, np.int32)
        mask = np.zeros(tmpState.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)

        tmpState.selection_mask = mask

    def start_polygon():
        reset_selection()

        tmpState.canvas.bind("<Button-1>", add_polygon_point)
        tmpState.canvas.bind("<Motion>", update_polygon)
        tmpState.canvas.bind("<Button-3>", finish_polygon)

    def add_polygon_point( event):
        x, y = clamp_to_image(event.x, event.y)
        tmpState.selection_points.append((x, y))

        if len(tmpState.selection_points) > 1:
            tmpState.canvas.coords(tmpState.selection_shape_ids[-1], *tmpState.selection_points[-2], *tmpState.selection_points[-1])

        tmpState.selection_shape_ids.append(
            tmpState.canvas.create_line(tmpState.selection_points[-1], tmpState.selection_points[-1], fill="red", width=2))

    def update_polygon( event):
        if len(tmpState.selection_shape_ids) < 1:
            return
        mouse_pos = clamp_to_image(event.x, event.y)
        tmpState.canvas.coords(tmpState.selection_shape_ids[-1], *tmpState.selection_points[-1], *mouse_pos)

    def finish_polygon( event):
        tmpState.canvas.unbind("<Button-1>")
        tmpState.canvas.unbind("<Button-3>")
        tmpState.canvas.unbind("<Motion>")

        if len(tmpState.selection_points) > 2:
            tmpState.canvas.coords(tmpState.selection_shape_ids[-1], *tmpState.selection_points[-1], *tmpState.selection_points[0])

        tmpState.selection_points = scale_up_cords(tmpState.selection_points)
        pts = np.array(tmpState.selection_points, np.int32)
        mask = np.zeros(tmpState.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        tmpState.selection_mask = mask

    def start_crop(event):
        start_rectangle(event)  # reuse rectangle logic

    def resize_image():
        h, w = tmpState.cv_image_full.shape[:2]
        new_w = simpledialog.askinteger("Resize", "Enter new width:", initialvalue=w, minvalue=1)
        new_h = simpledialog.askinteger("Resize", "Enter new height:", initialvalue=h, minvalue=1)
        if new_w and new_h:
            tmpState.cv_image_full = cv2.resize(tmpState.cv_image_full, (new_w, new_h))
            update_display_image()

    menu_image = Menu(menu_bar, tearoff=0)

    menu_select = Menu(menu_image, tearoff=0)
    menu_select.add_command(label="Rectangle", command=lambda: tmpState.canvas.bind("<Button-1>", start_rectangle))
    menu_select.add_command(label="Lasso", command=lambda: tmpState.canvas.bind("<Button-1>", start_lasso))
    menu_select.add_command(label="Polygon", command=lambda: start_polygon())
    menu_select.add_command(label="Crop", command=lambda: tmpState.canvas.bind("<Button-1>", start_crop))
    menu_select.add_command(label="Resize", command=resize_image)
    menu_image.add_cascade(label="Select", menu=menu_select)

    menu_rotate = Menu(menu_image, tearoff=0)
    menu_rotate.add_command(label="Rotate CW",
                            command=lambda: apply_image_operation(helper.rotate90DegreeClockwise))
    menu_rotate.add_command(label="Rotate CCW",
                            command=lambda: apply_image_operation(
                                helper.rotate90DegreeCounterClockwise))
    menu_rotate.add_command(label="Flip Vertically",
                            command=lambda: apply_image_operation(helper.flipVertical))
    menu_rotate.add_command(label="Flip Horizontal",
                            command=lambda: apply_image_operation(helper.flipHorizontal))
    menu_image.add_cascade(label="Rotate", menu=menu_rotate)

    menu_bar.add_cascade(label="Image", menu=menu_image)
