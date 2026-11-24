"""Directional and second-order spatial-domain edge detectors."""

import cv2
import numpy as np


ROBERTS_X = np.array([[1, 0], [0, -1]], dtype=np.float32)
ROBERTS_Y = np.array([[0, 1], [-1, 0]], dtype=np.float32)
PREWITT_X = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
PREWITT_Y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
KIRSCH_KERNELS = [
    np.array(mask, dtype=np.float32)
    for mask in (
        [[5, 5, 5], [-3, 0, -3], [-3, -3, -3]],
        [[5, 5, -3], [5, 0, -3], [-3, -3, -3]],
        [[5, -3, -3], [5, 0, -3], [5, -3, -3]],
        [[-3, -3, -3], [5, 0, -3], [5, 5, -3]],
        [[-3, -3, -3], [-3, 0, -3], [5, 5, 5]],
        [[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]],
        [[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]],
        [[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]],
    )
]
LAPLACIAN_KERNEL = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)


def _gray(image):
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def _magnitude(gx, gy):
    return cv2.convertScaleAbs(cv2.magnitude(gx.astype(np.float32), gy.astype(np.float32)))


def _normalize(response):
    return cv2.normalize(np.abs(response), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def directional_responses(image, algorithm, kernel_size=3):
    """Return displayable absolute x/y derivative responses for directional operators."""
    gray = _gray(image)
    if algorithm == "Roberts Cross":
        gx = cv2.filter2D(gray, cv2.CV_32F, ROBERTS_X)
        gy = cv2.filter2D(gray, cv2.CV_32F, ROBERTS_Y)
    elif algorithm == "Prewitt":
        gx = cv2.filter2D(gray, cv2.CV_32F, PREWITT_X)
        gy = cv2.filter2D(gray, cv2.CV_32F, PREWITT_Y)
    elif algorithm == "Sobel":
        if kernel_size not in (3, 5, 7):
            raise ValueError("Sobel kernel size must be 3, 5, or 7.")
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=kernel_size)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=kernel_size)
    else:
        raise ValueError("Directional responses are not available for this operator.")
    return cv2.convertScaleAbs(gx), cv2.convertScaleAbs(gy)


def apply_edge(image, algorithm, kernel_size=3, sigma=1.0, sigma2=2.0, threshold=12):
    gray = _gray(image)
    if algorithm == "Roberts Cross":
        gx = cv2.filter2D(gray, cv2.CV_32F, ROBERTS_X)
        gy = cv2.filter2D(gray, cv2.CV_32F, ROBERTS_Y)
        return _magnitude(gx, gy)
    if algorithm == "Prewitt":
        gx = cv2.filter2D(gray, cv2.CV_32F, PREWITT_X)
        gy = cv2.filter2D(gray, cv2.CV_32F, PREWITT_Y)
        return _magnitude(gx, gy)
    if algorithm == "Sobel":
        if kernel_size not in (3, 5, 7):
            raise ValueError("Sobel kernel size must be 3, 5, or 7.")
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=kernel_size)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=kernel_size)
        return _magnitude(gx, gy)
    if algorithm == "Kirsch":
        responses = [cv2.filter2D(gray, cv2.CV_32F, kernel) for kernel in KIRSCH_KERNELS]
        return _normalize(np.maximum.reduce(responses))
    if algorithm == "Laplacian Edge":
        return _normalize(cv2.filter2D(gray, cv2.CV_32F, LAPLACIAN_KERNEL))
    if algorithm == "Laplacian of Gaussian (LoG)":
        if sigma <= 0:
            raise ValueError("LoG sigma must be greater than zero.")
        smooth = cv2.GaussianBlur(gray, (0, 0), sigma)
        response = cv2.Laplacian(smooth, cv2.CV_32F, ksize=3)
        crosses = np.zeros_like(gray, dtype=np.uint8)
        horizontal_cross = ((response[:, 1:] < 0) != (response[:, :-1] < 0))
        horizontal_cross &= np.abs(response[:, 1:] - response[:, :-1]) >= threshold
        crosses[:, 1:] |= horizontal_cross.astype(np.uint8) * 255
        vertical_cross = ((response[1:, :] < 0) != (response[:-1, :] < 0))
        vertical_cross &= np.abs(response[1:, :] - response[:-1, :]) >= threshold
        crosses[1:, :] |= vertical_cross.astype(np.uint8) * 255
        return crosses
    if algorithm == "Difference of Gaussian (DoG)":
        if sigma <= 0 or sigma2 <= 0 or sigma == sigma2:
            raise ValueError("DoG sigmas must be positive and different.")
        first = cv2.GaussianBlur(gray, (0, 0), sigma)
        second = cv2.GaussianBlur(gray, (0, 0), sigma2)
        return _normalize(first.astype(np.float32) - second.astype(np.float32))
    raise ValueError("Unknown edge algorithm: {}".format(algorithm))
