from tkinter import *
from tkinter import colorchooser

def create_colors_menu(menu_bar, canvas):
    colors_menu = Menu(menu_bar, tearoff=0)

    # Variabel for valgt farge og penselstørrelse
    brush_color = StringVar(value="black")
    brush_size = IntVar(value=5)

    # Funksjon for å velge farge fra palett
    def choose_color():
        color = colorchooser.askcolor(title="Velg farge")[1]
        if color:
            brush_color.set(color)

    # Funksjon for å endre penselstørrelse
    def set_brush_size(size):
        brush_size.set(size)

    # Her legger vi menyvalg
    colors_menu.add_command(label="Velg farge", command=choose_color)

    # Legger til undermeny for penselstørrelse
    size_menu = Menu(colors_menu, tearoff=0)
    for size in [2, 5, 10, 15, 20, 30]:
        size_menu.add_radiobutton(label=f"{size}px", command=lambda s=size: set_brush_size(s))

    colors_menu.add_cascade(label="Penselstørrelse", menu=size_menu)

    # Legger fargen inn i canvas for tegning (hvis dere bruker brush senere)
    canvas.brush_color = brush_color
    canvas.brush_size = brush_size

    # Legg til menyen i hovedmenyen
    menu_bar.add_cascade(label="Colors", menu=colors_menu)
