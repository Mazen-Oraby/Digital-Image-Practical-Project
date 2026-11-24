"""Dark-themed Matplotlib histograms in a separate window."""

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from utils.image_metrics import grayscale


class HistogramView(ctk.CTkToplevel):
    def __init__(self, master, original, result):
        super().__init__(master)
        self.title("PixelEnhance — Histograms")
        self.geometry("1000x520")
        self.configure(fg_color="#0F172A")
        figure = Figure(figsize=(10, 4.5), dpi=100, facecolor="#0F172A")
        for index, (image, title) in enumerate(((original, "Original"), (result, "Enhanced")), 1):
            axis = figure.add_subplot(1, 2, index)
            axis.set_facecolor("#1E293B")
            axis.set_title(title, color="#F8FAFC")
            axis.set_xlabel("Intensity", color="#CBD5E1")
            axis.set_ylabel("Pixel count", color="#CBD5E1")
            axis.tick_params(colors="#94A3B8")
            for spine in axis.spines.values():
                spine.set_color("#334155")
            if image.ndim == 2:
                axis.hist(image.ravel(), bins=256, range=(0, 256), color="#818CF8", alpha=0.9)
            else:
                colors = (("Blue", 0, "#60A5FA"), ("Green", 1, "#4ADE80"), ("Red", 2, "#F87171"))
                for label, channel, color in colors:
                    axis.hist(image[:, :, channel].ravel(), bins=256, range=(0, 256),
                              color=color, alpha=0.48, label=label)
                axis.legend(facecolor="#1E293B", labelcolor="#F8FAFC", frameon=False)
            axis.grid(alpha=0.15, color="#94A3B8")
        figure.tight_layout()
        canvas = FigureCanvasTkAgg(figure, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)
