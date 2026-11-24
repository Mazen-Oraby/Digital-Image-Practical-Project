# PixelEnhance — Spatial Domain Image Enhancement Studio

PixelEnhance is a Windows desktop application for exploring classical spatial-domain image enhancement. It uses CustomTkinter for the interface, OpenCV and NumPy for image processing, Pillow for previews, and Matplotlib for histograms. All filters work directly with pixels and neighborhoods; no Fourier transforms are used.

## Features

- Load PNG, JPG/JPEG, BMP, and TIFF images, including grayscale images.
- Preserve the source image while applying operations to either the original or the latest result.
- Preview the original and processed image side by side, zoom, fit, undo, reset, and export full-resolution PNG/JPEG.
- Explore each algorithm's principle and its kernel/response description.
- Hover over the algorithm selector for a brief algorithm tooltip.
- Compare results and inspect original/enhanced intensity histograms.
- Inspect horizontal and vertical response images for Roberts, Prewitt, and Sobel.
- Measure operation time. MSE and PSNR are displayed as reference comparisons only: meaningful evaluation requires a clean ground-truth image, and the source is not assumed to be ground truth.

## Spatial-domain algorithms

1. Average (box) filter, using `cv2.blur`.
2. Gaussian low-pass filter, using `cv2.GaussianBlur`.
3. Median filter, using `cv2.medianBlur`.
4. Laplacian sharpening, subtracting a scaled four-neighbor Laplacian response.
5. High-pass sharpening, blending the source with the specified cross-shaped high-pass response.
6. Roberts Cross, using two 2×2 directional masks.
7. Prewitt, using horizontal and vertical 3×3 masks.
8. Sobel, using `cv2.Sobel` with selectable odd kernel size.
9. Kirsch, taking the maximum response from eight compass masks.
10. Laplacian edge detection.
11. Laplacian of Gaussian (LoG), with Gaussian denoising and thresholded zero crossings.
12. Difference of Gaussian (DoG), using two selectable Gaussian scales.
13. Histogram equalization. Grayscale uses `cv2.equalizeHist`; color equalizes luminance in YCrCb to limit hue shifts.

Neighborhood filters and sharpening preserve the input's dimensions. Edge detectors return a grayscale edge map. Color histogram equalization retains three-channel color. For color edge inputs, processing uses the image luminance.

## Project structure

```text
main.py
processing/      # spatial filters and dispatch
ui/              # CustomTkinter window, viewers, settings and plots
utils/            # image I/O, conversion and metric helpers
tests/            # unittest coverage for processing
requirements.txt
```

## Windows installation and launch

Install Python 3.11 or newer, then open PowerShell in this project folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Run the processing tests:

```powershell
python -m unittest discover -s tests -v
```

## Notes

- OpenCV stores color pixels in BGR order; Pillow preview conversion is handled in the UI conversion helper.
- Export writes the processed array, never a resized preview.
- Images with alpha are composited by dropping alpha (retaining their RGB/BGR color values); unsupported channel layouts are rejected.
- MSE is the mean squared pixel error and PSNR is `10 log10(255² / MSE)`. These scores compare against the supplied reference only and should not be interpreted as objective enhancement quality without a clean reference.
