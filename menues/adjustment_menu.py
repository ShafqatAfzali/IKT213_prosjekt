from tkinter import Menu, Scale, Toplevel
from classes.state import State
from helpers.image_render import update_display_image


def create_adjustment_menu(state: State, menu_bar):
    def on_brightness_drag(value):
        state.preview_adjust = True
        state.preview_brightness_value = int(value)
        update_display_image(state)

    def set_brightness(image, value):
        state.brightness_value = value
        return image

    def on_brightness_slider_release():
        state.preview_adjust = False
        state.operations.append((set_brightness, [state.preview_brightness_value], {}))
        state.redo_stack.clear()
        update_display_image(state)

    def open_brightness_window():
        state.preview_brightness_value = state.brightness_value
        win = Toplevel(state.main_window)
        win.title("Brightness")
        slider = Scale(win, from_=-100, to=100, orient="horizontal",command=lambda v: on_brightness_drag(v))
        slider.set(state.brightness_value)
        slider.pack()
        slider.bind("<ButtonRelease-1>", lambda e: on_brightness_slider_release())


    def on_contrast_drag(value):
        state.preview_adjust = True
        state.preview_contrast_value = float(value)
        update_display_image(state)

    def set_contrast(image, value):
        state.contrast_value = value
        return image

    def on_contrast_slider_release():
        state.preview_adjust = False
        state.operations.append((set_contrast, [state.preview_contrast_value], {}))
        state.redo_stack.clear()
        update_display_image(state)

    def open_contrast_window():
        win = Toplevel(state.main_window)
        win.title("Contrast")
        slider = Scale(win, from_=0.5, to=2.0, resolution=0.1, orient='horizontal', command=on_contrast_drag)
        slider.set(state.contrast_value)
        slider.pack()
        slider.bind("<ButtonRelease-1>", lambda e: on_contrast_slider_release())

    def on_saturation_drag(value):
        state.preview_adjust = True
        state.preview_saturation_value = float(value)
        update_display_image(state)

    def set_saturation(image, value):
        state.saturation_value = float(value)
        return image

    def on_saturation_slider_release():
        state.preview_adjust = False
        state.operations.append((set_saturation, [state.preview_saturation_value], {}))
        state.redo_stack.clear()
        update_display_image(state)

    def open_saturation_window():
        win = Toplevel(state.main_window)
        win.title("saturation")
        slider = Scale(win, from_=0.0, to=2.0, resolution=0.1, orient='horizontal', command=on_saturation_drag)
        slider.set(state.saturation_value)
        slider.pack()
        slider.bind("<ButtonRelease-1>", lambda e: on_saturation_slider_release())

    def on_exposure_drag(value):
        state.preview_adjust = True
        state.preview_exposure_value = float(value)
        update_display_image(state)

    def set_exposure(image, value):
        state.exposure_value = float(value)
        return image

    def on_exposure_slider_release():
        state.preview_adjust = False
        state.operations.append((set_exposure, [state.preview_exposure_value], {}))
        state.redo_stack.clear()
        update_display_image(state)

    def open_exposure_window():
        win = Toplevel(state.main_window)
        win.title("exposure")
        slider = Scale(win, from_=0.5, to=2.0, resolution=0.1, orient='horizontal', command=on_exposure_drag)
        slider.set(state.exposure_value)
        slider.pack()
        slider.bind("<ButtonRelease-1>", lambda e: on_exposure_slider_release())

    def on_white_balance_drag(value):
        state.preview_adjust = True
        state.preview_white_balance_value = int(value)
        update_display_image(state)

    def set_white_balance(image, value):
        state.white_balance_value = int(value)
        return image

    def on_white_balance_slider_release():
        state.preview_adjust = False
        state.operations.append((set_white_balance, [state.preview_white_balance_value], {}))
        state.redo_stack.clear()
        update_display_image(state)

    def open_white_balance_window():
        win = Toplevel(state.main_window)
        win.title("white_balance")
        slider = Scale(win, from_=-100, to=100, orient='horizontal', command=on_white_balance_drag)
        slider.set(state.white_balance_value)
        slider.pack()
        slider.bind("<ButtonRelease-1>", lambda e: on_white_balance_slider_release())



    adjustment_menu = Menu(menu_bar, tearoff=0)
    adjustment_menu.add_command(label="Brightness", command=open_brightness_window)
    adjustment_menu.add_command(label="Contrast", command=open_contrast_window)
    adjustment_menu.add_command(label="Saturation", command=open_saturation_window)
    adjustment_menu.add_command(label="Exposure", command=open_exposure_window)
    adjustment_menu.add_command(label="White balance", command=open_white_balance_window)
    menu_bar.add_cascade(label="Adjustment", menu=adjustment_menu)