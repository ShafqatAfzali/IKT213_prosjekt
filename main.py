from tkinter import *
from PIL import Image, ImageTk
from Abdifatah.tools_menu import open_tools_menu


root = Tk()
root.title("Photo Editor - Group 20")
root.geometry("800x600")
root.configure(background="black")

# Menubar
menubar = Menu(root)
root.config(menu=menubar)


class Example(Frame):
    def __init__(self, master, *pargs):
        Frame.__init__(self, master, *pargs)

        # Sawirka bilowga (hubi inuu jiro img.png gudaha Sindre/)
        self.image = Image.open("Sindre/img.png")
        self.img_copy = self.image.copy()

        self.background_image = ImageTk.PhotoImage(self.image)

        # Canvas lagu tuso sawirka
        self.background = Label(self, image=self.background_image)
        self.background.pack(fill=BOTH, expand=YES)
        self.background.bind('<Configure>', self._resize_image)

    def _resize_image(self, event):
        new_width = event.width
        new_height = event.height
        self.image = self.img_copy.resize((new_width, new_height))
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)


# Instance ka mid ah class Example
e = Example(root)
e.pack(fill=BOTH, expand=YES)

# Add Tools menu (Abdifatah)
tools_menu = open_tools_menu(root, e.background, e.image)
menubar.add_cascade(label="Tools", menu=tools_menu)

# Placeholder menus for other team members (can be expanded later)
file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="Open")
file_menu.add_command(label="Save")
menubar.add_cascade(label="File", menu=file_menu)

image_menu = Menu(menubar, tearoff=0)
image_menu.add_command(label="Crop")
image_menu.add_command(label="Resize")
menubar.add_cascade(label="Image", menu=image_menu)

shapes_menu = Menu(menubar, tearoff=0)
shapes_menu.add_command(label="Rectangle")
shapes_menu.add_command(label="Circle")
menubar.add_cascade(label="Shapes", menu=shapes_menu)

colors_menu = Menu(menubar, tearoff=0)
colors_menu.add_command(label="Pick Color")
menubar.add_cascade(label="Colors", menu=colors_menu)

clipboard_menu = Menu(menubar, tearoff=0)
clipboard_menu.add_command(label="Copy")
clipboard_menu.add_command(label="Paste")
menubar.add_cascade(label="Clipboard", menu=clipboard_menu)

# Start app
root.mainloop()
