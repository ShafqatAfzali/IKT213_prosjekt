import cv2
from PIL import ImageTk, Image


def cv2_to_tk(cv_img):
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cv_img_rgb)
    return ImageTk.PhotoImage(pil_img)