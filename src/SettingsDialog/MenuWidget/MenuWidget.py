#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    MenuWidget class used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

# =--------------= #
# Libraries import #
# =--------------= #

from typing             import Callable, Dict
from PySide6.QtCore     import Qt
from PySide6.QtGui      import QCloseEvent
from PySide6.QtWidgets  import QPushButton, QVBoxLayout, QWidget
from src.config         import STYLE
import src.utils            as utils

# =-----------------------------------------------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =--------------= #
# MenuWidget class #
# =--------------= #

class MenuWidget(QWidget):
    """
    MenuWidget Widget class that contains the
    different buttons for displaying the
    various settings accessible from the SettingsDialog.
    """

    # ================== #
    # Initializer method #
    # ================== #

    def __init__(self, parent: QWidget, menu_selected_callback: Callable[[QPushButton], None]) -> None:
        """Initializer method."""

        # Call the super class's initializer method.
        super().__init__(parent)

        # Set the straight-forward attributes.
        self._menu_selected_callback: Callable[[QPushButton], None] = menu_selected_callback
        self._menu_buttons: Dict[str, QPushButton] = {}

        # Initialize the UI.
        self._init_ui()

        # Initialize the UI style.
        self.set_stylesheets()

    def _init_ui(self) -> None:
        """Initialize the UI of the MenuWidget instance itself."""

        # Create the main layout of the MenuWidget.
        main_layout: QVBoxLayout = QVBoxLayout()

        # Create a Theme button.
        theme_button = QPushButton("Theme", self)
        theme_button.setCheckable(True)
        theme_button.clicked.connect(lambda: self._menu_selected_callback(theme_button))

        # Add the Theme button to the menu_buttons list.
        self._menu_buttons["Theme"] = theme_button

        # Add the Theme button to the menu layout, aligned to the top.
        main_layout.addWidget(theme_button, alignment=Qt.AlignTop)

        # Create a Shortcut button.
        shortcut_button = QPushButton("Shortcut", self)
        shortcut_button.setCheckable(True)
        shortcut_button.clicked.connect(lambda: self._menu_selected_callback(shortcut_button))

        # Add the Shortcut button to the menu_buttons list.
        self._menu_buttons["Shortcut"] = shortcut_button

        # Add the Shortcut button to the menu layout, aligned to the top.
        main_layout.addWidget(shortcut_button, alignment=Qt.AlignTop)

        # Add a stretch to the main layout
        # to ensure the buttons are at its top.
        main_layout.addStretch()

        # Set the main layout to the MenuWidget.
        self.setLayout(main_layout)

    # ================== #
    # Overridden methods #
    # ================== #

    def closeEvent(self, event: QCloseEvent):
        """
        Overridden closeEvent method.
        This method is called when the SettingsDialog instance get closed.

        :param PySide6.QtGui.QCloseEvent event: The QCloseEvent received.
        """

        # Handle the event.
        super().closeEvent(event)

        # Clear the MenuWidget's layout.
        utils.clear_layout(self.layout())

    # =================== #
    # Stylesheets methods #
    # =================== #

    def _set_theme_widget_stylesheet(self) -> None:
        """Set the SettingsDialog StyleSheet."""

        # Set the StyleSheet.
        self.setStyleSheet(f"""
            background-color: {STYLE["background-color"]};
        """)

    @staticmethod
    def _set_menu_button_stylesheet(menu_button: QPushButton) -> None:
        """
        Set the given menu button StyleSheet.

        :param menu_button: The style button to set the StyleSheet.
        :type menu_button: PySide6.QtWidgets.QPushButton
        """

        # Set the StyleSheet depending on the button being checked.
        if menu_button.isChecked():
            menu_button.setStyleSheet(f"""\
                QPushButton {{
                    background-color: {STYLE["QPushButton:checked"]["background-color"]};
                    color: {STYLE["color"]};
                    font-family: {STYLE["font-family"]};
                    font-size: 16px;
                    width: 250px;
                    border: 2px solid rgb(255, 255, 255);
                    border-radius: 10px;
                    padding: 2px;
                    margin-left: 10px;
                    margin-right: 10px;
                }}
            """)
        else:
            menu_button.setStyleSheet(f"""\
                QPushButton {{
                    background-color: {STYLE["background-color"]};
                    color: {STYLE["color"]};
                    font-family: {STYLE["font-family"]};
                    font-size: 16px;
                    width: 250px;
                    border: 2px solid rgb(255, 255, 255);
                    border-radius: 10px;
                    padding: 2px;
                    margin-left: 10px;
                    margin-right: 10px;
                }}
            """)

    def set_stylesheets(self) -> None:
        """Call every set_stylesheet method."""

        # Set the StyleSheets.
        self._set_theme_widget_stylesheet()
        for button in self._menu_buttons.values():
            MenuWidget._set_menu_button_stylesheet(button)

    # ============= #
    # Getter method #
    # ============= #

    @property
    def menu_buttons(self) -> Dict[str, QPushButton]:
        """
        Getter method for the menu_buttons attribute.

        :return: The menu_buttons attribute.
        :rtype: Dict[str, QPushButton]
        """
        return self._menu_buttons