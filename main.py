from tkinter import *
from PIL import Image, ImageTk

#for å håndtere funksjon import fra hver av filene
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'shafqat'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Erling'))

#importerer create_shapes_menu fra shafqat folder som lager shapes funkjsoner i menu bar
from shapes import create_shapes_menu
#importerer create_shapes_menu fra shafqat folder som lager main meny funksjoner i menu bar
from main_menyer import create_main_menu  


#lager pop up window
main_window = Tk()
main_window.title("IKT213 Photo looksmaxer")
main_window.geometry("600x600")
main_window.configure(background="black")

#lager frame inni windowet
main_frame = Frame(main_window, bg="black")
main_frame.pack(fill=BOTH, expand=YES)


#lager menu bar inni frame, denne skal inneholde alle "options" for edditing
menu_bar = Menu(main_window)

#lager canvas for tegning denne inneholder lastet opp bildet,
#det blir tegnet på canvas som vil si på bildet
#når man "saver" blir canvas savet som bildet
canvas = Canvas(main_frame, bg="black")
canvas.pack(fill=BOTH, expand=YES)

# legger til main meny i menu bar
create_main_menu(menu_bar, canvas, main_window)

# legger til shapes meny i menu bar
create_shapes_menu(menu_bar, canvas)

# bruker min menu bare i root
main_window.config(menu=menu_bar)

main_window.mainloop()

'''
#loader sindre sin bildet
image = Image.open("Sindre/img.png")
img_copy = image.copy()

def resize_image(event):
    new_width = event.width
    new_height = event.height
    
    resized_image = img_copy.resize((new_width, new_height))
    background_image = ImageTk.PhotoImage(resized_image)
    
    # Update canvas with the image
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=background_image)
    canvas.background = background_image  # Keep a reference

# Bind resize event to canvas
canvas.bind('<Configure>', resize_image)

# Initial display of image
def show_initial_image():
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    if width > 1 and height > 1:  # Make sure canvas has valid dimensions
        resized_image = img_copy.resize((width, height))
        background_image = ImageTk.PhotoImage(resized_image)
        canvas.create_image(0, 0, anchor="nw", image=background_image)
        canvas.background = background_image  # Keep a reference

# Schedule initial image display after window is fully loaded
main_window.after(100, show_initial_image)
'''

