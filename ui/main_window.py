"""Main PixelEnhance desktop window and application workflow."""

import os
import time
from tkinter import filedialog, messagebox

import customtkinter as ctk
import cv2

from processing import process_image
from ui.comparison_view import ComparisonView
from ui.edge_response_view import EdgeResponseView
from ui.histogram_view import HistogramView
from ui.image_viewer import ImageViewer
from ui.settings_panel import SettingsPanel
from ui.sidebar import CATEGORIES, Sidebar
from processing.edges import directional_responses
from utils.image_loader import load_image
from utils.image_saver import save_image


BACKGROUND = "#0F172A"
CARD = "#1E293B"


class PixelEnhanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PixelEnhance — Spatial Domain Image Enhancement Studio")
        self.geometry("1440x900")
        self.minsize(1060, 680)
        self.configure(fg_color=BACKGROUND)
        self.original = None
        self.result = None
        self.source_path = None
        self.history = []
        self.last_algorithm = "No operation yet"
        self.last_parameters = {}
        self.processing_seconds = 0.0
        self.directional_result = None
        self.zoom = 1.0

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.sidebar = Sidebar(self, self._select_category)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=1, columnspan=2, sticky="ew", padx=20, pady=(16, 8))
        toolbar.grid_columnconfigure(0, weight=1)
        title_box = ctk.CTkFrame(toolbar, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_box, text="Image workspace", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#F8FAFC").pack(anchor="w")
        self.file_info = ctk.CTkLabel(title_box, text="No image loaded",
                                      text_color="#94A3B8", font=ctk.CTkFont(size=11))
        self.file_info.pack(anchor="w", pady=(2, 0))
        self.upload_button = ctk.CTkButton(toolbar, text="＋  Open image", width=132,
                                            fg_color="#6366F1", hover_color="#4F46E5",
                                            command=self.open_image)
        self.upload_button.grid(row=0, column=1, padx=(0, 8))
        self.export_button = ctk.CTkButton(toolbar, text="Export", width=82, fg_color="#334155",
                                            hover_color="#475569", state="disabled", command=self.export_image)
        self.export_button.grid(row=0, column=2, padx=4)
        self.undo_button = ctk.CTkButton(toolbar, text="Undo", width=70, fg_color="#334155",
                                          hover_color="#475569", state="disabled", command=self.undo)
        self.undo_button.grid(row=0, column=3, padx=4)
        self.reset_button = ctk.CTkButton(toolbar, text="Reset", width=70, fg_color="#334155",
                                           hover_color="#475569", state="disabled", command=self.reset)
        self.reset_button.grid(row=0, column=4, padx=4)

        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.grid(row=1, column=1, sticky="nsew", padx=(18, 12), pady=(8, 16))
        workspace.grid_columnconfigure((0, 1), weight=1, uniform="viewers")
        workspace.grid_rowconfigure(1, weight=1)
        view_tools = ctk.CTkFrame(workspace, fg_color="transparent")
        view_tools.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(view_tools, text="PREVIEW", text_color="#94A3B8",
                     font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
        self._tool_button(view_tools, "−", lambda: self._set_zoom(self.zoom / 1.2)).pack(side="right", padx=2)
        self._tool_button(view_tools, "＋", lambda: self._set_zoom(self.zoom * 1.2)).pack(side="right", padx=2)
        self._tool_button(view_tools, "Fit", lambda: self._set_zoom(1.0)).pack(side="right", padx=2)
        self._tool_button(view_tools, "Compare", self.show_comparison).pack(side="right", padx=(8, 2))
        self._tool_button(view_tools, "Histogram", self.show_histogram).pack(side="right", padx=2)
        self.responses_button = self._tool_button(view_tools, "Responses", self.show_responses)
        self.responses_button.configure(state="disabled")
        self.responses_button.pack(side="right", padx=2)

        self.original_view = ImageViewer(workspace, "ORIGINAL IMAGE")
        self.result_view = ImageViewer(workspace, "ENHANCED RESULT")
        self.original_view.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        self.result_view.grid(row=1, column=1, sticky="nsew", padx=(6, 0))
        self.status = ctk.CTkLabel(workspace, text="Ready — open an image to start.",
                                   anchor="w", text_color="#94A3B8")
        self.status.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(9, 0))

        self.settings = SettingsPanel(self, self.apply_algorithm)
        self.settings.grid(row=1, column=2, sticky="nsew", padx=(0, 18), pady=(8, 16))
        self.bind("<Control-o>", lambda _event: self.open_image())
        self.bind("<Control-s>", lambda _event: self.export_image())

    @staticmethod
    def _tool_button(parent, text, command):
        return ctk.CTkButton(parent, text=text, width=76 if len(text) > 1 else 34,
                             height=30, fg_color="#1E293B", hover_color="#334155",
                             text_color="#CBD5E1", command=command)

    def _select_category(self, category):
        if category == "About Project":
            messagebox.showinfo(
                "About PixelEnhance",
                "PixelEnhance demonstrates spatial-domain image enhancement using OpenCV and NumPy.\n\n"
                "Filters operate on image neighborhoods; no Fourier-domain processing is used.",
                parent=self,
            )
        elif category in CATEGORIES:
            self.settings.set_category(category)

    def open_image(self):
        path = filedialog.askopenfilename(
            parent=self,
            title="Open image",
            filetypes=[("Supported images", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                       ("All files", "*.*")],
        )
        if not path:
            return
        try:
            image = load_image(path)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Could not open image", str(exc), parent=self)
            self.status.configure(text="Image could not be opened.", text_color="#EF4444")
            return
        self.original = image.copy()
        self.result = image.copy()
        self.source_path = path
        self.history.clear()
        self.last_algorithm = "No operation yet"
        self.last_parameters = {}
        self.processing_seconds = 0.0
        self.directional_result = None
        self.responses_button.configure(state="disabled")
        self.original_view.set_image(self.original)
        self.result_view.set_image(self.result)
        height, width = image.shape[:2]
        image_format = os.path.splitext(path)[1].upper().lstrip(".")
        size = os.path.getsize(path)
        self.file_info.configure(
            text="{}  •  {} × {}  •  {}  •  {}".format(
                os.path.basename(path), width, height, image_format, self._format_size(size)
            )
        )
        self.settings.set_image_available(True)
        self.export_button.configure(state="normal")
        self.reset_button.configure(state="normal")
        self.undo_button.configure(state="disabled")
        self.status.configure(text="Image loaded. Original pixels are preserved.", text_color="#22C55E")

    @staticmethod
    def _format_size(byte_count):
        if byte_count < 1024 * 1024:
            return "{:.1f} KB".format(byte_count / 1024)
        return "{:.2f} MB".format(byte_count / (1024 * 1024))

    def apply_algorithm(self):
        if self.original is None:
            return
        algorithm = self.settings.get_algorithm()
        parameters = self.settings.get_parameters()
        source = self.result if self.settings.get_mode() == "Latest result" else self.original
        self.status.configure(text="Processing {}…".format(algorithm), text_color="#A5B4FC")
        self.update_idletasks()
        start = time.perf_counter()
        try:
            processed = process_image(source, algorithm, **parameters)
            directional = None
            if algorithm in ("Roberts Cross", "Prewitt", "Sobel"):
                directional = directional_responses(
                    source, algorithm, kernel_size=parameters["kernel_size"]
                )
        except (ValueError, cv2.error) as exc:
            messagebox.showerror("Processing failed", str(exc), parent=self)
            self.status.configure(text="Processing failed: {}".format(exc), text_color="#EF4444")
            return
        elapsed = time.perf_counter() - start
        self.history.append((
            self.result.copy(), self.last_algorithm, self.last_parameters.copy(),
            self.processing_seconds,
            None if self.directional_result is None else tuple(
                response.copy() for response in self.directional_result
            ),
        ))
        self.result = processed
        self.last_algorithm = algorithm
        self.last_parameters = parameters
        self.processing_seconds = elapsed
        self.directional_result = directional
        self.responses_button.configure(state="normal" if directional else "disabled")
        self.result_view.set_image(self.result)
        self.undo_button.configure(state="normal")
        self.status.configure(
            text="{} completed in {:.2f} ms  •  {}".format(
                algorithm, elapsed * 1000, self._parameter_summary(algorithm, parameters)
            ),
            text_color="#22C55E",
        )

    @staticmethod
    def _parameter_summary(algorithm, parameters):
        if algorithm in ("Average Filter", "Gaussian Low-Pass", "Median Filter", "Sobel"):
            return "kernel {} × {}".format(parameters["kernel_size"], parameters["kernel_size"])
        if algorithm in ("Laplacian Sharpening", "High-Pass Sharpening"):
            return "strength {:.1f}".format(parameters["strength"])
        return "spatial-domain operation"

    def undo(self):
        if not self.history:
            return
        (self.result, self.last_algorithm, self.last_parameters, self.processing_seconds,
         self.directional_result) = self.history.pop()
        self.result_view.set_image(self.result)
        self.responses_button.configure(state="normal" if self.directional_result else "disabled")
        self.undo_button.configure(state="normal" if self.history else "disabled")
        self.status.configure(
            text="Last operation undone. Current result: {}".format(self.last_algorithm),
            text_color="#A5B4FC",
        )

    def reset(self):
        if self.original is None:
            return
        self.result = self.original.copy()
        self.history.clear()
        self.last_algorithm = "No operation yet"
        self.last_parameters = {}
        self.processing_seconds = 0.0
        self.directional_result = None
        self.responses_button.configure(state="disabled")
        self.result_view.set_image(self.result)
        self.undo_button.configure(state="disabled")
        self.status.configure(text="Result reset to the original image.", text_color="#A5B4FC")

    def export_image(self):
        if self.result is None:
            return
        path = filedialog.asksaveasfilename(
            parent=self, title="Export processed image", defaultextension=".png",
            filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg *.jpeg")],
        )
        if not path:
            return
        if os.path.splitext(path)[1].lower() not in (".png", ".jpg", ".jpeg"):
            path += ".png"
        try:
            save_image(path, self.result)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Export failed", str(exc), parent=self)
            self.status.configure(text="Export failed: {}".format(exc), text_color="#EF4444")
            return
        self.status.configure(text="Saved full-resolution image to {}".format(path), text_color="#22C55E")

    def show_comparison(self):
        if self.original is not None:
            ComparisonView(self, self.original, self.result, self.last_algorithm, self.processing_seconds)

    def show_histogram(self):
        if self.original is not None:
            HistogramView(self, self.original, self.result)

    def show_responses(self):
        if self.directional_result is not None:
            horizontal, vertical = self.directional_result
            EdgeResponseView(self, horizontal, vertical, self.last_algorithm)

    def _set_zoom(self, zoom):
        self.zoom = max(0.1, min(5.0, zoom))
        self.original_view.set_zoom(self.zoom)
        self.result_view.set_zoom(self.zoom)
