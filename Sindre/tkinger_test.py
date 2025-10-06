from tkinter import simpledialog, Frame, Canvas, Tk, Menu, BOTH, YES

import numpy as np
from PIL import Image, ImageTk
import cv2
import Image_menu as imgFunc

root = Tk()
root.title("Title")
root.geometry("1000x1000")
root.configure(background="black")

def cv2_to_tk(cv_img):
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cv_img_rgb)
    return ImageTk.PhotoImage(pil_img)


class ImageEditingFrame(Frame):
    def __init__(self, master, *pargs):
        super().__init__(master, *pargs)

        self.cv_image_full = cv2.imread("img.png", cv2.IMREAD_UNCHANGED)
        self.cv_image_display = self.cv_image_full.copy()
        self.tk_background_image = cv2_to_tk(self.cv_image_display)

        self.selection_points = []
        self.selection_shape_ids = []
        self.selection_mask = None

        self.canvas = Canvas(self, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.update_display_image())


        self.menu_bar = Menu(self)
        self.make_menu()
        master.config(menu=self.menu_bar)

    def show_maks(self):
        cv2.imshow("mask", self.selection_mask)

    def make_menu(self):
        menu_image = Menu(self.menu_bar, tearoff=0)


        menu_select = Menu(menu_image, tearoff=0)
        menu_select.add_command(label="Rectangle",
                                     command=lambda: self.canvas.bind("<Button-1>", self.start_rectangle))
        menu_select.add_command(label="Free-form",
                                     command=lambda: self.canvas.bind("<Button-1>", self.start_lasso))
        menu_select.add_command(label="Polygon",
                                command=lambda:  self.start_polygon())
        menu_select.add_command(label="Crop",
                                command=lambda: self.start_crop())
        menu_select.add_command(label="Resize",
                                command=lambda: self.resize_image())
        menu_image.add_cascade(label="Select", menu=menu_select)


        menu_rotate = Menu(menu_image, tearoff=0)
        menu_rotate.add_command(label="Rotate CW",
                                        command=lambda: self.apply_image_operation(imgFunc.rotate90DegreeClockwise))
        menu_rotate.add_command(label="Rotate CCW",
                                        command=lambda: self.apply_image_operation(
                                            imgFunc.rotate90DegreeCounterClockwise))
        menu_rotate.add_command(label="Flip Vertically",
                                        command=lambda: self.apply_image_operation(imgFunc.flipVertical))
        menu_rotate.add_command(label="Flip Horizontal",
                                        command=lambda: self.apply_image_operation(imgFunc.flipHorizontal))
        menu_image.add_cascade(label="Rotate", menu=menu_rotate)

        self.menu_bar.add_cascade(label="Image", menu=menu_image)

        menu_test = Menu(self.menu_bar, tearoff=0)
        menu_test.add_command(label="Show mask",
                                command=lambda: self.show_maks())
        self.menu_bar.add_cascade(label="Test", menu=menu_test)

    def resize_image(self):
        h, w, _ = self.cv_image_full.shape
        new_w = simpledialog.askinteger("Resize", "Enter new width:", initialvalue=w, minvalue=1)
        new_h = simpledialog.askinteger("Resize", "Enter new height:", initialvalue=h, minvalue=1)

        if new_w and new_h:
            self.cv_image_full = cv2.resize(self.cv_image_full, (new_w, new_h), interpolation=cv2.INTER_AREA)
            self.update_display_image()

    def clamp_to_image(self, x, y):
        h, w, _ = self.cv_image_display.shape

        x = max(0, min(x, w))
        y = max(0, min(y, h))
        return (x, y)

    def scale_up_cords(self, cords):
        h_full, w_full, _ = self.cv_image_full.shape
        h_display, w_display, _ = self.cv_image_display.shape

        scale = w_full / w_display

        scaled_cords = []

        for x,y in cords:
            new_x = int(x * scale)
            new_y = int(y * scale)
            points = (new_x, new_y)
            scaled_cords.append(points)

        return scaled_cords

    def reset_selection_variables(self):
        for line_id in self.selection_shape_ids:
            self.canvas.delete(line_id)

        self.selection_points = []
        self.selection_shape_ids = []
        self.selection_mask = None

    def start_rectangle(self, event):
        self.reset_selection_variables()

        self.selection_points.append(self.clamp_to_image(event.x, event.y))
        self.selection_points.append(self.selection_points[0])

        self.selection_shape_ids.append(self.canvas.create_rectangle(*self.selection_points[0], *self.selection_points[1], outline="red", width=2))

        self.canvas.bind("<B1-Motion>", self.update_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.finish_rectangle)

    def update_rectangle(self, event):
        self.selection_points[1] = self.clamp_to_image(event.x, event.y)
        self.canvas.coords(self.selection_shape_ids[0], *self.selection_points[0], *self.selection_points[1])

    def finish_rectangle(self, event):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

        self.selection_points = self.scale_up_cords(self.selection_points)
        x1, y1 = self.selection_points[0]
        x2, y2 = self.selection_points[1]
        pts = np.array([[x1, y1],[x2, y1],[x2, y2],[x1, y2]], np.int32)
        mask = np.zeros(self.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)

        self.selection_mask = mask

    def start_lasso(self, event):
        self.reset_selection_variables()

        self.canvas.bind("<B1-Motion>", self.add_lasso_point)
        self.canvas.bind("<ButtonRelease-1>", self.finish_lasso)

    def add_lasso_point(self, event):
        x, y = self.clamp_to_image(event.x, event.y)
        self.selection_points.append((x, y))
        if len(self.selection_points) > 1:
            line_id = self.canvas.create_line(self.selection_points[-2], self.selection_points[-1], fill="red", width=2)
            self.selection_shape_ids.append(line_id)

    def finish_lasso(self, event):
        self.canvas.unbind("<B1-Motion>")

        if len(self.selection_points) > 2:
            line_id = self.canvas.create_line(
                self.selection_points[-1],
                self.selection_points[0],
                fill="red", width=2
            )
            self.selection_shape_ids.append(line_id)

        self.selection_points = self.scale_up_cords(self.selection_points)
        pts = np.array(self.selection_points, np.int32)
        mask = np.zeros(self.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)

        self.selection_mask = mask

    def start_polygon(self):
        self.reset_selection_variables()

        self.canvas.bind("<Button-1>", self.add_polygon_point)
        self.canvas.bind("<Motion>", self.update_polygon)
        self.canvas.bind("<Button-3>", self.finish_polygon)

    def add_polygon_point(self, event):
        x, y = self.clamp_to_image(event.x, event.y)
        self.selection_points.append((x, y))

        if len(self.selection_points) > 1:
            self.canvas.coords(self.selection_shape_ids[-1], *self.selection_points[-2], *self.selection_points[-1])

        self.selection_shape_ids.append(self.canvas.create_line(self.selection_points[-1], self.selection_points[-1], fill="red", width=2))

    def update_polygon(self, event):
        if len(self.selection_shape_ids) < 1:
            return
        mouse_pos = self.clamp_to_image(event.x, event.y)
        self.canvas.coords(self.selection_shape_ids[-1], *self.selection_points[-1], *mouse_pos)


    def finish_polygon(self, event):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-3>")
        self.canvas.unbind("<Motion>")

        if len(self.selection_points) > 2:
            self.canvas.coords(self.selection_shape_ids[-1], *self.selection_points[-1], *self.selection_points[0])

        self.selection_points = self.scale_up_cords(self.selection_points)
        pts = np.array(self.selection_points, np.int32)
        mask = np.zeros(self.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)

        self.selection_mask = mask

    def start_crop(self):
        self.reset_selection_variables()
        self.canvas.bind("<Button-1>", self.begin_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.finish_crop)

    def begin_crop(self, event):
        self.selection_points.append(self.clamp_to_image(event.x, event.y))
        self.selection_points.append(self.selection_points[0])

        self.selection_shape_ids.append(
            self.canvas.create_rectangle(*self.selection_points[0], *self.selection_points[1], outline="blue", width=2))


    def draw_crop_rectangle(self, event):
        self.selection_points[1] = self.clamp_to_image(event.x, event.y)
        self.canvas.coords(self.selection_shape_ids[0], *self.selection_points[0], *self.selection_points[1])

    def finish_crop(self, event):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<ButtonRelease-1>")

        x1, y1 = self.selection_points[0]
        x2, y2 = event.x, event.y

        x1, y1 = self.clamp_to_image(x1, y1)
        x2, y2 = self.clamp_to_image(x2, y2)

        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        [(x1,y1),(x2,y2)] = self.scale_up_cords([(x1,y1),(x2,y2)])

        cropped = self.cv_image_full[y1:y2, x1:x2]
        if cropped.size == 0:
            print("Invalid crop ")
            return

        self.cv_image_full = cropped

        self.update_display_image()

    def apply_image_operation(self, func):
        self.cv_image_full = func(self.cv_image_full)
        self.update_display_image()

    def update_display_image(self):
        '''
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()
        h, w, _ = self.cv_image_full.shape

        scale = min(c_width / w, c_height / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        self.cv_image_display = cv2.resize(self.cv_image_full, (new_w, new_h), interpolation=cv2.INTER_AREA)
        '''
        self.tk_background_image = cv2_to_tk(self.cv_image_display)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_background_image)

if __name__ == "__main__":
    imageEditingFrame = ImageEditingFrame(root)
    imageEditingFrame.pack(fill=BOTH, expand=YES)

    root.mainloop()