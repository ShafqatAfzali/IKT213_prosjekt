from tkinter import *

from PIL import Image, ImageTk
import cv2

import Image as imgFunc

root = Tk()
root.title("Title")
root.geometry("600x600")
root.configure(background="black")

def cv2_to_tk(cv_img):
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(cv_img_rgb)


class ImageEditingFrame(Frame):
    def __init__(self, master, *pargs):
        Frame.__init__(self, master, *pargs)

        self.original_cv_image = cv2.imread("img.png", cv2.IMREAD_UNCHANGED)
        self.cv_image = self.original_cv_image
        self.cv_image = cv2.imread("img.png", cv2.IMREAD_UNCHANGED)
        self.image = cv2_to_tk(self.cv_image)

        self.canvas = Canvas(self, width=600, height=600)
        self.canvas.pack(fill="both", expand=True)

        self.background_image = ImageTk.PhotoImage(self.image)


        self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind('<Motion>', self.motion)

        self.menu_bar = Menu(self)

        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=lambda: print("Open clicked"))
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.test = Menu(self.menu_bar, tearoff=0)
        self.test.add_command(label="Rotate Clockwise",
                              command=lambda: self.apply_image_operation(imgFunc.rotate90DegreeClockwise))
        self.test.add_command(label="Rotate Clockwise",
                              command=lambda: self.apply_image_operation(imgFunc.rotate90DegreeCounterClockwise))
        self.test.add_command(label="Flip Vertically",
                              command=lambda: self.apply_image_operation(imgFunc.flipVertical))
        self.test.add_command(label="Flip Horizontal",
                              command=lambda: self.apply_image_operation(imgFunc.flipHorizontal))
        self.menu_bar.add_cascade(label="Functions", menu=self.test)

        master.config(menu=self.menu_bar)

    def on_canvas_resize(self, event):
        width = event.width
        height = event.height
        self.resize_image_to_canvas(width, height)

    def motion(self, event):
        x, y = event.x, event.y
        print('{}, {}'.format(x, y))


    def resize_image_to_canvas(self, width, height):
        h, w, _ = self.cv_image.shape

        # Compute scale factor (fit inside max_width × max_height)
        scale = min(width / w, height / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        resized_cv_image = cv2.resize(self.original_cv_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        self.change_image(resized_cv_image)


    def change_image(self, cv_image):
        self.cv_image = cv_image
        self.image = cv2_to_tk(self.cv_image)
        self.img_copy= self.image.copy()
        self.background_image = ImageTk.PhotoImage(self.image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)

    def apply_image_operation(self, func):
        self.cv_image = func(self.cv_image)
        self.change_image(self.cv_image)

if __name__ == "__main__":
    imageEditingFrame = ImageEditingFrame(root)
    imageEditingFrame.pack(fill=BOTH, expand=YES)

    root.mainloop()