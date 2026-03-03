import tkinter as tk
from main_of_matches_game import start_match_stick
if __name__ == "__main__":
 import tkinter as tk
from main_of_matches_game import start_match_stick

if __name__ == "__main__":

    root = tk.Tk()
    root.title("Projet IA")
    root.geometry("1200x600")
    root.minsize(1100, 500)

    # ===== HEADER =====
    header = tk.Frame(root, bd=2, relief="groove")
    header.pack(fill="x", padx=20, pady=(20, 10))

    tk.Label(
        header,
        text="Projet IA",
        font=("Arial", 20, "italic")
    ).pack(pady=10)

    # ===== ZONE DES CARTES =====
    main_frame = tk.Frame(root)
    main_frame.pack(expand=True)

    # Pour répartir l’espace horizontalement
    for i in range(3):
        main_frame.columnconfigure(i, weight=1)

    def create_card(parent, title, command=None, disabled=False):
        frame = tk.Frame(parent, bg="#ffffff", bd=1, relief="solid",
                     width=340, height=260)
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

    # Cartes
    card1 = create_card(main_frame, "Allumettes", command=lambda: start_match_stick(root))
    card1.grid(row=0, column=0, padx=30)

    card2 = create_card(main_frame, "Cubee", disabled=True)
    card2.grid(row=0, column=1, padx=30)

    card3 = create_card(main_frame, "PixelKart", disabled=True)
    card3.grid(row=0, column=2, padx=30)

    root.mainloop()