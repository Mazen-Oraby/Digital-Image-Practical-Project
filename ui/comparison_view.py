"""Side-by-side comparison window and reference metric display."""

import customtkinter as ctk

from ui.image_viewer import ImageViewer
from utils.image_metrics import calculate_metrics


class ComparisonView(ctk.CTkToplevel):
    def __init__(self, master, original, result, algorithm, elapsed):
        super().__init__(master)
        self.title("PixelEnhance — Before / After")
        self.geometry("1080x680")
        self.configure(fg_color="#0F172A")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        before = ImageViewer(self, "ORIGINAL")
        after = ImageViewer(self, "ENHANCED · " + algorithm.upper())
        before.grid(row=0, column=0, sticky="nsew", padx=(18, 8), pady=18)
        after.grid(row=0, column=1, sticky="nsew", padx=(8, 18), pady=18)
        before.set_image(original)
        after.set_image(result)
        try:
            metrics = calculate_metrics(original, result)
            psnr = "∞" if metrics["psnr"] == float("inf") else "{:.2f} dB".format(metrics["psnr"])
            metric_text = "MSE  {:.3f}     PSNR  {}".format(metrics["mse"], psnr)
        except ValueError:
            metric_text = "MSE / PSNR unavailable: dimensions or channels differ."
        footer = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=10)
        footer.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 16))
        ctk.CTkLabel(footer, text="Processing time  {:.2f} ms".format(elapsed * 1000),
                     text_color="#A5B4FC").pack(side="left", padx=16, pady=12)
        ctk.CTkLabel(footer, text=metric_text, text_color="#E2E8F0").pack(side="left", padx=12)
        ctk.CTkLabel(
            self, text="MSE and PSNR are meaningful against a clean reference; the original may be noisy.",
            text_color="#94A3B8", font=ctk.CTkFont(size=11),
        ).grid(row=2, column=0, columnspan=2, pady=(0, 14))
