#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This program is a HUD allowing to
    bind hotkeys to click on screen.

     _____________________________________________________________________
    | VERSION | DATE YYYY-MM-DD |                 CONTENT                 |
    |=====================================================================|
    |  0.1.0  |      2024-03-12 | Initial release.                        |
    |---------|-----------------|-----------------------------------------|
    |  0.2.0  |      2024-03-13 | Add a mechanism to deactivate hotkeys   |
    |         |                 | when pressing the "right shift" key.    |
    |         |                 | Double the sleep time before hotkey     |
    |         |                 | click to ensure the click isn't done    |
    |         |                 | too early.                              |
    |         |                 | Handle hotkeys's ellipse with a width   |
    |         |                 | different than its height.              |
    |         |                 | Fix the hotkey's position from being    |
    |         |                 | offseted after several HUD restoration. |
    |---------|-----------------|-----------------------------------------|
    |  0.3.0  |      2024-03-13 | Add a mechanism to select the config    |
    |         |                 | file when several are available.        |
    |         |                 | Add a relative path config file parsing |
    |         |                 | mechanism.                              |
    |---------|-----------------|-----------------------------------------|
    |  0.3.1  |      2024-03-16 | Migrated from PyQt5 to PySide6.         |
    |---------|-----------------|-----------------------------------------|
    |  0.3.2  |      2024-03-17 | Migrated the unhook function to a       |
    |         |                 | utils.py dedicated file.                |
    |         |                 | Migrated the logger content to a        |
    |         |                 | logger.py dedicated file.               |
    |         |                 | Migrated the CircleWindow content to a  |
    |         |                 | circle_window.py dedicated file.        |
    |         |                 | Migrated the MainWindow content to a    |
    |         |                 | main_window.py dedicated file.          |
    |---------|-----------------|-----------------------------------------|
    |  0.4.0  |      2024-03-17 | Improve the relative path config file   |
    |         |                 | parsing mechanism.                      |
    |---------|-----------------|-----------------------------------------|
    |  0.5.0  |      2024-03-17 | Improve the UI design of the software.  |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from main_window       import MainWindow
from PySide6.QtWidgets import QApplication
import os

# =------------------------------------= #


# =--------= #
# Authorship #
# =--------= #

__author__       = "Quentin Raimbaud"
__contact__      = "quentin.raimbaud.contact@gmail.com"
__date__         = "2024-03-17"
__license__      = "LGPL"
__maintainer__   = "Quentin Raimbaud"
__status__       = "Development"
__todo__         = [
    "Add a hotkey mapping mechanism",
    "Make the hotkeys label fit their CircleWindow",
    "Click as long as the hotkey is pressed"
]
__version__      = "0.5.0"

# =-------------------------------------------------= #


# =-----------= #
# Main function #
# =-----------= #

def main() -> None:
    """Main function."""

    # Disable the high DPI scaling.
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = '0'

    # Initialize the QApplication.
    app = QApplication([])

    # Initialize the MainWindow and show it.
    main_window = MainWindow()
    main_window.show()

    # Run the QApplication.
    app.exec()

# =-------------------------------------------= #


#   Run the main function is
# this script is run directly.
if __name__ == '__main__':
    main()
