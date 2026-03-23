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

    def __init__(self, player1:Player, player2:Player, size: int = 5):

        self.size = size
        self.player1.game_model = self
        self.player2.game_model = self
        self.player1 = player1
        self.player2 = player2
        self.board_mask = (1 << (self.size**2)) - 1 
       
        self.moves = {
        "up": -self.size,
        "down": self.size,
        "left": - 1,
        "right": 1,
        }

        
        self.player_turn = 1
        self.winner = None
        self.loser = None
        self.score = (0, 0)
        self.reset()

    @property
    def current_player(self) -> Player:
        """Return the player whose turn it is."""
        return self.player1 if self.player_turn == 1 else self.player2
    
    def reset(self) -> None:
        """Réinitialise complètement la partie."""
        self.player1_board = 0
        self.player2_board = 0
        self.player1.position = 0 
        self.player2.position = (self.size**2)-1
        self.winner = None
        self.loser = None
        self.player_turn = random.choice([1, 2])
        self.update_score()

    @property
    def occupied_tiles(self):
        return self.player1_board | self.player2_board | (1 << self.player1.position) | (1 << self.player2.position)

    def compute_target(self,move):
        """
        Compute a target position from de current position of the player and a move, and return it
        Args : self,move
        Return : target index
        """
        return self.current_player.position + self.moves.get(move)

    def get_player_by_id(self, player_id: int) -> Player | None:
        """Retourne le joueur correspondant à l'id donné."""
        if player_id == 1:
            return self.player1
        if player_id == 2:
            return self.player2
        return None

    def step(self, move: str) -> bool:
        """

        """
        if not self.is_legal_move(move):
            return False
        else:

            pos = self.current_player.position

            target = self.compute_target(move)

            if self.current_player == self.player1:
                self.player1_board |= (1 << pos)
                self.player1.position = target
            else:
                self.player2_board |= (1 << pos)
                self.player2.position = target
            
            self.update_score()
            self.is_game_over()
            self.next_player()

            return True
    
    def get_valid_moves(self):
        """
        Return the valid moves in the available moves
        a move is valid if it satisfies the "is_legal_move function"
        """
        return [move for move in self.moves if self.is_legal_move(move)]
        

    def is_legal_move(self, move: str) -> bool:
        """
        Check if a move is legal

        a player can move to:
        - no occupied tiles
        - his own tiles

        a player can't move to :
        - out of the board
        - opponent tiles

        In the 3rd statement : Check if the target position doesn't exceed the size of the board
        In the 4th and 5th statement : Check if the move is not out of bound when it does go left or right
        In the last statement : check if the the target is not on occupied tiles

        Precondition : The input move is among the moves in the attribute 'self.moves'
        Postcondition : return a boolean value depending the given move

        """
        if self.is_game_over:
            return False

        if self.current_player == self.player1:
            opponent_board = self.player2_board
            opponent_pos = self.player2.position
        else:
            opponent_board = self.player1_board
            opponent_pos = self.player1.position

        pos = self.current_player.position

        target = self.compute_target(move)

        if target < 0 or target >= self.size**2:
            return False
        
        if move == "left" and pos % self.size == 0:
            return False
        
        if move == "right" and pos % self.size == self.size - 1:
            return False
        
        if opponent_board & (1 << target) != 0:
            return False
        
        if target == opponent_pos:
            return False
        
        return True
        
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
        score1 = int.bit_count(self.player1_board) + self.player1.position
        score2 = int.bit_count(self.player2_board) + self.player2.position
        self.score = (score1,score2)

    def end_game(self) -> None:
        """Termine la partie et détermine le gagnant."""
    pass
    def is_game_over(self) -> bool:
        """
        Vérifie si la partie est terminée.

        La partie s'arrête :
        - s'il n'y a plus de case libre
        - ou si les deux joueurs sont bloqués
        """
    pass

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