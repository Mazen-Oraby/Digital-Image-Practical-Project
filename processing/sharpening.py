"""Spatial high-pass and Laplacian sharpening filters."""

import cv2
import numpy as np


LAPLACIAN_KERNEL = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
HIGH_PASS_KERNEL = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)


def apply_sharpening(image, algorithm, strength=1.0):
    if not 0 <= strength <= 3:
        raise ValueError("Sharpening strength must be between 0 and 3.")
    source = image.astype(np.float32)
    if algorithm == "Laplacian Sharpening":
        response = cv2.filter2D(source, cv2.CV_32F, LAPLACIAN_KERNEL)
        result = source - strength * response
    elif algorithm == "High-Pass Sharpening":
        response = cv2.filter2D(source, cv2.CV_32F, HIGH_PASS_KERNEL)
        result = source + strength * (response - source)
    else:
        raise ValueError("Unknown sharpening algorithm: {}".format(algorithm))
    return np.clip(result, 0, 255).astype(np.uint8)
