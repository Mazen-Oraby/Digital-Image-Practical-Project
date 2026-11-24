"""Reference-based image quality metrics."""

import cv2
import numpy as np


def calculate_metrics(reference, result):
    """Return MSE and PSNR; caller must supply a meaningful clean reference."""
    if reference.shape != result.shape:
        raise ValueError("Images must have identical dimensions and channels.")
    first = reference.astype(np.float64)
    second = result.astype(np.float64)
    mse = float(np.mean((first - second) ** 2))
    psnr = float("inf") if mse == 0 else float(10 * np.log10((255.0 ** 2) / mse))
    return {"mse": mse, "psnr": psnr}


def grayscale(image):
    return image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
