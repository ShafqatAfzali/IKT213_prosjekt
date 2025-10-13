class State:
    def __init__(self):
        # tkinter references
        self.main_window = None
        self.canvas = None

        self.current_file_path = None
        self.original_image = None              # --- original image, don't change unless loading an image
        self.cv_image_full = None               # Image that all edits happen to
        self.cached_images = {}                 # A dict with cached images for faster render pipline
        self.cv_image_display = None            # cv_image_full but resized to fit the canvas. To be swaped with w,h?
        self.tk_image = None                    # Image that is displayed in tkinter. To be removed

        self.operations = []                    # (func, args, kwargs), for undo
        self.redo_stack = []                    # (func, args, kwargs), for redo

        self.preview_brush_mask = None          # Used to store mask for previewing brushstrokes before adding to operations

        self.selection_points = []              # List of points used for making selection mask, saved as coordinates on cv_image_full
        self.selection_shape_ids = []           # shape_id of all the lines making up the selection area
        self.selection_mask = None              # A black white mask with a white area corresponding to the selection area

        self.brush_size = 5
        self.brush_color = (255, 0, 0)          # Color in rgb format

        self.clipboard_image = None