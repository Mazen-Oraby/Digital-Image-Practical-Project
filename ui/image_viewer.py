"""Responsive image preview with fit and zoom controls."""

import customtkinter as ctk
from PIL import Image

from utils.image_converter import to_pillow


class ImageViewer(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, fg_color="#1E293B", corner_radius=12, **kwargs)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(11, 5))
        ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#CBD5E1").pack(side="left")
        self.info = ctk.CTkLabel(header, text="No image", text_color="#64748B",
                                 font=ctk.CTkFont(size=10))
        self.info.pack(side="right")
        self.image_label = ctk.CTkLabel(self, text="Upload an image to begin",
                                        text_color="#64748B", fg_color="#0F172A",
                                        corner_radius=8)
        self.image_label.pack(fill="both", expand=True, padx=12, pady=(2, 12))
        self._image = None
        self._ctk_image = None
        self.zoom = 1.0
        self.image_label.bind("<Configure>", lambda _event: self._render())

    def set_image(self, image):
        self._image = None if image is None else to_pillow(image).copy()
        if image is None:
            self.info.configure(text="No image")
            self.image_label.configure(image=None, text="Upload an image to begin")
        else:
            self.info.configure(text="{} × {}".format(image.shape[1], image.shape[0]))
        self._render()

    def set_zoom(self, zoom):
        self.zoom = max(0.1, min(5.0, zoom))
        self._render()

    def _render(self):
        if self._image is None:
            return
        width = max(1, self.image_label.winfo_width() - 24)
        height = max(1, self.image_label.winfo_height() - 24)
        source = self._image
        ratio = min(width / source.width, height / source.height) * self.zoom
        size = (max(1, int(source.width * ratio)), max(1, int(source.height * ratio)))
        preview = source.resize(size, Image.Resampling.LANCZOS)
        self._ctk_image = ctk.CTkImage(light_image=preview, dark_image=preview, size=size)
        self.image_label.configure(image=self._ctk_image, text="")
