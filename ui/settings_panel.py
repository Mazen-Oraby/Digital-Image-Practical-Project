"""Algorithm selector and parameter controls."""

import customtkinter as ctk

from ui.sidebar import CATEGORIES
from ui.components import Tooltip


THEORY = {
    "Average Filter": ("A neighborhood mean suppresses rapid intensity variation by replacing each pixel with the local average.",
                       "h = (1/k²) · ones(k,k)"),
    "Gaussian Low-Pass": ("Gaussian-weighted neighborhood averaging reduces high-frequency noise with less ringing than a box filter.",
                          "Gσ(x,y) = exp(-(x²+y²)/(2σ²))"),
    "Median Filter": ("A nonlinear rank filter replaces each pixel with its neighborhood median; it is effective against impulse noise.",
                      "g(x,y) = median{f(s,t)}"),
    "Laplacian Sharpening": ("The Laplacian estimates the second spatial derivative. Subtracting its scaled response emphasizes fine detail.",
                             "0  1  0\n1 -4  1\n0  1  0"),
    "High-Pass Sharpening": ("A center-weighted high-pass kernel retains the source and emphasizes local intensity changes.",
                             "0 -1  0\n-1  5 -1\n0 -1  0"),
    "Roberts Cross": ("Two 2×2 diagonal difference masks approximate the gradient magnitude.",
                      "Gx: [1  0; 0 -1]\nGy: [0  1; -1 0]"),
    "Prewitt": ("Horizontal and vertical 3×3 derivative masks estimate the image gradient in two directions.",
                "Gx: [-1 0 1; -1 0 1; -1 0 1]\nGy: [-1 -1 -1; 0 0 0; 1 1 1]"),
    "Sobel": ("Sobel uses a derivative combined with perpendicular smoothing; the gradient magnitude estimates edge strength.",
              "Gx = d/dx * smoothing; Gy = d/dy * smoothing"),
    "Kirsch": ("Eight compass masks measure directional edge strength; the largest directional response is retained.",
               "Each mask: center 0, three adjacent +5, others -3"),
    "Laplacian Edge": ("The second derivative responds to rapid intensity changes regardless of orientation.",
                       "0  1  0\n1 -4  1\n0  1  0"),
    "Laplacian of Gaussian (LoG)": ("Gaussian smoothing limits noise before a Laplacian; edges are located at thresholded zero crossings.",
                                    "LoG = ∇²(Gσ * f)"),
    "Difference of Gaussian (DoG)": ("Subtracting two differently blurred images approximates a band-pass edge response.",
                                     "DoG = Gσ1 * f - Gσ2 * f"),
    "Histogram Equalization": ("Redistributes luminance values using the cumulative histogram to improve global contrast.",
                              "s = (L-1) · Σ p(rj)"),
}


class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master, on_apply, **kwargs):
        super().__init__(master, width=290, fg_color="#1E293B", corner_radius=12, **kwargs)
        self.on_apply = on_apply
        self.algorithm = ctk.StringVar(value="Average Filter")
        self.kernel = ctk.StringVar(value="3")
        self.sigma = ctk.DoubleVar(value=1.0)
        self.sigma2 = ctk.DoubleVar(value=2.0)
        self.strength = ctk.DoubleVar(value=1.0)
        self.threshold = ctk.IntVar(value=12)
        self.mode = ctk.StringVar(value="Original image")
        self._category = "Dashboard"
        self._image_available = False

        ctk.CTkLabel(self, text="PROCESSING", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#94A3B8").pack(anchor="w", padx=18, pady=(18, 12))
        ctk.CTkLabel(self, text="Algorithm", text_color="#CBD5E1").pack(anchor="w", padx=18, pady=(0, 5))
        self.algorithm_menu = ctk.CTkOptionMenu(self, variable=self.algorithm, values=CATEGORIES["Dashboard"],
                                                 command=self._update_theory, fg_color="#334155",
                                                 button_color="#6366F1", height=36)
        self.algorithm_menu.pack(fill="x", padx=18)
        ctk.CTkLabel(self, text="Process from", text_color="#CBD5E1").pack(anchor="w", padx=18, pady=(14, 5))
        self.mode_menu = ctk.CTkOptionMenu(self, variable=self.mode,
                                           values=["Original image", "Latest result"],
                                           fg_color="#334155", button_color="#6366F1")
        self.mode_menu.pack(fill="x", padx=18)

        self.parameter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.parameter_frame.pack(fill="x")
        self.kernel_row = self._row("Kernel size")
        self.kernel_menu = ctk.CTkOptionMenu(self.kernel_row, variable=self.kernel,
                                              values=["3", "5", "7"], width=90,
                                              fg_color="#334155", button_color="#6366F1")
        self.kernel_menu.pack(side="right")
        self.sigma_row, self.sigma_slider = self._slider_row("Sigma", self.sigma, 0.1, 5.0)
        self.sigma2_row, self.sigma2_slider = self._slider_row("Second sigma", self.sigma2, 0.2, 8.0)
        self.strength_row, self.strength_slider = self._slider_row("Strength", self.strength, 0.0, 3.0)
        self.threshold_row, self.threshold_slider = self._slider_row("LoG threshold", self.threshold, 1, 80)

        ctk.CTkFrame(self, height=1, fg_color="#334155").pack(fill="x", padx=18, pady=16)
        ctk.CTkLabel(self, text="HOW IT WORKS", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#94A3B8").pack(anchor="w", padx=18)
        self.explanation = ctk.CTkLabel(self, text="", wraplength=245, justify="left",
                                         text_color="#CBD5E1", font=ctk.CTkFont(size=12))
        self.explanation.pack(anchor="w", padx=18, pady=(7, 10))
        self.kernel_text = ctk.CTkLabel(self, text="", justify="left", anchor="w",
                                         font=ctk.CTkFont(family="Consolas", size=11),
                                         text_color="#A5B4FC")
        self.kernel_text.pack(anchor="w", padx=18, pady=(0, 14))
        self.apply_button = ctk.CTkButton(self, text="Apply algorithm", height=42,
                                           fg_color="#6366F1", hover_color="#4F46E5",
                                           command=self.on_apply, state="disabled")
        self.apply_button.pack(fill="x", padx=18, pady=(4, 8))
        self._update_theory(self.algorithm.get())
        self.algorithm_tooltip = Tooltip(
            self.algorithm_menu, lambda: THEORY[self.algorithm.get()][0]
        )
        self.set_image_available(False)

    def _row(self, label):
        row = ctk.CTkFrame(self.parameter_frame, fg_color="transparent", height=34)
        row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(row, text=label, text_color="#CBD5E1").pack(side="left")
        return row

    def _slider_row(self, label, variable, start, end):
        row = ctk.CTkFrame(self.parameter_frame, fg_color="transparent")
        row.pack(fill="x", pady=(9, 0))
        title = ctk.CTkFrame(row, fg_color="transparent")
        title.pack(fill="x")
        ctk.CTkLabel(title, text=label, text_color="#CBD5E1").pack(side="left")
        value_label = ctk.CTkLabel(title, textvariable=variable, text_color="#A5B4FC")
        value_label.pack(side="right")
        slider = ctk.CTkSlider(row, from_=start, to=end, variable=variable,
                               number_of_steps=int((end - start) * 10), progress_color="#6366F1")
        slider.pack(fill="x", pady=(2, 0))
        return row, slider

    def set_category(self, category):
        self._category = category
        self.algorithm_menu.configure(values=CATEGORIES[category])
        self.algorithm.set(CATEGORIES[category][0])
        self._update_theory(self.algorithm.get())

    def set_image_available(self, available):
        self._image_available = available
        state = "normal" if available else "disabled"
        self.apply_button.configure(state=state)
        self.algorithm_menu.configure(state=state)
        self.mode_menu.configure(state=state)
        self.kernel_menu.configure(state=state)
        for slider in (self.sigma_slider, self.sigma2_slider,
                       self.strength_slider, self.threshold_slider):
            slider.configure(state=state)

    def get_parameters(self):
        return {
            "kernel_size": int(self.kernel.get()),
            "sigma": float(self.sigma.get()),
            "sigma2": float(self.sigma2.get()),
            "strength": float(self.strength.get()),
            "threshold": int(self.threshold.get()),
        }

    def get_algorithm(self):
        return self.algorithm.get()

    def get_mode(self):
        return self.mode.get()

    def _update_theory(self, _value=None):
        description, kernel = THEORY[self.algorithm.get()]
        self.explanation.configure(text=description)
        self.kernel_text.configure(text="Kernel / principle\n" + kernel)
        name = self.algorithm.get()
        for row in (self.kernel_row, self.sigma_row, self.sigma2_row,
                    self.strength_row, self.threshold_row):
            row.pack_forget()
        if name in ("Average Filter", "Gaussian Low-Pass", "Median Filter", "Sobel"):
            self.kernel_row.pack(fill="x", pady=(8, 0))
        if name in ("Gaussian Low-Pass", "Laplacian of Gaussian (LoG)", "Difference of Gaussian (DoG)"):
            self.sigma_row.pack(fill="x", pady=(9, 0))
        if name == "Difference of Gaussian (DoG)":
            self.sigma2_row.pack(fill="x", pady=(9, 0))
        if name in ("Laplacian Sharpening", "High-Pass Sharpening"):
            self.strength_row.pack(fill="x", pady=(9, 0))
        if name == "Laplacian of Gaussian (LoG)":
            self.threshold_row.pack(fill="x", pady=(9, 0))
