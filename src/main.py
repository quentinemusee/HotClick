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
    |         |                 | Handle hotkeys ellipse with a width     |
    |         |                 | different from its height.              |
    |         |                 | Fix the hotkey position from being      |
    |         |                 | offset after several HUD restoration.   |
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
    |         |                 | CircleWindow.py dedicated file.        |
    |         |                 | Migrated the MainWindow content to a    |
    |         |                 | MainWindow.py dedicated file.          |
    |---------|-----------------|-----------------------------------------|
    |  0.4.0  |      2024-03-17 | Improve the relative path config file   |
    |         |                 | parsing mechanism.                      |
    |---------|-----------------|-----------------------------------------|
    |  0.5.0  |      2024-03-17 | Improve the UI design of the software.  |
    |---------|-----------------|-----------------------------------------|
    |  0.6.0  |      2024-03-21 | Add a BarMenu to the main UI containing |
    |         |                 | a "File -> New", "File -> Open",        |
    |         |                 | "File -> Save As" and "Settings"        |
    |         |                 | buttons.                                |
    |         |                 | Add a IMainWindow class that contains   |
    |         |                 | the main window's UI without any        |
    |         |                 | callback so this class can run in       |
    |         |                 | standalone.                             |
    |         |                 | Add a StatusBar linked to the main UI   |
    |         |                 | with the logger, with the text color    |
    |         |                 | adapted to the log level.               |
    |         |                 | New hotkeys come with a brand new and   |
    |         |                 | not already used default hotkey.        |
    |         |                 | Duplicate hotkeys verification is now   |
    |         |                 | performed when editing a hotkey and not |
    |         |                 | when starting the main hotkey routine   |
    |         |                 | anymore.                                |
    |         |                 | Create and use a new config file when   |
    |         |                 | the one used at start-up is corrupted.  |
    |         |                 | The config file is now updated each     |
    |         |                 | time the user's doing an action.        |
    |         |                 | New hotkey default position will be the |
    |         |                 | last position of a moved CircleWindow.  |
    |         |                 | Add a fully functional Settings menu.   |
    |         |                 | Add an icon to the software.            |
    |         |                 | Very huge refactor.                     |
    |---------|-----------------|-----------------------------------------|
    |  0.7.0  |      2024-03-29 | Refactor the directory structure of the |
    |         |                 | project, creating a directory per       |
    |         |                 | section to make it way more readable.   |
    |         |                 | Introduce the QConfigList widget.       |
    |         |                 | Introduce the QPushButtonShortcut       |
    |         |                 | widget.                                 |
    |         |                 | Add a garbage mechanism to delete       |
    |         |                 | unused widgets anymore.                 |
    |         |                 | Hotkeys's click stops when the hotkey   |
    |         |                 | is released.                            |
    |         |                 | Biggest refactor ever done.             |
    |         |                 | Fix the style settings being applied    |
    |         |                 | even when clicking on "No" to the       |
    |         |                 | YesNoCancelDialog.                      |
    |---------|-----------------|-----------------------------------------|
    |  0.8.0  |      2024-03-31 | Refactor the way the hotkeys are        |
    |         |                 | handled by hooking a callback method    |
    |         |                 | infinitely but controlling the handling |
    |         |                 | via a global boolean variable.          |
    |         |                 | Edit the way QPushButtonShortcuts       |
    |         |                 | handle new shortcut to use the same     |
    |         |                 | method as the MainWindow. This          |
    |         |                 | implementation result in not using Qt's |
    |         |                 | keyboard methods but the python"s       |
    |         |                 | keyboard library, which handle global   |
    |         |                 | keyboard event.                         |
    |         |                 | Remove the dumb Qt's KeySequence to     |
    |         |                 | keyboard's keys from version 0.7.0.     |
    |         |                 | When clicking te save button from the   |
    |         |                 | Custom Shortcuts menu, close the        |
    |         |                 | CustomKeyMappingDialog.                 |
    |         |                 | Add a new Builtin shortcut "Restore     |
    |         |                 | Application" for restoring the software |
    |         |                 | when the main hotkey routine is         |
    |         |                 | running or when the software is         |
    |         |                 | minimized.                              |
    |         |                 | Add two new options to the "Theme"      |
    |         |                 | settings menu.                          |
    |         |                 | Don't consider the typical failed       |
    |         |                 | unhook as critical anymore.             |
    |         |                 | Fix the CircleWindows from keeping the  |
    |         |                 | hotclick editing focus even after being |
    |         |                 | deleted.                                |
    |         |                 | Fix the Hotclicks from being offset to  |
    |         |                 | the bottom-right corner of the          |
    |         |                 | CircleWindows.                          |
    |         |                 | Fix the builtin shortcuts handling      |
    |         |                 | mouse clicks shortcuts binding.         |
    |---------|-----------------|-----------------------------------------|
    |  0.8.1  |      2024-03-31 | Fix the unsafe integration of the       |
    |         |                 | keyboard library in the                 |
    |         |                 | QPushButtonShortcut file.               |
    |---------|-----------------|-----------------------------------------|
    |  0.8.2  |      2024-03-31 | Fix the QPushButtonShortcut's           |
    |         |                 | KeyboardThread not being able to handle |
    |         |                 | the same hotkey as lastly entered.      |
    |         |                 | Fix the hotkeys clicks event being      |
    |         |                 | stacked when pressing a hotkey          |
    |         |                 | continuously.                           |
    |---------|-----------------|-----------------------------------------|
    |  1.0.0  |      2024-04-03 | Disable the menu settings save buttons  |
    |         |                 | when is_valid method returns False.     |
    |         |                 | Set the CircleWindow minimum size to    |
    |         |                 | 50x50.                                  |
    |         |                 | Make the CircleWindow sizegrip position |
    |         |                 | the closest possible to the ellipse and |
    |         |                 | make its QSizeGrip "hitbox" larger and  |
    |         |                 | way easier to grab/use for resizing.    |
    |         |                 | Make the MainWindow always on top,      |
    |         |                 | along with the CircleWindows.           |
    |         |                 | Get rid of the use of '__' in classes   |
    |         |                 | attributes and methods.                 |
    |         |                 | Make the CircleWindow text font adapted |
    |         |                 | to fit the available space.             |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from src.MainWindow    import MainWindow
from PySide6.QtWidgets import QApplication
import os
import sys

# =------------------------------------= #


# =--------= #
# Authorship #
# =--------= #

__author__       = "Quentin Raimbaud"
__contact__      = "quentin.raimbaud.contact@gmail.com"
__date__         = "2024-04-03"
__license__      = "LGPL-2.1"
__maintainer__   = "Quentin Raimbaud"
__status__       = "Production"
__version__      = "1.0.0"

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
    sys.exit(0)
