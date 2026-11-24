"""Low-pass spatial filters used for smoothing and noise reduction."""

import cv2


def apply_low_pass(image, algorithm, kernel_size=3, sigma=1.0):
    if kernel_size not in (3, 5, 7):
        raise ValueError("Kernel size must be 3, 5, or 7.")
    if algorithm == "Average Filter":
        return cv2.blur(image, (kernel_size, kernel_size))
    if algorithm == "Gaussian Low-Pass":
        if sigma <= 0:
            raise ValueError("Gaussian sigma must be greater than zero.")
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
    if algorithm == "Median Filter":
        return cv2.medianBlur(image, kernel_size)
    raise ValueError("Unknown low-pass algorithm: {}".format(algorithm))
