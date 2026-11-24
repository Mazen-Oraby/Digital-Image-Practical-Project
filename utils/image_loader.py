"""Validated image loading that works with non-ASCII Windows paths."""

from pathlib import Path

import cv2
import numpy as np


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def load_image(path):
    file_path = Path(path)
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Choose a PNG, JPG, JPEG, BMP, or TIFF image.")
    try:
        data = np.fromfile(str(file_path), dtype=np.uint8)
    except OSError as exc:
        raise OSError("Could not read the selected image: {}".format(exc)) from exc
    image = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    if image is None or image.size == 0:
        raise ValueError("The selected file is not a valid, supported image.")
    if image.ndim == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    elif image.ndim == 3 and image.shape[2] != 3:
        raise ValueError("The image must be grayscale or RGB color.")
    if image.dtype != np.uint8:
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return image
