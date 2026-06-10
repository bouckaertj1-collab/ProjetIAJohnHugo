from __future__ import annotations

import tkinter as tk


class PixelKartWindow(tk.Toplevel):
    """Main window used to display PixelKart screens."""

    def __init__(self, parent: tk.Misc) -> None:
        """
        Initialize the PixelKart window.

        Args:
            parent: Parent Tkinter window.
        """
        super().__init__(parent)
        self.title("PixelKart")
        self.minsize(1000, 650)
        self.resizable(True, True)
        self.center()

    def center(self, width: int = 1100, height: int = 700) -> None:
        """
        Center the window on the screen.

        Args:
            width: Window width.
            height: Window height.
        """
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")