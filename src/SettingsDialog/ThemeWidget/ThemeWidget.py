#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    ThemeWidget class used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

# =--------------= #
# Libraries import #
# =--------------= #

from typing                   import Dict, Optional, Tuple
from ..ISettingsContentWidget import ISettingsContentWidget
from PySide6.QtGui            import QColor
from PySide6.QtWidgets        import QColorDialog, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from src.config               import STYLE
import src.config                 as config
import src.utils                  as utils

# =-------------------------------------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =---------------= #
# ThemeWidget class #
# =---------------= #

class ThemeWidget(ISettingsContentWidget):
    """
    The Theme Widget class that allow to edit
    the theme used by the whole HotClick software.
    """

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self, parent: QWidget) -> None:
        """
        Initializer method.

        :param parent: The parent of the ThemeWidget to instantiate.
        :type parent: QWidget
        """

        # Call the super class's initializer method.
        super().__init__(
            title="Application theme",
            description="Customize the application's theme: "
                        "Edit the colors of the different element constituting the software "
                        "to make yourself comfortable.",
            parent=parent
        )

        # Set the straight-forward attributes.
        self._style_buttons: Dict[QPushButton, Tuple[str, ...]] = {}

        # Initialize the UI.
        self._init_ui()

        # Initialize the UI style.
        self.set_stylesheets()

    def _init_ui(self) -> None:
        """Initialize the UI of the ThemeWidget instance itself."""

        # Call the super class's init_ui method.
        super()._init_ui()

        # Retrieve the main layout inherited from ISettingsContentWidget.
        main_layout: QVBoxLayout = self.layout()

        # Initialize every style button.
        for styles in [
            [("background-color", "Background color"), ("Custom", "middleground-color", "Middleground color")],
            [("Custom", "selected-background-color", "Selected background color"), ("color", "Text color")],
            [
                ("QStatusBar", "background-color", "Status bar background color"),
                ("QPushButton:checked", "background-color", "Selected settings menu button background color")
            ],
            [
                ("QPushButton", "background-color", "Buttons background color"),
                ("QPushButton:pressed", "background-color", "Pressed buttons background color")
            ],
        ]:
            # Create a horizontal layout for the style button to be created.
            horizontal_layout: QHBoxLayout = QHBoxLayout(self)

            # Create the style buttons.
            for style in styles:
                style_button: QPushButton = QPushButton(style[-1], self)

                # Connect the style button to the style_button_clicked callback method.
                style_button.clicked.connect(
                    lambda checked=False, style_button_=style_button, style_=style[:-1]: self._style_button_clicked(
                        style_button_
                    )
                )

                # Add the style button to the style_button dictionary.
                self._style_buttons[style_button] = style[:-1]

                # Add the style button to the horizontal layout
                horizontal_layout.addWidget(style_button)

            # Add the horizontal layout to the main layout.
            main_layout.addLayout(horizontal_layout)

        # Add a stretch to the main_layout to push
        # its horizontal layout to the top.
        main_layout.addStretch()

        # Create and add the save button to the main layout.
        self._add_save_button()

    # =================== #
    # Stylesheets methods #
    # =================== #

    def _set_theme_widget_stylesheet(self) -> None:
        """Set the SettingsDialog StyleSheet."""

        # Set the StyleSheet.
        self.setStyleSheet(f"""
            background-color: {STYLE["Custom"]["middleground-color"]};
        """)

    def _set_style_button_stylesheet(self, style_button: QPushButton) -> None:
        """
        Set the given style button StyleSheet.

        :param style_button: The style button to set the StyleSheet.
        :type style_button: PySide6.QtWidgets.QPushButton
        """

        # Set the StyleSheet.
        background_color: str = utils.access_dict(STYLE, *(self._style_buttons[style_button]))
        style_button.setStyleSheet(f"""\
            QPushButton {{
                background-color: {background_color};
                color: {utils.opposite_hex_color(background_color)};
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
        super().set_stylesheets()
        self._set_theme_widget_stylesheet()
        for button in self._style_buttons.keys():
            self._set_style_button_stylesheet(button)

    # ================ #
    # Callback methods #
    # ================ #

    def _style_button_clicked(self, style_button: QPushButton) -> None:
        """
        Callback method used when any style button get clicked.

        :param style_button: The clicked style button QPushButton.
        :type style_button: PySide6.QtWidgets.QPushButton
        """

        # Retrieve the keys to access such a style button's property.
        keys: Tuple[str, ...] = self._style_buttons[style_button]

        # Open a QColorDialog and wait for a color to be selected.
        color: QColor = QColorDialog.getColor(
            initial=utils.access_dict(STYLE, *keys)
        )

        # If the QColorDialog has been closed, return here.
        if not color.isValid():
            return

        # Update the style dictionary.
        utils.update_dict(STYLE, *keys, value=color.name())

        # Save the style file.
        config.save_style()

        # Update the whole HotClick software stylesheets.
        parent: Optional[QWidget] = self
        while parent.parent() is not None:
            parent = parent.parent()
        if hasattr(parent, "set_stylesheets"):
            parent.set_stylesheets()

        # Update the settings_changes attribute.
        self._settings_changed = True

# =---------------------------------------------------------------------------------------------------------= #
