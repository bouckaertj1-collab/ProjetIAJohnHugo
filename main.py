"""
Main entry point of the application.

This module starts the graphical launcher of the project.
The launcher allows the user to select and start available games.
"""

from launcher.controller import LauncherController

if __name__ == "__main__":
    LauncherController().run()


