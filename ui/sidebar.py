"""Navigation sidebar for processing categories."""

import customtkinter as ctk


CATEGORIES = {
    "Dashboard": ["Average Filter", "Gaussian Low-Pass", "Median Filter", "Histogram Equalization"],
    "Smoothing & Noise Reduction": ["Average Filter", "Gaussian Low-Pass", "Median Filter"],
    "Sharpening": ["Laplacian Sharpening", "High-Pass Sharpening"],
    "Edge Detection": [
        "Roberts Cross", "Prewitt", "Sobel", "Kirsch", "Laplacian Edge",
        "Laplacian of Gaussian (LoG)", "Difference of Gaussian (DoG)",
    ],
    "Histogram Enhancement": ["Histogram Equalization"],
}


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_select, **kwargs):
        super().__init__(master, width=220, corner_radius=0, fg_color="#111C30", **kwargs)
        self.on_select = on_select
        ctk.CTkLabel(self, text="PIXEL\nENHANCE", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#818CF8", justify="left").pack(anchor="w", padx=22, pady=(24, 28))
        ctk.CTkLabel(self, text="WORKSPACE", text_color="#64748B",
                     font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=20, pady=(0, 8))
        self.buttons = {}
        for label in CATEGORIES:
            button = ctk.CTkButton(
                self, text=label, anchor="w", height=40, corner_radius=8,
                fg_color="transparent", hover_color="#263449", text_color="#CBD5E1",
                command=lambda name=label: self.select(name),
            )
            button.pack(fill="x", padx=10, pady=2)
            if label == "Dashboard":
                button.configure(fg_color="#263449", text_color="#F8FAFC")
            self.buttons[label] = button
        about = ctk.CTkButton(
            self, text="About Project", anchor="w", height=40, corner_radius=8,
            fg_color="transparent", hover_color="#263449", text_color="#CBD5E1",
            command=lambda: self.on_select("About Project"),
        )
        about.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(
            self, text="SPATIAL DOMAIN\nOpenCV  •  NumPy  •  Python",
            text_color="#64748B", justify="left", font=ctk.CTkFont(size=10),
        ).pack(side="bottom", anchor="w", padx=20, pady=20)

    def select(self, category):
        for name, button in self.buttons.items():
            button.configure(fg_color="#263449" if name == category else "transparent",
                             text_color="#F8FAFC" if name == category else "#CBD5E1")
        self.on_select(category)
