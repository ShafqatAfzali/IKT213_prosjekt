class State:
    def __init__(self):
        # tkinter references
        self.main_window = None
        self.canvas = None

        # Image references
        self.current_file_path = None
        self.original_image = None              # CV2 original image, don't change unless loading an image
        self.cv_image_full = None               # Image that all edits happen to
        self.cached_images = {}                 # A dict with cached images for faster render pipline
        self.cv_image_display = None            # cv_image_full but resized to fit the canvas. To be swaped with w,h?
        self.tk_image = None                    # Image that is displayed in tkinter. To be removed

        self.operations = []                    # (func, args, kwargs), for undo
        self.redo_stack = []                    # (func, args, kwargs), for redo

        self.preview_brush_mask = None          # Used to store mask for previewing brushstrokes before adding to operations

        self.shape_points = []                  # List of points used for making selection mask, saved as coordinates on cv_image_full
        self.shape_ids = []                     # shape_id of all the lines making up the selection area
        self.selection_mask = None              # A black white mask with a white area corresponding to the selection area

        self.brush_size = 5
        self.brush_color = (255, 0, 0)          # Color in rgb format

        self.clipboard_image = None

        # zoom
        self.zoom = 1.0  # 1 = 100%
        self.zoom_offset_x = 0
        self.zoom_offset_y = 0
        self.min_zoom = 0.25
        self.max_zoom = 8.0
        self.pan_start = None

        self.cropping = False
        self.crop_metadata = None  # dict with {'x0': ..., 'y0': ..., 'x1': ..., 'y1': ...}

        self.preview_adjust = False
        self.adjustment_values = { # dict for adjustment values
            "brightness": 0,
            "contrast": 1.0,
            "saturation": 1.0,
            "exposure": 1.0,
            "white_balance": 0,
        }
        self.preview_values = self.adjustment_values.copy()     # dict for preview adjustment values