"""Small reusable user-interface components."""

import customtkinter as ctk


class Tooltip:
    def __init__(self, widget, text_provider, delay=450):
        self.widget = widget
        self.text_provider = text_provider
        self.delay = delay
        self._timer = None
        self._window = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel_timer()
        self._timer = self.widget.after(self.delay, self._show)

    def _show(self):
        self._timer = None
        text = self.text_provider()
        if not text or not self.widget.winfo_exists():
            return
        self._window = ctk.CTkToplevel(self.widget)
        self._window.wm_overrideredirect(True)
        self._window.attributes("-topmost", True)
        self._window.configure(fg_color="#334155")
        label = ctk.CTkLabel(self._window, text=text, wraplength=300, justify="left",
                             text_color="#F8FAFC", padx=10, pady=7)
        label.pack()
        self._window.geometry("+{}+{}".format(
            self.widget.winfo_rootx() + 10, self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        ))

    def _hide(self, _event=None):
        self._cancel_timer()
        if self._window is not None:
            self._window.destroy()
            self._window = None

    def _cancel_timer(self):
        if self._timer is not None:
            self.widget.after_cancel(self._timer)
            self._timer = None
