"""Spatial-domain image processing algorithms."""

from processing.edges import apply_edge
from processing.histogram_equalization import equalize_histogram
from processing.low_pass import apply_low_pass
from processing.sharpening import apply_sharpening


def process_image(image, algorithm, **parameters):
    """Run one named spatial-domain algorithm on an image."""
    if algorithm in ("Average Filter", "Gaussian Low-Pass", "Median Filter"):
        return apply_low_pass(
            image, algorithm,
            kernel_size=parameters.get("kernel_size", 3),
            sigma=parameters.get("sigma", 1.0),
        )
    if algorithm in ("Laplacian Sharpening", "High-Pass Sharpening"):
        return apply_sharpening(image, algorithm, strength=parameters.get("strength", 1.0))
    if algorithm == "Histogram Equalization":
        return equalize_histogram(image)
    return apply_edge(
        image, algorithm,
        kernel_size=parameters.get("kernel_size", 3),
        sigma=parameters.get("sigma", 1.0),
        sigma2=parameters.get("sigma2", 2.0),
        threshold=parameters.get("threshold", 12),
    )


__all__ = ["process_image"]
