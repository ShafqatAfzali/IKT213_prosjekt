from tkinter import Frame, Label, Scale, BOTH, RIGHT, HORIZONTAL, IntVar, Checkbutton, Scrollbar, Y, Canvas
from classes.state import State
from helpers.image_render import update_display_image
from menues.preset_menu import create_preset_menu


def create_adjustment_menu(state: State, menu_bar):
    panel_width = 250

    def toggle_adjustment_panel():
        if hasattr(state, "adjustment_panel") and state.adjustment_panel.winfo_exists():
            state.adjustment_panel.destroy()
            delattr(state, "adjustment_panel")
            return

        adjustment_panel = Frame(state.main_frame, bg="#222", width=panel_width)
        # noinspection PyTypeChecker
        adjustment_panel.pack(side=RIGHT, fill=BOTH)
        state.adjustment_panel = adjustment_panel

        canvas_inside_adjustment_panel = Canvas(adjustment_panel, bg="#222", width=panel_width, highlightthickness=0)
        canvas_inside_adjustment_panel.pack(side="left", fill=Y)

        scrollbar = Scrollbar(adjustment_panel, orient="vertical", command=canvas_inside_adjustment_panel.yview)
        scrollbar.pack(side="right", fill=Y)
        canvas_inside_adjustment_panel.configure(yscrollcommand=scrollbar.set)

        inner_frame = Frame(canvas_inside_adjustment_panel, bg="#222")
        window_id = canvas_inside_adjustment_panel.create_window((0, 0), window=inner_frame, anchor="nw")

        def resize_inner_frame(event):
            canvas_inside_adjustment_panel.itemconfig(window_id, width=event.width)

        canvas_inside_adjustment_panel.bind("<Configure>", resize_inner_frame)

        def on_configure(event):
            canvas_inside_adjustment_panel.configure(scrollregion=canvas_inside_adjustment_panel.bbox("all"))
        inner_frame.bind("<Configure>", on_configure)

        def _on_mousewheel(event):
            canvas_inside_adjustment_panel.yview_scroll(-int(event.delta / 120), "units")

        canvas_inside_adjustment_panel.bind_all("<MouseWheel>", _on_mousewheel)

        def add_slider(label, key, min_val, max_val, resolution=1.0):
            def start_preview(key):
                state.preview_values = state.adjustment_values.copy()

            def on_drag(value, key):
                if state.preview_values is None:
                    return
                state.preview_values[key] = type(state.adjustment_values[key])(value)
                update_display_image(state)

            def set_adjustment_value(image, value, key):
                state.adjustment_values[key] = value
                return image

            def on_release(key):
                value = state.preview_values[key]
                state.operations.append((set_adjustment_value, [value, key], {}))
                state.preview_values = None
                state.redo_stack.clear()
                update_display_image(state)


            Label(inner_frame, text=label, bg="#2b2b2b", fg="white").pack()
            # noinspection PyTypeChecker
            slider = Scale(
                inner_frame,
                from_=min_val,
                to=max_val,
                resolution=resolution,
                orient=HORIZONTAL,
                command=lambda v: on_drag(v, key),
            )
            slider.set(state.adjustment_values[key])
            slider.pack(fill="x")
            slider.bind("<ButtonPress-1>", lambda e, k=key: start_preview(k))
            slider.bind("<ButtonRelease-1>", lambda e: on_release(key))

            return key, slider

        def add_toggle(label, key):
            var = IntVar(value=True if state.adjustment_values.get(key, False) else False)

            def on_toggle():
                state.adjustment_values[key] = var.get()
                update_display_image(state)

            toggle = Checkbutton(
                inner_frame,
                text=label,
                variable=var,
                command=on_toggle,
                bg="#2b2b2b",
                fg="white",
                selectcolor="#444"
            )
            toggle.pack(anchor="w")

            return key, var

        # Add sliders
        sliders = dict([
            add_slider("Brightness", "brightness", -100, 100, 1),
            add_slider("Contrast", "contrast", 0.5, 2.0, 0.1),
            add_slider("Saturation", "saturation", 0.0, 2.0, 0.1),
            add_slider("Exposure", "exposure", 0.5, 2.0, 0.1),
            add_slider("r_gain", "r_gain", 0.5, 2.5, 0.01),
            add_slider("b_gain", "b_gain", 0.5, 2.5, 0.01),
            add_slider("g_gain", "g_gain", 0.5, 2.5, 0.01),
            add_slider("Tone curve strength", "tone_curve_strength", -1.0, 1.0, 0.01),
            add_slider("Vignette strength", "vignette_strength", 0.0, 1.0, 0.01),
        ])

        # Add toggle buttons
        toggle_buttons = dict([
        add_toggle("Grayscale", "grayscale"),
        ])



        create_preset_menu(state, inner_frame, sliders, toggle_buttons)

    menu_bar.add_command(label="Adjustment", command=toggle_adjustment_panel)
