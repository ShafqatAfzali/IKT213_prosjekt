from tkinter import simpledialog, Frame, Canvas, Tk, Menu, BOTH, YES

import numpy as np
from PIL import Image, ImageTk
import cv2
import Image as imgFunc
from Selection import Selection

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

        self.selection = Selection()

        self.canvas = Canvas(self, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.update_display_image())


        self.menu_bar = Menu(self)
        self.make_menu()
        master.config(menu=self.menu_bar)

    def make_menu(self):
        menu_image = Menu(self.menu_bar, tearoff=0)

        menu_select = Menu(menu_image, tearoff=0)
        menu_select.add_command(label="Rectangle",
                                     command=lambda: self.canvas.bind("<Button-1>", self.start_rectangle))
        menu_select.add_command(label="Free-form",
                                     command=lambda: print("Free-form"))
        menu_select.add_command(label="Polygon",
                                command=lambda:  self.start_polygon())
        menu_select.add_command(label="Crop",
                                command=lambda: self.crop())
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

    # TODO: Take input and return output
    def cords_to_full(self):
        h_full, w_full, _ = self.cv_image_full.shape
        h_display, w_display, _ = self.cv_image_display.shape

        scale = w_full / w_display

        tmp = []

        for x,y in self.selection.points:
            new_x = int(x * scale)
            new_y = int(y * scale)
            points = (new_x, new_y)
            tmp.append(points)

        self.selection.points = tmp

    def start_rectangle(self, event):
        self.selection.reset_variables()

        self.selection.points.append(self.clamp_to_image(event.x, event.y))
        self.selection.points.append(self.selection.points[0])

        self.selection.to_mouse_shape = self.canvas.create_rectangle(*self.selection.points[0], *self.selection.points[1], outline="red", width=2)
        self.canvas.bind("<Motion>", self.update_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.finish_rectangle)

    def update_rectangle(self, event):
        self.selection.points[1] = self.clamp_to_image(event.x, event.y)
        self.canvas.coords(self.selection.to_mouse_shape, *self.selection.points[0], *self.selection.points[1])

    def finish_rectangle(self, event):
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<ButtonRelease-1>")


        self.cords_to_full()

        start = self.selection.points[0]
        end = self.selection.points[1]

        pts = np.array([
            [start[0], start[1]],
            [end[0], start[1]],
            [end[0], end[1]],
            [start[0], end[1]]
        ], np.int32)

        mask = np.zeros(self.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)

        self.selection.mask = mask


    def start_polygon(self):
        self.selection.reset_variables()
        self.canvas.bind("<Button-1>", self.add_polygon_point)

    def add_polygon_point(self, event):
        x, y = self.clamp_to_image(event.x, event.y)
        self.selection.points.append((x, y))

        if len(self.selection.points) > 1:
            line_id = self.canvas.create_line(self.selection.points[-2], self.selection.points[-1], fill="red", width=2)
            self.selection.shape_ids.append(line_id)

        self.selection.to_mouse_shape = self.canvas.create_line(self.selection.points[-1], self.selection.points[-1], fill="red", width=2)

        self.canvas.bind("<Motion>", self.update_polygon)
        self.canvas.bind("<Button-3>", self.finish_polygon)

    def update_polygon(self, event):
        mouse_pos = self.clamp_to_image(event.x, event.y)
        self.canvas.coords(self.selection.to_mouse_shape, *self.selection.points[-1], *mouse_pos)


    def finish_polygon(self, event):
        if len(self.selection.points) > 2:
            line_id = self.canvas.create_line(self.selection.points[-1], self.selection.points[0], fill="red", width=2)
            self.selection.shape_ids.append(line_id)

        self.canvas.delete(self.selection.to_mouse_shape)

        self.cords_to_full()

        pts = np.array(self.selection.points, np.int32)

        mask = np.zeros(self.cv_image_full.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)

        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-3>")
        self.canvas.unbind("<Motion>")

        self.selection.mask = mask


    # TODO: Add lasso
    # TODO: Improve and clean

    # TODO: Finish after changing select
    def crop(self):
        h, w, _ = self.cv_image_full.shape
        c_w = self.canvas.winfo_width()
        c_h = self.canvas.winfo_height()

        # Same scale used in update_display_image
        scale = min(c_w / w, c_h / h)

        # Map canvas coords → image coords
        x0 = int((self.rect_start[0]) / scale)
        y0 = int((self.rect_start[1]) / scale)
        x1 = int((self.rect_end[0]) / scale)
        y1 = int((self.rect_end[1]) / scale)

        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))

        print(f"{x0=}, {x1=}")
        print(f"{y0=}, {y1=}")
        cropped = self.cv_image_full[y0:y1, x0:x1]
        if cropped.size == 0:
            print("Invalid crop selection.")
            return

        self.cv_image_full = cropped
        self.update_display_image()

    def apply_image_operation(self, func):
        self.cv_image_full = func(self.cv_image_full)
        self.update_display_image()

    def update_display_image(self):
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()
        h, w, _ = self.cv_image_full.shape

        scale = min(c_width / w, c_height / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        self.cv_image_display = cv2.resize(self.cv_image_full, (new_w, new_h), interpolation=cv2.INTER_AREA)
        self.tk_background_image = cv2_to_tk(self.cv_image_display)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_background_image)

if __name__ == "__main__":
    imageEditingFrame = ImageEditingFrame(root)
    imageEditingFrame.pack(fill=BOTH, expand=YES)

    root.mainloop()