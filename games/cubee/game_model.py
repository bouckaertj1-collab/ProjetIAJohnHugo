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

        self.left_column_mask = 0
        for index in range(self.size**2):
            if index % self.size == 0:
                self.left_column_mask |= (1 << index)

        self.right_column_mask = 0
        for index in range(self.size**2):
                if index % self.size == self.size - 1:
                    self.right_column_mask |= (1 << index)    

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
        
        pos = self.current_player.position
        target = self.compute_target(move)

        if self.current_player == self.player1:
            self.player1_board |= (1 << pos)
            self.player1.position = target
        else:
            self.player2_board |= (1 << pos)
            self.player2.position = target
            
        self.update_score()

        if self.is_game_over:
            self.end_game()
        else:
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
        
        pos = self.current_player.position

        target = self.compute_target(move)

        if move == "left" and self.is_left_edge(pos):
            return False
        
        if move == "right" and self.is_right_edge(pos):
            return False

        if not self.is_in_bounds(target):
            return False
        
        if self._is_opponent_cell(target,self.current_player):
            return False
        
        return True
        
    def next_player(self) -> None:
        """Passe au joueur suivant."""
        if self.player_turn == 1:
            self.player_turn = 2
        else:
            self.player_turn = 1

    def update_score(self) -> None:
        """Recalcule le score à partir du plateau."""
        self.score = ((self.player1_board | (1 << self.player1.position)).bit_count() 
                    ,(self.player2_board |(1 << self.player2.position)).bit_count())

    @property
    def is_game_over(self) -> bool:
        """
          Vérifie si la partie est terminée.

        La partie s'arrête :
        - s'il n'y a plus de case libre
        - ou si les deux joueurs sont bloqués
        """
        return self.occupied_tiles == self.board_mask or self._both_players_blocked()
        
    def check_enclosure(self) -> None:
        """
        
        """
        opponent = self.get_opponent(self.current_player)
        start = opponent.position
        to_explore = (1 << start) 
        visited |= (1 << start)
        free_cells = ~self.occupied_tiles & self.board_mask
        opponent_cells = self.get_opponent_board(opponent)  
        traversable = free_cells | opponent_cells
        
        while to_explore:

            up = to_explore >> self.size
            down = to_explore << self.size
            left =  (to_explore >> 1) & ~self.right_column_mask
            right = (to_explore << 1) & ~self.left_column_mask

            next_to_explore = (up | down | left | right) & traversable
        
            to_explore = next_to_explore & ~visited
            visited |= to_explore

        captured = free_cells & ~visited

        if self.current_player is self.player1:
            self.player1_board |= captured
        else:           
            self.player2_board |= captured
        self.update_score()

    def is_valid_neighbor(self,current_tile,move,neighbor,reachable,opponent):
        if move == "left" and self.is_left_edge(current_tile):
            return False
        if move == "right" and self.is_right_edge(current_tile):
            return False
        if not self.is_in_bounds(neighbor):
            return False
        if reachable & (1 << neighbor):
            return False
        if self._is_free_cell(neighbor) or self._is_opponent_cell(neighbor,opponent):
            return True
        
        return False

    def _is_free_cell(self,index):
        return self.occupied_tiles & (1 << index) == 0
    
    def _is_opponent_cell(self,index,player):
       return (self.get_opponent_board(player) & (1 << index)) != 0
    
    def get_opponent(self,player):

        if player is self.player1:
            return self.player2
        elif player is self.player2:
            return self.player1
        else:
            raise ValueError("Le joueur actuel n'est pas une instance de joueur")
    
    def get_opponent_board(self,player):

        if player is self.player1:
            return self.player2_board 
        elif player is self.player2:
            return self.player1_board
        else:
            raise ValueError("Le joueur actuel n'est pas une instance de joueur et ne possède pas de plateau")
    
    def is_in_bounds(self,index):
        return 0 <= index < self.size**2
        
    def is_left_edge(self,index):
        return index % self.size == 0

    def is_right_edge(self,index):
        return index % self.size == self.size - 1
    
    def _both_players_blocked(self):
            old_player_turn = self.player_turn
            try:
                self.player_turn = 1
                valid_moves_j1 = self.get_valid_moves()

                self.player_turn = 2
                valid_moves_j2 = self.get_valid_moves()

                return not (valid_moves_j1 or valid_moves_j2) 
            finally:
                self.player_turn = old_player_turn

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