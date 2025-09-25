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
    pil_img = Image.fromarray(cv_img_rgb)
    return ImageTk.PhotoImage(pil_img)


class ImageEditingFrame(Frame):
    def __init__(self, master, *pargs):
        super().__init__(master, *pargs)

        self.cv_image_full = cv2.imread("img.png", cv2.IMREAD_UNCHANGED)
        self.cv_image_display = self.cv_image_full.copy()
        self.tk_background_image = cv2_to_tk(self.cv_image_display)

        self.selection_rect = None
        self.rect_start = None
        self.rect_end = None


        self.canvas = Canvas(self, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.update_display_image())
        self.canvas.bind("<Button-1>", self.start_rectangle)


        self.menu_bar = Menu(self)
        self.make_menu()
        master.config(menu=self.menu_bar)

    def make_menu(self):
        self.menu_functions = Menu(self.menu_bar, tearoff=0)
        self.menu_functions.add_command(label="Rotate CW",
                                        command=lambda: self.apply_image_operation(imgFunc.rotate90DegreeClockwise))
        self.menu_functions.add_command(label="Rotate CCW",
                                        command=lambda: self.apply_image_operation(imgFunc.rotate90DegreeCounterClockwise))
        self.menu_functions.add_command(label="Flip Vertically",
                                        command=lambda: self.apply_image_operation(imgFunc.flipVertical))
        self.menu_functions.add_command(label="Flip Horizontal",
                                        command=lambda: self.apply_image_operation(imgFunc.flipHorizontal))
        self.menu_functions.add_command(label="Crop",
                                        command=lambda: self.crop())
        self.menu_bar.add_cascade(label="Functions", menu=self.menu_functions)

    def start_rectangle(self, event):
        self.rect_start = (event.x, event.y)
        self.rect_end = self.rect_start
        self.selection_rect = self.canvas.create_rectangle(*self.rect_start, *self.rect_end, outline="red", width=2)
        self.canvas.bind("<Motion>", self.update_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.finish_rectangle)

    def update_rectangle(self, event):
        self.rect_end = (event.x, event.y)
        self.canvas.coords(self.selection_rect, *self.rect_start, *self.rect_end)

    def finish_rectangle(self, event):
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

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

        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        x0, x1 = sorted((max(0, x0), min(w, x1)))
        y0, y1 = sorted((max(0, y0), min(h, y1)))

        print(f"{x0=}, {x1=}")
        print(f"{y0=}, {y1=}")
        cropped = self.cv_image_full[y0:y1, x0:x1]
        if cropped.size == 0:
            print("⚠️ Invalid crop selection.")
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