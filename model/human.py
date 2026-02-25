"""
Human player implementations.
"""

from model.player import Player


class Human(Player):
    """
    Human player for console-based games.

    The player is asked to choose a number of matches to take via standard input.
    """

    def play(self, max_take: int = 3) -> int:
        """
        Ask the user to choose how many matches to take.

        The choice must be an integer between 1 and 3.
        The user is prompted again until a valid input is provided.

        Returns:
            int: The number of matches chosen by the player (1, 2, 3).
        """
        choice = None

        while choice not in range(1, max_take + 1):
            try:
                choice = int(input(f"{self.name}, take 1 to {max_take} matches: "))
            except ValueError:
                choice = None

            if choice not in range(1, max_take + 1):
                print(f"Invalid choice. Please enter a number between 1 and {max_take}.")

        return choice


class HumanGUI(Player):
    """
    Human player for the Tkinter GUI.

    This class represents a human player interacting through a graphical
    interface. The player does not choose actions using the `play()` method;
    instead, actions are provided by the controller in response to button
    clicks in the GUI.
    """

    pass
