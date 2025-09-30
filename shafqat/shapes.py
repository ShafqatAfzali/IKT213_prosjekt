import tkinter as tk
from tkinter import colorchooser, simpledialog

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

def set_shape_type(shape_type):
    """Set the current shape type to draw"""
    global current_shape_type, current_shape
    current_shape_type = shape_type
    # Reset current drawing if switching shapes
    if current_shape:
        canvas.delete(current_shape)
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

def start_drawing(event):
    """Start drawing a shape"""
    global start_x, start_y, current_shape
    
    start_x = event.x
    start_y = event.y
    
    if current_shape_type == "rectangle":
        current_shape = canvas.create_rectangle(
            start_x, start_y, start_x, start_y,
            outline=outline_color, fill=fill_color, width=line_width
        )
    elif current_shape_type == "oval":
        current_shape = canvas.create_oval(
            start_x, start_y, start_x, start_y,
            outline=outline_color, fill=fill_color, width=line_width
        )
    elif current_shape_type == "line":
        current_shape = canvas.create_line(
            start_x, start_y, start_x, start_y,
            fill=outline_color, width=line_width
        )
    elif current_shape_type == "triangle":
        current_shape = canvas.create_polygon(
            start_x, start_y, start_x, start_y, start_x, start_y,
            outline=outline_color, fill=fill_color, width=line_width
        )

def update_drawing(event):
    """Update the shape being drawn"""
    global current_shape
    
    if not current_shape:
        return
        
    if current_shape_type in ["rectangle", "oval"]:
        canvas.coords(current_shape, start_x, start_y, event.x, event.y)
    elif current_shape_type == "line":
        canvas.coords(current_shape, start_x, start_y, event.x, event.y)
    elif current_shape_type == "triangle":
        # Calculate triangle points
        mid_x = (start_x + event.x) / 2
        canvas.coords(current_shape,
                     start_x, event.y,  # bottom left
                     mid_x, start_y,    # top center  
                     event.x, event.y   # bottom right
        )

def finish_drawing(event):
    """Finish drawing the shape"""
    global current_shape
    current_shape = None

def enable_shape_drawing(canvas_widget):
    """Enable shape drawing on the canvas"""
    global canvas
    canvas = canvas_widget
    
    # Bind mouse events for drawing
    canvas.bind("<Button-1>", start_drawing)
    canvas.bind("<B1-Motion>", update_drawing)
    canvas.bind("<ButtonRelease-1>", finish_drawing)

def disable_shape_drawing():
    """Disable shape drawing on the canvas"""
    canvas.unbind("<Button-1>")
    canvas.unbind("<B1-Motion>")
    canvas.unbind("<ButtonRelease-1>")

def create_shapes_menu(menu_bar, canvas_widget):
    """Create the Shapes menu and add it to the menu bar"""
    global canvas
    canvas = canvas_widget
    
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
        command=lambda: enable_shape_drawing(canvas)
    )
    shapes_menu.add_command(
        label="Disable Drawing", 
        command=disable_shape_drawing
    )
    
    # Automatically add to menu bar
    menu_bar.add_cascade(label="Shapes", menu=shapes_menu)