#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    SettingsDialog class used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

# =--------------= #
# Libraries import #
# =--------------= #

from typing                   import Any, Tuple
from .CustomKeyMappingDialog  import CustomKeyMappingDialog
from ..ISettingsContentWidget import ISettingsContentWidget
from src.UtilityWidgets       import QConfigList, QPushButtonShortcut
from PySide6.QtCore           import Qt
from PySide6.QtWidgets        import QLabel, QPushButton, QVBoxLayout, QWidget
from src.config               import CONFIG, STYLE
import src.config                 as config
import src.utils                  as utils

# =------------------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =--------------------= #
# KeyMappingWidget class #
# =--------------------= #

class KeyMappingWidget(ISettingsContentWidget):
    """
    KeyMapping Widget that allow to edit
    the key mapping used by the whole HotClick software.
    """

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self, parent: QWidget) -> None:
        """
        Initializer method.

        :param parent: The parent of the SettingsDialog to instantiate.
        :type parent: QWidget
        """

        # Call the super class's initializer method.
        super().__init__(
            title="Application shortcuts",
            description="Customize the way your keyboard control the application: "
                        "Edit both the builtin action shortcuts and the custom key mapping you would like to use "
                        "when starting the program for your very personal needs.",
            parent=parent
        )

        # Initialize the UI.
        self._init_ui()

        # Initialize the UI style.
        self.set_stylesheets()

    def _init_ui(self) -> None:
        """Initialize the UI of the SettingsDialog instance itself."""

        # Call the super class's init_ui method.
        super()._init_ui()

        # Retrieve the main layout inherited from ISettingsContentWidget.
        main_layout: QVBoxLayout = self.layout()

        # Create the QConfigList.
        self._config_list: QConfigList = QConfigList(
            n=2,
            header_texts=("Action", "Shortcut"),
            no_duplicates=[2],
            initial=tuple(
                (
                    QLabel(text=bind),
                    QPushButtonShortcut(text=CONFIG["shortcuts"]["builtin"][bind]),
                )
                for bind in CONFIG["shortcuts"]["builtin"]
            ),
            widget_edited_callback=(lambda _action, *widgets: self.settings_just_changed(*widgets)),
            no_buttons=True,
            no_verif=True,
            style=STYLE,
            parent=self
        )

        # Add the QConfigList to the main layout.
        main_layout.addWidget(self._config_list)

        # Create the custom key mapping button.
        self._custom_key_mapping_button: QPushButton = QPushButton(
            text="Customize your custom key mapping",
            parent=self
        )
        self._custom_key_mapping_button.clicked.connect(self._open_custom_key_mapping_dialog)

        # Add the custom key mapping button to the main layout.
        main_layout.addWidget(self._custom_key_mapping_button, alignment=Qt.AlignRight)

        # Create and add the save button to the main layout.
        self._add_save_button()

    # ================== #
    # Overridden methods #
    # ================== #

    def settings_just_changed(self, *widgets_content: Any) -> None:
        """
        Set the _settings_changed attribute to True and update the CONFIG dictionary.

        :param widgets_content: The changed row of widgets from the config_list.
        :type widgets_content: Tuple[QLabel or QPushButtonShortcut, QPushButtonShortcut]
        """

        # Call the super class's settings_just_changed method.
        super().settings_just_changed(*widgets_content)

        # Update the CONFIG dictionary.
        utils.update_dict(CONFIG, "shortcuts", "builtin", widgets_content[0], value=widgets_content[1])

        # Save the CONFIG dictionary.
        config.save_config()

    def _reset_widgets(self) -> None:
        """Reset the widgets of the ISettingsContentWidget."""
        for row_widgets in self._config_list.widgets:
            setattr(row_widgets[1], "shortcut", (CONFIG["shortcuts"]["builtin"][getattr(row_widgets[0], "text")()]))
            getattr(row_widgets[1], "setText")(CONFIG["shortcuts"]["builtin"][getattr(row_widgets[0], "text")()])

    def _is_valid(self) -> bool:
        """
        Return True if the content of the ISettingsContentWidget is valid and can be saved.
        This method should be overridden in child classes.
        """
        return self._config_list.is_valid

    # ================ #
    # Callback methods #
    # ================ #

    def _open_custom_key_mapping_dialog(self) -> None:
        """Open the custom key mapping dialog menu."""

        # Initialize the CustomKeyMappingDialog.
        custom_key_mapping_dialog: CustomKeyMappingDialog = CustomKeyMappingDialog(self)
        custom_key_mapping_dialog.open()

    # =================== #
    # Stylesheets methods #
    # =================== #

    def _set_key_mapping_widget_stylesheet(self) -> None:
        """Set the KeyMappingWidget StyleSheet."""

        # Set the StyleSheet.
        self.setStyleSheet(f"""
            background-color: {STYLE["Custom"]["middleground-color"]};
        """)

    def _set_config_list_stylesheet(self) -> None:
        """Set the config list StyleSheet."""

        # Set the StyleSheet.
        self._config_list.set_stylesheets()

    def _set_custom_key_mapping_button_stylesheet(self) -> None:
        """Set the custom key mapping Stylesheet."""

        # Set the Stylesheet.
        self._custom_key_mapping_button.setStyleSheet(f"""
            QPushButton {{
                color: {STYLE["color"]};    
                font-size: 18px;
                font-style: italic;
                font-weight: bolder;
                border: 2px solid rgb(255, 255, 255);
                border-radius: 10px;
                padding: 10px;
                margin-top: 15px;
                margin-bottom: 15px;
            }}
        """)

    def set_stylesheets(self) -> None:
        """Call every set_stylesheet method."""

        # Set the SettingsDialog StyleSheets.
        super().set_stylesheets()
        self._set_key_mapping_widget_stylesheet()
        self._set_config_list_stylesheet()
        self._set_custom_key_mapping_button_stylesheet()

# =------------------------------------------------------------------------------------------------------------------= #
