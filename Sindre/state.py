class State:
    def __init__(self):
        self.cv_image_full = None
        self.cv_image_display = None
        self.canvas = None
        self.tk_image = None
        self.selection_points = []
        self.selection_shape_ids = []
        self.selection_mask = None
        self.main_window = None
        self.current_file_path = None
        self.clipboard_image = None