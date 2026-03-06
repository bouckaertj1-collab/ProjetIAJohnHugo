class Player:
    """
    Représente un joueur de Cubee.
    """

    def __init__(self, name, player_id, position, color=None):
        self.name = name
        self.player_id = player_id
        self.position = position
        self.color = color

        self.nb_win = 0
        self.nb_lose = 0
        self.nb_draw = 0
        self.nb_game = 0

        self.game_model = None

    def play(self):
        """Incrémente le nombre de parties jouées."""
        self.nb_game += 1

    def win(self):
        """Enregistre une victoire."""
        self.nb_win += 1
        self.nb_game += 1

    def lose(self):
        """Enregistre une défaite."""
        self.nb_lose += 1
        self.nb_game += 1

    def draw(self):
        """Enregistre un match nul."""
        self.nb_draw += 1
        self.nb_game += 1

    def __repr__(self):
        return f"Player(name={self.name}, id={self.player_id}, position={self.position})"