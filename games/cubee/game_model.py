import random
from collections import deque

try:
    from games.cubee.player import Player
except ModuleNotFoundError:
    from player import Player


class GameModel:
    """
    Modèle principal du jeu Cubee.
    """

    MOVES = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }

    def __init__(self, player1, player2, size: int = 5):
        self.size = size

        if isinstance(player1, Player):
            self.player1 = player1
        else:
            self.player1 = Player(player1, 1, (0, 0))

        if isinstance(player2, Player):
            self.player2 = player2
        else:
            self.player2 = Player(player2, 2, (size - 1, size - 1))

        self.player1.game_model = self
        self.player2.game_model = self

        self.board = []
        self.is_game_over = False
        self.current_player = None
        self.player_turn = 1
        self.turn = 1
        self.winner = None
        self.loser = None
        self.score = (0, 0)

        self.reset()

    def reset(self) -> None:
        """Réinitialise complètement la partie."""
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]

        self.player1.position = (0, 0)
        self.player2.position = (self.size - 1, self.size - 1)

        self.board[0][0] = 1
        self.board[self.size - 1][self.size - 1] = 2

        self.is_game_over = False
        self.winner = None
        self.loser = None

        self.shuffle_player()
        self.update_score()

    def shuffle_player(self) -> None:
        """Choisit aléatoirement le joueur qui commence."""
        self.current_player = random.choice([self.player1, self.player2])
        self.player_turn = self.current_player.player_id
        self.turn = self.player_turn

    def get_player_by_id(self, player_id: int) -> Player | None:
        """Retourne le joueur correspondant à l'id donné."""
        if player_id == 1:
            return self.player1
        if player_id == 2:
            return self.player2
        return None

    def get_current_player(self) -> Player:
        """Retourne le joueur courant."""
        return self.get_player_by_id(self.player_turn)

    def get_opponent(self, player: Player | None = None) -> Player:
        """Retourne l'adversaire du joueur donné."""
        if player is None:
            player = self.get_current_player()
        return self.player2 if player.player_id == 1 else self.player1

    def is_in_bounds(self, position: tuple[int, int]) -> bool:
        """Vérifie qu'une position est dans le plateau."""
        row, col = position
        return 0 <= row < self.size and 0 <= col < self.size

    def get_target_position(self, move: str, player: Player | None = None) -> tuple[int, int] | None:
        """Calcule la position cible après un déplacement."""
        if player is None:
            player = self.get_current_player()

        if move not in self.MOVES:
            return None

        row, col = player.position
        d_row, d_col = self.MOVES[move]
        return row + d_row, col + d_col

    def is_legal_move(self, move: str, player: Player | None = None) -> bool:
        """
        Vérifie si un déplacement est légal.

        Un joueur peut aller :
        - sur une case libre
        - sur une case qui lui appartient déjà

        Un joueur ne peut pas aller :
        - hors du plateau
        - sur une case adverse
        """
        if self.is_game_over:
            return False

        if player is None:
            player = self.get_current_player()

        new_position = self.get_target_position(move, player)
        if new_position is None:
            return False

        if not self.is_in_bounds(new_position):
            return False

        row, col = new_position
        target_cell = self.board[row][col]
        opponent = self.get_opponent(player)

        return target_cell != opponent.player_id

    def available_moves(self, player: Player | None = None) -> list[str]:
        """Retourne la liste des coups possibles."""
        if player is None:
            player = self.get_current_player()

        moves = []
        for move in self.MOVES:
            if self.is_legal_move(move, player):
                moves.append(move)
        return moves

    def available_cell(self) -> list[tuple[int, int]]:
        """Retourne la liste des cases libres."""
        free_cells = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0:
                    free_cells.append((row, col))
        return free_cells

    def next_player(self) -> None:
        """Passe au joueur suivant."""
        if self.player_turn == 1:
            self.player_turn = 2
            self.current_player = self.player2
        else:
            self.player_turn = 1
            self.current_player = self.player1

        self.turn = self.player_turn

    def update_score(self) -> None:
        """Recalcule le score à partir du plateau."""
        score_p1 = 0
        score_p2 = 0

        for row in self.board:
            for cell in row:
                if cell == 1:
                    score_p1 += 1
                elif cell == 2:
                    score_p2 += 1

        self.score = (score_p1, score_p2)

    def end_game(self) -> None:
        """Termine la partie et détermine le gagnant."""
        self.is_game_over = True
        self.update_score()

        if self.score[0] > self.score[1]:
            self.winner = self.player1
            self.loser = self.player2
        elif self.score[1] > self.score[0]:
            self.winner = self.player2
            self.loser = self.player1
        else:
            self.winner = None
            self.loser = None

    def check_game_over(self) -> bool:
        """
        Vérifie si la partie est terminée.

        La partie s'arrête :
        - s'il n'y a plus de case libre
        - ou si les deux joueurs sont bloqués
        """
        if len(self.available_cell()) == 0:
            self.end_game()
            return True

        if len(self.available_moves(self.player1)) == 0 and len(self.available_moves(self.player2)) == 0:
            self.end_game()
            return True

        return False

    def check_enclosure(self) -> None:
        """
        Détecte les enclos de manière compatible avec les tests de l'énoncé.

        On considère que le joueur `player_turn` vient de jouer.
        On cherche alors toutes les cases encore atteignables par l'adversaire
        en traversant :
        - ses propres cases
        - les cases libres

        Toutes les cases libres non atteignables sont capturées
        par le joueur courant.
        """
        current_player = self.get_player_by_id(self.player_turn)
        opponent = self.get_opponent(current_player)

        reachable = [[False for _ in range(self.size)] for _ in range(self.size)]
        queue = deque()

        start_row, start_col = opponent.position
        queue.append((start_row, start_col))
        reachable[start_row][start_col] = True

        while queue:
            row, col = queue.popleft()

            for d_row, d_col in self.MOVES.values():
                new_row = row + d_row
                new_col = col + d_col
                new_position = (new_row, new_col)

                if not self.is_in_bounds(new_position):
                    continue

                if reachable[new_row][new_col]:
                    continue

                cell_value = self.board[new_row][new_col]

                if cell_value == 0 or cell_value == opponent.player_id:
                    reachable[new_row][new_col] = True
                    queue.append((new_row, new_col))

        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0 and not reachable[row][col]:
                    self.board[row][col] = current_player.player_id

    def step(self, move: str) -> bool:
        """
        Exécute un tour de jeu.

        Retourne True si le coup a été joué, sinon False.
        """
        if self.is_game_over:
            return False

        current_player = self.get_current_player()

        if not self.is_legal_move(move, current_player):
            return False

        new_row, new_col = self.get_target_position(move, current_player)
        current_player.position = (new_row, new_col)
        self.board[new_row][new_col] = current_player.player_id

        self.check_enclosure()
        self.update_score()

        if self.check_game_over():
            return True

        self.next_player()
        self.check_game_over()

        return True

    def board_to_string(self) -> str:
        """Convertit le plateau en chaîne compacte."""
        return "".join(str(cell) for row in self.board for cell in row)

    def get_state_DTO(self) -> dict:
        """Retourne l'état courant du jeu sous forme de dictionnaire."""
        return {
            "size": self.size,
            "board": self.board_to_string(),
            "turn": self.turn,
            "pos_p1": self.player1.position,
            "pos_p2": self.player2.position,
            "is_game_over": self.is_game_over,
            "score": self.score,
            "winner": self.winner.name if self.winner else None,
            "loser": self.loser.name if self.loser else None,
        }