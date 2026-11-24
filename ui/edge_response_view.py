"""Window for inspecting horizontal and vertical edge responses."""

import customtkinter as ctk

from ui.image_viewer import ImageViewer


class EdgeResponseView(ctk.CTkToplevel):
    def __init__(self, master, horizontal, vertical, algorithm):
        super().__init__(master)
        self.title("PixelEnhance — Directional responses")
        self.geometry("1200x560")
        self.configure(fg_color="#0F172A")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)
        for column, (title, response) in enumerate((
            ("HORIZONTAL / X — absolute response", horizontal),
            ("VERTICAL / Y — absolute response", vertical),
        )):
            viewer = ImageViewer(self, title)
            viewer.grid(row=0, column=column, sticky="nsew", padx=(16 if column == 0 else 8, 8),
                        pady=18)
            viewer.set_image(response)
        ctk.CTkLabel(
            self, text="{} directional derivative responses (absolute intensity)".format(algorithm),
            text_color="#94A3B8",
        ).grid(row=1, column=0, columnspan=3, pady=(0, 14))
