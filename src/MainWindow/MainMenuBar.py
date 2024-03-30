#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    MainMenuBar class used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

# =--------------= #
# Libraries import #
# =--------------= #

from PySide6.QtGui     import QAction
from PySide6.QtWidgets import QMenu, QMenuBar, QWidget
from src.config        import STYLE
import typing

# =------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =-----------------= #
# MainStatusBar class #
# =-----------------= #

class MainMenuBar(QMenuBar):
    """
    Circle Window class that represent a painted movable
    frameless circle containing an editable hotkey.
    """

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        """
        Initializer method.
        If parent is provided, set such a parent to the MainToolbar.

        :param parent: The optional parent of the MainToolbar to instantiate. By default, None.
        :type parent: QWidget or None
        """

        # Call the super class's initializer method.
        super().__init__(parent)

        # Initialize the UI.
        self._init_ui()

        # Initialize the UI style.
        self.set_stylesheets()

    def _init_ui(self) -> None:
        """Initialize the UI of the MainMenuBar instance itself."""

        # Initialize the "File" menu.
        file_menu: QMenu = self.addMenu("File")

        # Initialize and add the "New" action.
        self._new_action: QAction = QAction("New", self)
        self._new_action.setStatusTip("Create and use a new config file")
        file_menu.addAction(self._new_action)

        # Initialize and add the "Open" action.
        self._open_action: QAction = QAction("Open", self)
        self._open_action.setStatusTip("Open an existing config file")
        file_menu.addAction(self._open_action)

        # Initialize and add the "Save as" action.
        self._save_as_action: QAction = QAction("Save As...", self)
        self._save_as_action.setStatusTip("Save the config file in use as...")
        file_menu.addAction(self._save_as_action)

        # Initialize and add the "Settings" action.
        self._settings_menu_action: QAction = QAction("Settings", self)
        self._settings_menu_action.setStatusTip("Configure the software settings")
        self.addAction(self._settings_menu_action)

    # ============== #
    # Public methods #
    # ============== #

    def set_menu_callbacks(
            self,
            file_new_callback: typing.Callable[..., typing.Any],
            file_open_callback: typing.Callable[..., typing.Any],
            file_save_as_callback: typing.Callable[..., typing.Any],
            settings_callback: typing.Callable[..., typing.Any]
    ) -> None:
        """
        Set the given callback to the associated MenuBar buttons.

        :param file_new_callback: The optional "File -> New" button callback.
        :type file_new_callback: typing.Callable[..., typing.Any]
        :param file_open_callback: The optional "File -> Open" button callback.
        :type file_open_callback: typing.Callable[..., typing.Any]=
        :param file_save_as_callback: The optional "File -> Save As" button callback.
        :type file_save_as_callback: typing.Callable[..., typing.Any]
        :param settings_callback: The optional "Settings" button \
callback.
        :type settings_callback: typing.Callable[..., typing.Any]
        """

        # Set the given callbacks.
        self._new_action.triggered.connect(file_new_callback)
        self._open_action.triggered.connect(file_open_callback)
        self._save_as_action.triggered.connect(file_save_as_callback)
        self._settings_menu_action.triggered.connect(settings_callback)

    # =================== #
    # Stylesheets methods #
    # =================== #

    def _set_main_menu_bar_stylesheet(self) -> None:
        """Set the MainMenuBar StyleSheet."""

        # Set the StyleSheet.
        self.setStyleSheet(f"""
            background-color: {STYLE["Custom"]["middleground-color"]};
        """)

    def set_stylesheets(self) -> None:
        """Call every set_stylesheet method."""

        # Set the MainMenuBar StyleSheets.
        self._set_main_menu_bar_stylesheet()

# =-----------------------------------------------------------------------------------------= #
