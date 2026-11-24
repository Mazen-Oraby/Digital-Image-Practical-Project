"""Conversions between OpenCV arrays and Pillow display images."""

import cv2
from PIL import Image


def to_pillow(image):
    if image.ndim == 2:
        return Image.fromarray(image)
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
