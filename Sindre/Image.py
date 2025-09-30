import cv2


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

if __name__ == "__main__":
    image = cv2.imread("img.png", cv2.IMREAD_UNCHANGED)
    flipVertical(image)