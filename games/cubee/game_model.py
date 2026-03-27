import random
try:
    from games.cubee.player import Player
except ModuleNotFoundError:
    from player import Player


class GameModel:
    """
    Game Model of Cubee based on bitBoard to represent de board of the game.
    """

    def __init__(self, player1:Player, player2:Player, size: int = 5):

        self.size = size
        self.player1 = player1
        self.player2 = player2
        self.player1_pos = 0
        self.player2_pos = (self.size**2)-1

        if hasattr(self.player1, "game_model"):
            self.player1.game_model = self

        if hasattr(self.player2, "game_model"):
            self.player2.game_model = self

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
        self.player1_pos = 0
        self.player2_pos = (self.size**2) - 1
        self.player1_board = 0
        self.player2_board = 0
        self.player1_board |= (1 << self.player1_pos )
        self.player2_board |= (1 << self.player2_pos )
        self.winner = None
        self.loser = None
        self.player_turn = random.choice([1, 2])
        self.update_score()

    @property
    def occupied_tiles(self):
        return self.player1_board | self.player2_board 
    
    @property #for test enclosures
    def board(self):
        board = [[0]*self.size for _ in range(self.size)]

        for i in range(self.size * self.size):
            row = i // self.size
            col = i % self.size

            if (self.player1_board >> i) & 1:
                board[row][col] = 1
            elif (self.player2_board >> i) & 1:
                board[row][col] = 2

        return board

    @board.setter #for test enclosures
    def board(self, value):
        self.player1_board = 0
        self.player2_board = 0

        for row in range(self.size):
            for col in range(self.size):
                i = row * self.size + col

                if value[row][col] == 1:
                    self.player1_board |= (1 << i)
                    if self.player1_pos is None:
                            self.player1_pos = i

                elif value[row][col] == 2:
                    self.player2_board |= (1 << i)
                    if self.player2_pos is None:
                            self.player2_pos = i

    def compute_target(self,move):
        """
        Compute a target position from de current position of the player and a move, and return it
        Args : self,move
        Return : target index
        """
        return self.current_position() + self.moves.get(move)

    def step(self, move: str) -> bool:
        """

        """
        if not self.is_legal_move(move):
            return False
        
        target = self.compute_target(move)
         
        board = self.current_board()
        board |= (1<< target)

        self.set_current_board(board)
        self.set_current_position(target)

        self.update_score()
        self.check_enclosure()
        self.next_player()

        return True
    
    def set_current_board(self,new_board):
        if self.player_turn == 1:
            self.player1_board = new_board
        else:
            self.player2_board = new_board

    def set_current_position(self,pos):
        if self.player_turn == 1:
            self.player1_pos = pos
        else:
            self.player2_pos = pos


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

        Precondition : The input move is among the moves in the attribute 'self.moves'
        Postcondition : return a boolean value depending the given move

        """
        if self.is_game_over:
            return False
        
        pos = self.current_position()

        target = self.compute_target(move)

        if move == "left" and self.is_left_edge(pos):
            return False
        
        if move == "right" and self.is_right_edge(pos):
            return False

        if not self.is_in_bounds(target):
            return False
        
        if (self.opponent_board() & (1 << target)) != 0:
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
        self.score = (self.player1_board .bit_count(),self.player2_board .bit_count())

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
        opponent_cells = self.opponent_board()
        to_explore = opponent_cells
        reachable = opponent_cells
        free_cells = ~self.occupied_tiles & self.board_mask
        
        allowed = free_cells | opponent_cells
        
        while to_explore:

            up = to_explore >> self.size
            down = to_explore << self.size
            left =  (to_explore >> 1) & ~self.right_column_mask
            right = (to_explore << 1) & ~self.left_column_mask

            next_to_explore = (up | down | left | right) & allowed
        
            to_explore = next_to_explore & ~reachable
            reachable |= to_explore

        captured = free_cells & ~reachable

        board = self.current_board()
        board |= captured 
        self.set_current_board(board)
       
        self.update_score()
    
    
    def opponent_board(self):
        return self.player2_board if self.player_turn == 1 else self.player1_board
    
    def current_board(self):
        return self.player1_board if self.player_turn == 1 else self.player2_board
    
    def current_position(self):
        return self.player1_pos if self.player_turn == 1 else self.player2_pos
    
    def opponent_position(self):
        return self.player2_pos if self.player_turn == 1 else self.player1_pos

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
            "board": self.board,
            "pos_p1": self.player1_pos,
            "pos_p2": self.player2_pos,
            "is_game_over": self.is_game_over,
            "score": self.score,
            "winner": self.winner.name if self.winner else None,
            "loser": self.loser.name if self.loser else None,
        }