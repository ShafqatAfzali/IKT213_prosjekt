from tkinter import *

#sys.path.append(os.path.join(os.path.dirname(__file__), 'shafqat'))
#sys.path.append(os.path.join(os.path.dirname(__file__), 'Erling'))

from shafqat.shapes import create_shapes_menu
from Erling.main_menyer import create_main_menu


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