"""Focused tests for the spatial-domain processing algorithms."""

import unittest
import tempfile
from pathlib import Path

import numpy as np

from processing import process_image
from processing.edges import KIRSCH_KERNELS, LAPLACIAN_KERNEL, directional_responses
from utils.image_metrics import calculate_metrics
from utils.image_loader import load_image
from utils.image_saver import save_image


class ProcessingTests(unittest.TestCase):
    def setUp(self):
        y, x = np.indices((64, 64))
        gray = np.where(x < 32, 35, 220).astype(np.uint8)
        self.gray = gray
        self.color = np.dstack((gray, np.flipud(gray), gray.copy()))

    def test_smoothing_algorithms_preserve_size_and_dtype(self):
        for name in ("Average Filter", "Gaussian Low-Pass", "Median Filter"):
            result = process_image(self.color, name, kernel_size=5, sigma=1.2)
            self.assertEqual(result.shape, self.color.shape)
            self.assertEqual(result.dtype, np.uint8)

    def test_sharpening_algorithms_are_bounded_and_preserve_input(self):
        original = self.color.copy()
        for name in ("Laplacian Sharpening", "High-Pass Sharpening"):
            result = process_image(self.color, name, strength=1.4)
            self.assertEqual(result.shape, self.color.shape)
            self.assertGreaterEqual(int(result.min()), 0)
            self.assertLessEqual(int(result.max()), 255)
        np.testing.assert_array_equal(self.color, original)

    def test_each_edge_algorithm_returns_grayscale_image(self):
        names = (
            "Roberts Cross", "Prewitt", "Sobel", "Kirsch", "Laplacian Edge",
            "Laplacian of Gaussian (LoG)", "Difference of Gaussian (DoG)",
        )
        for name in names:
            with self.subTest(algorithm=name):
                result = process_image(self.color, name, kernel_size=3)
                self.assertEqual(result.shape, self.gray.shape)
                self.assertEqual(result.dtype, np.uint8)
                self.assertGreater(int(result.max()), 0)

    def test_histogram_equalization_supports_gray_and_color(self):
        self.assertEqual(process_image(self.gray, "Histogram Equalization").shape, self.gray.shape)
        result = process_image(self.color, "Histogram Equalization")
        self.assertEqual(result.shape, self.color.shape)
        self.assertEqual(result.dtype, np.uint8)

    def test_parameter_validation(self):
        with self.assertRaises(ValueError):
            process_image(self.gray, "Average Filter", kernel_size=4)
        with self.assertRaises(ValueError):
            process_image(self.gray, "Gaussian Low-Pass", sigma=0)
        with self.assertRaises(ValueError):
            process_image(self.gray, "Difference of Gaussian (DoG)", sigma=1, sigma2=1)

    def test_reference_metrics_and_shape_validation(self):
        metrics = calculate_metrics(self.gray, self.gray.copy())
        self.assertEqual(metrics["mse"], 0)
        self.assertEqual(metrics["psnr"], float("inf"))
        with self.assertRaises(ValueError):
            calculate_metrics(self.gray, self.color)

    def test_documented_directional_masks_are_well_formed(self):
        self.assertEqual(LAPLACIAN_KERNEL.shape, (3, 3))
        self.assertEqual(len(KIRSCH_KERNELS), 8)
        self.assertTrue(all(mask.shape == (3, 3) for mask in KIRSCH_KERNELS))

    def test_horizontal_and_vertical_responses_are_available(self):
        for name in ("Roberts Cross", "Prewitt", "Sobel"):
            horizontal, vertical = directional_responses(self.color, name, kernel_size=3)
            self.assertEqual(horizontal.shape, self.gray.shape)
            self.assertEqual(vertical.shape, self.gray.shape)
            self.assertGreater(max(int(horizontal.max()), int(vertical.max())), 0)

    def test_image_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "enhanced.png"
            save_image(path, self.color)
            loaded = load_image(path)
            np.testing.assert_array_equal(loaded, self.color)
            self.assertEqual(loaded.shape, self.color.shape)

    def test_corrupted_supported_image_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.png"
            path.write_bytes(b"not an image")
            with self.assertRaises(ValueError):
                load_image(path)


if __name__ == "__main__":
    unittest.main()
