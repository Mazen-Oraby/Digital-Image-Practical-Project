"""Save full-resolution OpenCV images to PNG or JPEG files."""

from pathlib import Path

import cv2


def save_image(path, image):
    file_path = Path(path)
    extension = file_path.suffix.lower()
    if extension not in (".png", ".jpg", ".jpeg"):
        raise ValueError("Export format must be PNG or JPEG.")
    success, encoded = cv2.imencode(extension, image)
    if not success:
        raise OSError("OpenCV could not encode the processed image.")
    try:
        encoded.tofile(str(file_path))
    except OSError as exc:
        raise OSError("Could not save the image: {}".format(exc)) from exc
