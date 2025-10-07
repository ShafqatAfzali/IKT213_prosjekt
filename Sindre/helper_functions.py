import cv2
from PIL import Image, ImageTk


def cv2_to_tk(cv_img):
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cv_img_rgb)
    return ImageTk.PhotoImage(pil_img)


def display_image(state):
    state.canvas.delete("all")
    w, h = state.canvas.winfo_width(), state.canvas.winfo_height()
    state.cv_image_display = state.cv_image_full.copy()
    cv_img_rgb = cv2.cvtColor(state.cv_image_display, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cv_img_rgb)
    pil_img.thumbnail((w, h))
    state.tk_image = ImageTk.PhotoImage(pil_img)
    state.canvas.create_image(w // 2, h // 2, image=state.tk_image, anchor="center")

def rotate90DegreeClockwise(image):
    rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return rotated

def rotate90DegreeCounterClockwise(image):
    rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return rotated

def flipVertical(image):
    flipped = cv2.flip(image, 0)
    return flipped

def flipHorizontal(image):
    flipped = cv2.flip(image, 1)
    return flipped