class Selection:
    def __init__(self):
        self.points = []
        self.shape_ids = []
        self.to_mouse_shape = None
        self.mask = None

    def reset_variables(self):
        self.points = []
        self.shape_ids = []
        self.to_mouse_shape = None
        self.mask = None