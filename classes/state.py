from tkinter import StringVar, IntVar


class State:
    def __init__(self):
        self.main_window = None
        self.canvas = None

        self.current_file_path = None
        self.cv_image_full = None
        self.cv_image_display = None
        self.tk_image = None

        # TODO: Move
        self.selection_points = []
        self.selection_shape_ids = []


        self.selection_mask = None

        self.brush_size = 5
        self.brush_color = (255, 0, 0)

        self.clipboard_image = None