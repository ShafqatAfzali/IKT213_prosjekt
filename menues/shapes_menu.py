import tkinter as tk
from tkinter import colorchooser, simpledialog
from helpers.image_render import update_display_image
from helpers.cord_utils import canvas_to_full_image_cords

import cv2
import numpy as np

from classes.state import State

# Global variables for shapes functionality
current_shape_type = "rectangle"
outline_color = "red"
fill_color = ""
line_width = 2
current_shape = None
start_x = 0
start_y = 0

# Available shapes
available_shapes = ["rectangle", "oval", "line", "triangle"]



def create_shapes_menu(state: State, menu_bar):
    def set_shape_type(shape_type):
        """Set the current shape type to draw"""
        global current_shape_type, current_shape
        current_shape_type = shape_type
        # Reset current drawing if switching shapes
        if current_shape:
            state.canvas.delete(current_shape)
            current_shape = None

    def set_outline_color():
        """Open color chooser for outline color"""
        global outline_color
        color = colorchooser.askcolor(title="Choose Outline Color", initialcolor=outline_color)
        if color[1]:  # If a color was chosen
            outline_color = color[1]

    def set_fill_color():
        """Open color chooser for fill color"""
        global fill_color
        color = colorchooser.askcolor(title="Choose Fill Color", initialcolor=fill_color)
        if color[1]:  # If a color was chosen
            fill_color = color[1]

    def set_line_width():
        """Set line width for shapes"""
        global line_width
        width = simpledialog.askinteger("Line Width", "Enter line width:",
                                        initialvalue=line_width, minvalue=1, maxvalue=10)
        if width:
            line_width = width

    # TODO: draw shape to mask instead?
    def start_drawing(event):
        """Start drawing a shape"""
        global start_x, start_y, current_shape

        start_x = event.x
        start_y = event.y

        if current_shape_type == "rectangle":
            current_shape = state.canvas.create_rectangle(
                start_x, start_y, start_x, start_y,
                outline=outline_color, fill=fill_color, width=line_width
            )
        elif current_shape_type == "oval":
            current_shape = state.canvas.create_oval(
                start_x, start_y, start_x, start_y,
                outline=outline_color, fill=fill_color, width=line_width
            )
        elif current_shape_type == "line":
            current_shape = state.canvas.create_line(
                start_x, start_y, start_x, start_y,
                fill=outline_color, width=line_width
            )
        elif current_shape_type == "triangle":
            current_shape = state.canvas.create_polygon(
                start_x, start_y, start_x, start_y, start_x, start_y,
                outline=outline_color, fill=fill_color, width=line_width
            )

    def update_drawing(event):
        """Update the shape being drawn"""
        global current_shape

        if not current_shape:
            return

        if current_shape_type in ["rectangle", "oval"]:
            state.canvas.coords(current_shape, start_x, start_y, event.x, event.y)
        elif current_shape_type == "line":
            state.canvas.coords(current_shape, start_x, start_y, event.x, event.y)
        elif current_shape_type == "triangle":
            # Calculate triangle points
            mid_x = (start_x + event.x) / 2
            state.canvas.coords(current_shape,
                          start_x, event.y,  # bottom left
                          mid_x, start_y,  # top center
                          event.x, event.y  # bottom right
                          )

    # TODO: shapes move slightly when placed
    def finish_drawing(event):
        """Finish drawing the shape"""
        global current_shape

        if current_shape is None:
            return


        # get final coordinates from canvas
        coords = state.canvas.coords(current_shape)
        [(x1, y1), (x2, y2)] = canvas_to_full_image_cords(state, [(coords[0], coords[1]), (coords[2], coords[3])])
        coords = [x1,y1,x2,y2]

        def color_to_bgr(color):
            if not color:
                return None
            # Tkinter color names
            try:
                rgb = state.canvas.winfo_rgb(color)
                return (rgb)
            except Exception:
                return None

        def draw_shape(image, shape_type, coords, outline, fill, width):
            result = image.copy()
            bgr_outline = color_to_bgr(outline)
            bgr_fill = color_to_bgr(fill)

            if shape_type == "rectangle":
                x1, y1, x2, y2 = map(int, coords)
                cv2.rectangle(result, (x1, y1), (x2, y2), bgr_outline[::-1], width)
            elif shape_type == "oval":
                x1, y1, x2, y2 = map(int, coords)
                center = ((x1 + x2) // 2, (y1 + y2) // 2)
                axes = ((x2 - x1) // 2, (y2 - y1) // 2)
                cv2.ellipse(result, center, axes, 0, 0, 360, bgr_outline[::-1], width)
            elif shape_type == "line":
                x1, y1, x2, y2 = map(int, coords)
                cv2.line(result, (x1, y1), (x2, y2), bgr_outline[::-1], width)
            elif shape_type == "triangle":
                pts = np.array(coords, np.int32).reshape((-1, 1, 2))
                cv2.polylines(result, [pts], isClosed=True, color=bgr_outline[::-1], thickness=width)
                if bgr_fill:
                    cv2.fillPoly(result, [pts], bgr_fill[::-1])
            return result

        state.operations.append(
            (
                draw_shape,
                [],  # no positional args
                {
                    "shape_type": current_shape_type,
                    "coords": coords,
                    "outline": outline_color,
                    "fill": fill_color,
                    "width": line_width
                }
            )
        )

        state.canvas.delete(current_shape)
        current_shape = None

        state.redo_stack.clear()
        update_display_image(state)


    def enable_shape_drawing():
        """Enable shape drawing on the state.canvas"""
        # Bind mouse events for drawing
        state.canvas.bind("<Button-1>", start_drawing)
        state.canvas.bind("<B1-Motion>", update_drawing)
        state.canvas.bind("<ButtonRelease-1>", finish_drawing)

    def disable_shape_drawing():
        """Disable shape drawing on the state.canvas"""
        state.canvas.unbind("<Button-1>")
        state.canvas.unbind("<B1-Motion>")
        state.canvas.unbind("<ButtonRelease-1>")
    
    shapes_menu = tk.Menu(menu_bar, tearoff=0)
    
    # List of Shapes submenu
    shapes_list_menu = tk.Menu(shapes_menu, tearoff=0)
    for shape in available_shapes:
        shapes_list_menu.add_command(
            label=shape.capitalize(),
            command=lambda s=shape: set_shape_type(s)
        )
    shapes_menu.add_cascade(label="List of Shapes", menu=shapes_list_menu)
    
    # Outline color
    shapes_menu.add_command(label="Outline Color", command=set_outline_color)
    
    # Fill color
    shapes_menu.add_command(label="Fill Color", command=set_fill_color)
    
    # Line width
    shapes_menu.add_command(label="Line Width", command=set_line_width)
    
    # Enable/disable drawing
    shapes_menu.add_separator()
    shapes_menu.add_command(
        label="Enable Drawing", 
        command=lambda: enable_shape_drawing()
    )
    shapes_menu.add_command(
        label="Disable Drawing", 
        command=disable_shape_drawing
    )
    
    # Automatically add to menu bar
    menu_bar.add_cascade(label="Shapes", menu=shapes_menu)