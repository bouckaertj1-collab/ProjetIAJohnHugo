# view/game_view.py
import tkinter as tk
class GameView(tk.Tk):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Jeu des allumettes")
        self.resizable(False, False)
        self.configure(padx=14, pady=14)

        self.message_label = tk.Label(self, text="", font=("Arial", 12, "bold"))
        self.message_label.pack(pady=(0, 10))

      
        self.canvas = tk.Canvas(self, width=520, height=240, bg="#f5f5f5", highlightthickness=0)
        self.canvas.pack(pady=(0, 12))

        
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack()

        btn_kwargs = {"width": 12, "height": 2}

        self.btn1 = tk.Button(
            self.buttons_frame, text="Prendre 1",
            command=lambda: self.controller.handle_human_move(1),
            **btn_kwargs
        )
        self.btn2 = tk.Button(
            self.buttons_frame, text="Prendre 2",
            command=lambda: self.controller.handle_human_move(2),
            **btn_kwargs
        )
        self.btn3 = tk.Button(
            self.buttons_frame, text="Prendre 3",
            command=lambda: self.controller.handle_human_move(3),
            **btn_kwargs
        )

        self.btn1.pack(side=tk.LEFT, padx=8)
        self.btn2.pack(side=tk.LEFT, padx=8)
        self.btn3.pack(side=tk.LEFT, padx=8)
        self.update_view()

    def update_view(self):
        # redraw
        self.canvas.delete("all")
        self.draw_matches(self.controller.get_nb_matches())

        nb = self.controller.get_nb_matches()
        self.btn1.config(state=("normal" if nb >= 1 else "disabled"))
        self.btn2.config(state=("normal" if nb >= 2 else "disabled"))
        self.btn3.config(state=("normal" if nb >= 3 else "disabled"))

        # message
        self.message_label.config(text=self.controller.get_status_message())

        if self.controller.model.is_game_over():
            self.end_game()

    def draw_matches(self, nb):

        per_row = 25
        x0, y0 = 20, 24

        stick_w = 6     
        stick_h = 46
        head_r = 7
        gap = 20

        for i in range(nb):
            row = i // per_row
            col = i % per_row

            x = x0 + col * gap
            y = y0 + row * (stick_h + 20)

            # tête (cercle)
            self.canvas.create_oval(
                x - head_r,
                y - head_r,
                x + head_r,
                y + head_r,
                fill="#d9534f",
                outline="#b13f3b"
            )

            # tige (fine)
            self.canvas.create_rectangle(
                x - stick_w // 2,
                y,
                x + stick_w // 2,
                y + stick_h,
                fill="#deb887",
                outline="#2f2f2f"
            )

    def end_game(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        reset_btn = tk.Button(
            self.buttons_frame,
            text="Recommencer",
            command=self.controller.reset_game,
            width=18,
            height=2
        )
        reset_btn.pack()

    def reset(self):
        """
        Remet l'affichage de base (boutons 1/2/3)
        """
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        btn_kwargs = {"width": 12, "height": 2}
        self.btn1 = tk.Button(self.buttons_frame, text="Prendre 1",
                              command=lambda: self.controller.handle_human_move(1), **btn_kwargs)
        self.btn2 = tk.Button(self.buttons_frame, text="Prendre 2",
                              command=lambda: self.controller.handle_human_move(2), **btn_kwargs)
        self.btn3 = tk.Button(self.buttons_frame, text="Prendre 3",
                              command=lambda: self.controller.handle_human_move(3), **btn_kwargs)

        self.btn1.pack(side=tk.LEFT, padx=8)
        self.btn2.pack(side=tk.LEFT, padx=8)
        self.btn3.pack(side=tk.LEFT, padx=8)

        self.update_view()
