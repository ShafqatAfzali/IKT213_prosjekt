class State:
    def __init__(self):
        self.main_window = None
        self.canvas = None

        self.current_file_path = None
        self.original_image = None
        self.cv_image_full = None
        self.cv_image_display = None # TODO: Save w,h instead?
        self.tk_image = None

        self.operations = [] # (func, args, kwargs)

        # TODO: Move
        self.selection_points = []
        self.selection_shape_ids = []


        self.selection_mask = None

        self.brush_size = 5
        self.brush_color = (255, 0, 0)

        self.clipboard_image = None