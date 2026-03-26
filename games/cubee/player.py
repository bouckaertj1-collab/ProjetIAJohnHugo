import random


class Player:
    """
    Représente un joueur de Cubee.
    """

    def __init__(self, name, position, color=None):
        self.name = name
        self.position = position
        self.color = color

        self.nb_win = 0
        self.nb_lose = 0
        self.nb_draw = 0
        self.nb_game = 0

    def is_ai(self):
        return False

    def play(self, game_model):
        """Retourne le coup à jouer."""
        return None

    def win(self):
        self.nb_win += 1
        self.nb_game += 1

    def lose(self):
        self.nb_lose += 1
        self.nb_game += 1

    def draw(self):
        self.nb_draw += 1
        self.nb_game += 1

    def __repr__(self):
        return f"Player(name={self.name}, position={self.position})"

class RandomAgent(Player):
    """
    IA très simple qui joue un coup aléatoire.
    """

    def is_ai(self):
        return True

    def play(self, game_model):
        moves = game_model.available_moves()
        if not moves:
            return None
        return random.choice(moves)
    

class AI(Player):
    def __init__(self, name, position, color=None):
        super().__init__(name, position, color)
        self.alpha = 0.05
        self.gamma = 0.5 # importance que tu donnes à la récompense future
        self.epsilon = 0.9
        self.q_table = ()
        self.reward = None #
        "Pour examen : Analyser alpha, et gamma"

    def exploit(self):
        """  
        actions possibles : haut,bas,gauche,droite
        état : pos j1, pos j2, board, tour (à qui de jouer)
        stockage état ? => string mettre en 1er le tour du joueur car cela élimine déjà le plus recherche dans la DB
        voir comment faire avec bitboard peut être intéressant au niveau calcul
        """
        """
        Partie apprentissage : pas de stockage, on apprend direct dans la Q-TABLE :"
        stocker état précédent + action précédente"
        ensuite fonctionnement de V-Fonction

        """
    def play(self):
        pass

    """Attention DAO passe par le controller pour envoyer au GameModel ou IA et inversément"""
