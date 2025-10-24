import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2

from classes.state import State
from helpers.image_render import update_display_image
from helpers.menu_utils import add_menu_command_with_hotkey


def create_main_menu(state: State, menu_bar):
    def new_file():
        state.cv_image_full = None
        state.current_image_tk = None
        state.current_file_path = None
        state.canvas.delete("all")
        messagebox.showinfo("New File", "Started a new workspace.")

    def open_file():
        file_path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=(("Image Files", "*.jpg;*.jpeg;*.png;*.gif"), ("All Files", "*.*"))
        )
        if file_path:
            state.preview_brush_mask = None
            state.current_file_path = file_path
            state.original_image = cv2.imread(file_path)
            state.cv_image_full = state.original_image.copy()
            load_metadata(file_path)
            state.operations.clear()
            state.redo_stack.clear()
            update_display_image(state, new_image=True)

    def save_file():
        if state.current_file_path and state.cv_image_full is not None:
            cv2.imwrite(state.current_file_path, state.cv_image_full)
            save_metadata(state.current_file_path)
            messagebox.showinfo("Save", f"File saved: {state.current_file_path}")
        else:
            save_as_file()

    def save_as_file():
        if state.cv_image_full is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*"))
            )
            if file_path:
                state.current_file_path = file_path
                cv2.imwrite(state.current_file_path, state.cv_image_full)
                save_metadata(state.current_file_path)
                messagebox.showinfo("Save As", f"File saved as: {file_path}")

    def save_metadata(image_path):
        meta = {'crop': state.crop_metadata}
        with open(os.path.splitext(image_path)[0] + ".json", "w") as f:
            json.dump(meta, f)

    def load_metadata(image_path):
        meta_path = os.path.splitext(image_path)[0] + ".json"
        if os.path.exists(meta_path):
            state.crop_metadata = json.load(open(meta_path)).get("crop")

    def show_properties():
        if state.cv_image_full is not None:
            h, w = state.cv_image_full.shape[:2]

            if len(state.cv_image_full.shape) == 2:
                mode = "L"
            elif state.cv_image_full.shape[2] == 3:
                mode = "RGB"
            elif state.cv_image_full.shape[2] == 4:
                mode = "RGBA"
            else:
                mode = "Unknown"

            props = f"File: {state.current_file_path}\nSize: ({w}, {h})\nMode: {mode}"

            messagebox.showinfo("Properties", props)

        else:
            messagebox.showwarning("Properties", "No image loaded.")


    def undo():
        if not state.operations:
            return
        op_idx = len(state.operations) - 1
        operation = state.operations.pop()
        state.redo_stack.append(operation)

        if operation[0].__name__ == "apply_crop":
            state.crop_metadata = None
        elif operation[0].__name__ == "adjust_brightness":
            prev_value = 0
            for op in reversed(state.operations):
                if op[0].__name__ == "adjust_brightness":
                    prev_value = op[1][0]
                    break
            state.brightness_value = prev_value
        elif operation[0].__name__ == "adjust_contrast":
            prev_value = 0
            for op in reversed(state.operations):
                if op[0].__name__ == "adjust_contrast":
                    prev_value = op[1][0]
                    break
            state.contrast_value = prev_value

        if op_idx in state.cached_images:
            del state.cached_images[op_idx]

        update_display_image(state)

    def redo():
        if not state.redo_stack:
            return
        state.operations.append(state.redo_stack.pop())
        update_display_image(state)


    def copy_action():
        if state.cv_image_full:
            state.clipboard_image = state.cv_image_full.copy()
            messagebox.showinfo("Copy", "Image copied to clipboard buffer.")
        else:
            messagebox.showwarning("Copy", "No image to copy.")

    def paste_action():
        if state.clipboard_image:
            state.cv_image_full = state.clipboard_image.copy()
            state.redo_stack.clear()
            update_display_image(state)
            messagebox.showinfo("Paste", "Image pasted from clipboard buffer.")
        else:
            messagebox.showwarning("Paste", "Clipboard is empty.")

    def cut_action():
        if state.cv_image_full:
            state.clipboard_image = state.cv_image_full.copy()
            state.cv_image_full = None
            state.canvas.delete("all")
            messagebox.showinfo("Cut", "Image cut and stored in clipboard buffer.")
        else:
            messagebox.showwarning("Cut", "No image to cut.")
    
    # File Menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="New", command=new_file)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_command(label="Save As", command=save_as_file)
    file_menu.add_separator()
    add_menu_command_with_hotkey(state, file_menu, "Undo", undo, "Control+z")
    add_menu_command_with_hotkey(state, file_menu, "Redo", redo, "Control+y")
    file_menu.add_separator()
    file_menu.add_command(label="Properties", command=show_properties)
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=state.main_window.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    
    # Clipboard Menu
    clipboard_menu = tk.Menu(menu_bar, tearoff=0)
    clipboard_menu.add_command(label="Copy", command=copy_action)
    clipboard_menu.add_command(label="Paste", command=paste_action)
    clipboard_menu.add_command(label="Cut", command=cut_action)
    menu_bar.add_cascade(label="Clipboard", menu=clipboard_menu)

    return menu_bar

