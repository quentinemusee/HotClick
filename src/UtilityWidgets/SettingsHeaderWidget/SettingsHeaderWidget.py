#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    SettingsHeaderWidget class used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

# =--------------= #
# Libraries import #
# =--------------= #

from PySide6.QtGui           import QCloseEvent
from PySide6.QtWidgets       import QLabel, QVBoxLayout, QWidget
from src.config              import STYLE
import src.utils                 as utils

# =----------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =------------------------= #
# SettingsHeaderWidget class #
# =------------------------= #

class SettingsHeaderWidget(QWidget):
    """
    Theme SettingsHeader Widget class that allow to
    describe a Menu within the SettingsDialog's menu content widget.
    """

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self, title: str, description: str, parent: QWidget) -> None:
        """
        Initializer method.

        :param title: The title of the SettingsHeaderWidget.
        :type title: str
        :param description: The description of the SettingsHeaderWidget.
        :type description: str
        :param parent: The parent of the SettingsHeaderWidget to instantiate.
        :type parent: QWidget
        """

        # Call the super class's initializer method.
        super().__init__(parent)

        # Set the straight-forward attributes.
        self._title: str = title
        self._description: str = description

        # Initialize the UI.
        self._init_ui()

        # Initialize the UI style.
        self.set_stylesheets()

    def _init_ui(self) -> None:
        """Initialize the UI of the ThemeWidget instance itself."""

        # Initialize the main SettingsHeaderWidget's layout.
        main_layout: QVBoxLayout = QVBoxLayout(self)

        # Create the header label.
        self._header_label: QLabel = QLabel(text=self._title, parent=self)

        # Add the header label to the main layout.
        main_layout.addWidget(self._header_label)

        # Create the description label.
        self._description_label: QLabel = QLabel(text=self._description, parent=self)
        self._description_label.setWordWrap(True)

        # Add the description label to the main layout.
        main_layout.addWidget(self._description_label)

    # ================== #
    # Overridden methods #
    # ================== #

    def closeEvent(self, event: QCloseEvent):
        """
        Overridden closeEvent method.
        This method is called when the ThemeWidget instance get closed.

        :param PySide6.QtGui.QCloseEvent event: The QCloseEvent received.
        """

        # Handle the event.
        super().closeEvent(event)

        # Clear the SettingsDialog's layout.
        utils.clear_layout(self.layout())

    # =================== #
    # Stylesheets methods #
    # =================== #

    def _set_header_label_stylesheet(self) -> None:
        """Set the header label Stylesheet."""

        # Set the StyleSheet.
        self._header_label.setStyleSheet(f"""
            QLabel {{
                color: {STYLE["color"]};    
                font-size: 18px;
                font-weight: bold;
            }}
        """)

    def _set_description_label_stylesheet(self) -> None:
        """Set the description label Stylesheet."""

        # Set the StyleSheet.
        self._description_label.setStyleSheet(f"""
            QLabel {{
                color: {STYLE["color"]};   
                font-size: 16px;
                font-style: italic;
                font-weight: bolder;
                margin-top: 15px;
                margin-bottom: 20px;
            }}
        """)

    def set_stylesheets(self) -> None:
        """Call every set_stylesheet method."""

        # Set the StyleSheets.
        self._set_header_label_stylesheet()
        self._set_description_label_stylesheet()

# =---------------------------------------------------------------------------------------------------------= #
