"""PixelEnhance desktop application entry point."""

import customtkinter as ctk

from ui.main_window import PixelEnhanceApp


def main() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = PixelEnhanceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
