import cv2


def rotate_90_degree_clockwise(image):
    rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return rotated

def rotate_90_degree_counter_clockwise(image):
    rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return rotated

def flip_vertical(image):
    flipped = cv2.flip(image, 0)
    return flipped

def flip_horizontal(image):
    flipped = cv2.flip(image, 1)
    return flipped