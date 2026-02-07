import random

class Game:
    """
    Jeu des allumettes.
    Règle: le joueur qui prend la dernière allumette perd.
    """

    def __init__(self, nb, player1, player2, displayable=True):
        # nb initial et nb courant
        self.nb = nb
        self.original_nb = nb

        # affichage console activable/désactivable
        self.displayable = displayable

        # joueurs
        self.player1 = player1
        self.player2 = player2

        # rattacher la game aux joueurs
        self.player1.game = self
        self.player2.game = self

        # état de partie
        self.current_player = None
        self.is_over = False
        self.winner = None
        self.loser = None

        # mélange au démarrage
        self.shuffle()

    def shuffle(self):
        """
        Mélange l'ordre des joueurs (qui commence).
        """
        players = [self.player1, self.player2]
        random.shuffle(players)
        self.player1, self.player2 = players[0], players[1]
        self.current_player = self.player1

    def reset(self):
        """
        Remet la partie à zéro et mélange les joueurs.
        """
        self.nb = self.original_nb
        self.is_over = False
        self.winner = None
        self.loser = None
        self.shuffle()

    def display(self):
        """
        Affiche l'état du jeu (si displayable).
        """
        if self.displayable:
            print(f"Allumettes restantes: {self.nb}")

    def step(self, action):
        """
        Applique une action (1/2/3).
        Met à jour l'état du jeu et passe au joueur suivant si nécessaire.
        """
        if self.is_over:
            raise ValueError("La partie est déjà terminée.")

        if action not in (1, 2, 3):
            raise ValueError("Action invalide: il faut retirer 1, 2 ou 3 allumettes.")

        if action > self.nb:
            raise ValueError("Action invalide: impossible de retirer plus que le nombre restant.")

        # appliquer le coup
        self.nb -= action

        # si nb == 0, le joueur qui vient de jouer PERD
        if self.nb == 0:
            self.is_over = True
            self.loser = self.current_player
            self.winner = self.player2 if self.current_player == self.player1 else self.player1
            return

        # sinon on change de joueur
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1

    def play(self):
        """
        Joue une partie complète (utile pour tests / IA / console).
        En Tkinter, on jouera plutôt coup par coup via step().
        """
        self.reset()

        while not self.is_over:
            self.display()

            action = self.current_player.play()

            # Si c'est un humain Tkinter et qu'il n'a pas de choix, on ne peut pas continuer ici
            if action is None:
                raise RuntimeError(
                    "Human.play() a retourné None. "
                    "En Tkinter, utilise Game.step(action) depuis le contrôleur."
                )

            try:
                self.step(action)
            except ValueError:
                # si action invalide, on redemande un coup
                continue

        # fin de partie: stats
        self.winner.win()
        self.loser.lose()

        self.display()
        return self.winner
