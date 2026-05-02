"""
Main entry point of the application.

This module starts the graphical launcher of the project.
The launcher allows the user to select and start available games.
"""

from launcher.controller import LauncherController
from games.PixelKart.dao.q_table_dao import init_db

if __name__ == "__main__":
    init_db()
    LauncherController().run()


