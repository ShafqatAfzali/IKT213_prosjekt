import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


current_image = None
current_image_tk = None
current_file_path = None


def new_file():
    global current_image, current_image_tk, current_file_path
    current_image = None
    current_image_tk = None
    current_file_path = None
    canvas.delete("all")
    messagebox.showinfo("New File", "Started a new workspace.")


def open_file():
    global current_image, current_image_tk, current_file_path
    file_path = filedialog.askopenfilename(
        title="Open Image",
        filetypes=(("Image Files", "*.jpg;*.jpeg;*.png;*.gif"), ("All Files", "*.*"))
    )
    if file_path:
        current_file_path = file_path
        current_image = Image.open(file_path)
        display_image(current_image)


def save_file():
    global current_file_path, current_image
    if current_file_path and current_image:
        current_image.save(current_file_path)
        messagebox.showinfo("Save", f"File saved: {current_file_path}")
    else:
        save_as_file()


def save_as_file():
    global current_file_path, current_image
    if current_image:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*"))
        )
        if file_path:
            current_file_path = file_path
            current_image.save(file_path)
            messagebox.showinfo("Save As", f"File saved as: {file_path}")


def show_properties():
    global current_image, current_file_path
    if current_image:
        props = f"File: {current_file_path}\nSize: {current_image.size}\nMode: {current_image.mode}"
        messagebox.showinfo("Properties", props)
    else:
        messagebox.showwarning("Properties", "No image loaded.")


def quit_app():
    root.quit()


def copy_action():
    global clipboard_image, current_image
    if current_image:
        clipboard_image = current_image.copy()
        messagebox.showinfo("Copy", "Image copied to clipboard buffer.")
    else:
        messagebox.showwarning("Copy", "No image to copy.")


def paste_action():
    global clipboard_image, current_image
    if clipboard_image:
        current_image = clipboard_image.copy()
        display_image(current_image)
        messagebox.showinfo("Paste", "Image pasted from clipboard buffer.")
    else:
        messagebox.showwarning("Paste", "Clipboard is empty.")


def cut_action():
    global clipboard_image, current_image
    if current_image:
        clipboard_image = current_image.copy()
        current_image = None
        canvas.delete("all")
        messagebox.showinfo("Cut", "Image cut and stored in clipboard buffer.")
    else:
        messagebox.showwarning("Cut", "No image to cut.")


def display_image(img):
    """Resize and display image on canvas"""
    global current_image_tk
    canvas.delete("all")
    # Scale image to fit window
    w, h = canvas.winfo_width(), canvas.winfo_height()
    img_resized = img.copy()
    img_resized.thumbnail((w, h))
    current_image_tk = ImageTk.PhotoImage(img_resized)
    canvas.create_image(w//2, h//2, image=current_image_tk, anchor="center")


# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("Pictureroom - Python Tkinter")
root.geometry("1000x700")

# Menu bar
menu_bar = tk.Menu(root)

# File Menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_as_file)
file_menu.add_separator()
file_menu.add_command(label="Properties", command=show_properties)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=quit_app)
menu_bar.add_cascade(label="File", menu=file_menu)

# Clipboard Menu
clipboard_menu = tk.Menu(menu_bar, tearoff=0)
clipboard_menu.add_command(label="Copy", command=copy_action)
clipboard_menu.add_command(label="Paste", command=paste_action)
clipboard_menu.add_command(label="Cut", command=cut_action)
menu_bar.add_cascade(label="Clipboard", menu=clipboard_menu)

# Attach menu bar to window
root.config(menu=menu_bar)

# Canvas for image display
canvas = tk.Canvas(root, bg="black")
canvas.pack(fill=tk.BOTH, expand=True)

# Update display when window resizes
canvas.bind("<Configure>", lambda event: display_image(current_image) if current_image else None)

root.mainloop()
