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

        self.player1 = player1 if isinstance(player1, Player) else Player(player1, (0, 0))
        self.player2 = player2 if isinstance(player2, Player) else Player(player2, (size - 1, size - 1))

        self.board = []
        self.is_game_over = False
        self.player_turn = 1
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
        self.player_turn = random.choice([1, 2])
        self.winner = None
        self.loser = None

        self.update_score()

    def get_current_player(self) -> Player:
        """Retourne le joueur courant."""
        return self.player1 if self.player_turn == 1 else self.player2

    def get_opponent(self, player: Player | None = None) -> Player:
        """Retourne l'adversaire du joueur donné."""
        if player is None:
            player = self.get_current_player()
        return self.player2 if player == self.player1 else self.player1

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

        target_position = self.get_target_position(move, player)
        if target_position is None or not self.is_in_bounds(target_position):
            return False

        row, col = target_position
        target_cell = self.board[row][col]
        opponent_value = 2 if player == self.player1 else 1

        return target_cell != opponent_value

    def available_moves(self, player: Player | None = None) -> list[str]:
        """Retourne la liste des coups possibles."""
        if player is None:
            player = self.get_current_player()
        return [move for move in self.MOVES if self.is_legal_move(move, player)]

    def next_player(self) -> None:
        """Passe au joueur suivant."""
        self.player_turn = 2 if self.player_turn == 1 else 1

    def update_score(self) -> None:
        """Recalcule le score à partir du plateau."""
        flat_board = [cell for row in self.board for cell in row]
        self.score = (flat_board.count(1), flat_board.count(2))

    def end_game(self) -> None:
        """Termine la partie et détermine le gagnant."""
        self.is_game_over = True

        if self.score[0] > self.score[1]:
            self.winner = self.player1
            self.loser = self.player2
            self.player1.win()
            self.player2.lose()
        elif self.score[1] > self.score[0]:
            self.winner = self.player2
            self.loser = self.player1
            self.player2.win()
            self.player1.lose()
        else:
            self.winner = None
            self.loser = None
            self.player1.draw()
            self.player2.draw()
            
    def check_game_over(self) -> bool:
        """
        Vérifie si la partie est terminée.

        La partie s'arrête :
        - s'il n'y a plus de case libre
        - ou si les deux joueurs sont bloqués
        """
        if not any(0 in row for row in self.board):
            self.end_game()
            return True

        if not self.available_moves(self.player1) and not self.available_moves(self.player2):
            self.end_game()
            return True

        return False

    def check_enclosure(self) -> None:
        """
        Détecte les enclos.

        On considère que le joueur courant vient de jouer.
        On cherche alors toutes les cases encore atteignables par l'adversaire
        en traversant :
        - ses propres cases
        - les cases libres

        Toutes les cases libres non atteignables sont capturées
        par le joueur courant.
        """
        current_player = self.get_current_player()
        opponent = self.get_opponent(current_player)

        current_value = self.player_turn
        opponent_value = 2 if current_value == 1 else 1

        reachable = [[False for _ in range(self.size)] for _ in range(self.size)]
        queue = deque([opponent.position])

        start_row, start_col = opponent.position
        reachable[start_row][start_col] = True

        while queue:
            row, col = queue.popleft()

            for d_row, d_col in self.MOVES.values():
                new_row, new_col = row + d_row, col + d_col

                if not self.is_in_bounds((new_row, new_col)):
                    continue

                if reachable[new_row][new_col]:
                    continue

                if self.board[new_row][new_col] in (0, opponent_value):
                    reachable[new_row][new_col] = True
                    queue.append((new_row, new_col))

        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0 and not reachable[row][col]:
                    self.board[row][col] = current_value

    def step(self, move: str) -> bool:
        if self.is_game_over:
            return False

        current_player = self.get_current_player()

        if not self.is_legal_move(move, current_player):
            return False

        new_row, new_col = self.get_target_position(move, current_player)
        current_player.position = (new_row, new_col)
        self.board[new_row][new_col] = self.player_turn

        self.check_enclosure()
        self.update_score()

        if not self.check_game_over():
            self.next_player()

        return True

    def board_to_string(self) -> str:
        """Convertit le plateau en chaîne compacte."""
        return "".join(str(cell) for row in self.board for cell in row)

    def get_state_DTO(self) -> dict:
        """Retourne l'état courant du jeu sous forme de dictionnaire."""
        return {
            "size": self.size,
            "board": self.board_to_string(),
            "player_turn": self.player_turn,
            "pos_p1": self.player1.position,
            "pos_p2": self.player2.position,
            "is_game_over": self.is_game_over,
            "score": self.score,
            "winner": self.winner.name if self.winner else None,
            "loser": self.loser.name if self.loser else None,
        }