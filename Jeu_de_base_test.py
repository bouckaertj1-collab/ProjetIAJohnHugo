from random import randint,sample
class Player:
    def __init__(self,game=None):
        self.game = game
        self.nb_wins = 0
        self.nb_loses = 0

    @property
    def nb_games(self):
      return self.nb_wins + self.nb_loses

    @staticmethod
    def play():
        return randint(1,3)
        
    def win(self):
        self.nb_wins += 1

    def lose(self):
        self.nb_loses += 1

class Human(Player):
    def __init__(self,game):
        super().__init__(game,0,0) 

    @staticmethod
    def play():
        return int(input("Entrez un nombre entre 1 et 3"))
    
class Game:
    def __init__(self,nb_matches,player1,player2,displayable=True):
        self.nb_matches = nb_matches
        self.original_nb = nb_matches 
        self.player1 = player1
        self.player2 = player2
        self.displayable = displayable
        self.shuffle()

    def shuffle(self):
        sample((self.player1,self.player2),2)

    def reset(self):
        self.nb_matches = self.original_nb
        self.shuffle((self.player1,self.player2))

    def display(self):
        pass

    def step(action):
        pass 
    
    def play():
        pass     