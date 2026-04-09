"""
Tkinter view for the application launcher.

This window displays the main menu allowing the user
to choose which game to start.
"""

import tkinter as tk


class LauncherView(tk.Tk):
    """
    Graphical launcher window.

    Responsibilities:
        - Display the main menu
        - Provide buttons to start available games
        - Delegate user actions to the launcher controller
    """

    def __init__(self, controller) -> None:
        """
        Initialize the launcher window.

        Args:
            controller: Controller managing user actions.
        """
        super().__init__()
        self.controller = controller

        self.title("Projet IA")
        self.geometry("1200x600")
        self.minsize(1100, 500)
        self.resizable(False, False)

        self._build_ui()

    def _build_ui(self) -> None:
        """
        Create all interface elements.
        """
        header: tk.Frame = tk.Frame(self, bd=2, relief="groove")
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            header,
            text="Projet IA",
            font=("Arial", 20, "italic")
        ).pack(pady=10)

        main_frame: tk.Frame = tk.Frame(self)
        main_frame.pack(expand=True)

        for i in range(3):
            main_frame.columnconfigure(i, weight=1)

        card1: tk.Frame = self._create_card(
            main_frame,
            "Allumettes",
            command=self.controller.on_matchsticks
        )
        card1.grid(row=0, column=0, padx=30)

        card2: tk.Frame = self._create_card(
            main_frame,
            "Cubee",
            command=self.controller.on_cubee
        )
        card2.grid(row=0, column=1, padx=30)

        card3: tk.Frame = self._create_card(
            main_frame,
            "PixelKart",
            command=self.controller.on_pixelkart
        )
        card3.grid(row=0, column=2, padx=30)

    def _create_card(
        self,
        parent: tk.Widget,
        title: str,
        command=None,
        disabled: bool = False
    ) -> tk.Frame:
        """
        Create a launcher card.

        Args:
            parent: Parent container.
            title: Card title.
            command: Function executed when clicking the button.
            disabled: Whether the card is disabled.

        Returns:
            The card frame.
        """
        frame: tk.Frame = tk.Frame(
            parent,
            bg="#ffffff",
            bd=1,
            relief="solid",
            width=340,
            height=260
        )
        frame.grid_propagate(False)

        tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 16, "italic"),
            bg="#ffffff"
        ).pack(pady=50)

        if disabled:
            tk.Button(
                frame,
                text="Pas encore disponible",
                state="disabled",
                width=20,
                height=2
            ).pack()
        else:
            tk.Button(
                frame,
                text="Jouer",
                width=18,
                height=2,
                bg="#6fa8dc",
                activebackground="#3d85c6",
                fg="black",
                command=command
            ).pack()

        return frame

    def run(self) -> None:
        """
        Start the Tkinter main loop.
        """
        self.mainloop()