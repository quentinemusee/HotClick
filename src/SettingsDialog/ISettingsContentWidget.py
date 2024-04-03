#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    ISettingsContentWidget class used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

# =--------------= #
# Libraries import #
# =--------------= #

from typing                  import Any, Dict, List, Optional, Union
from src.UtilityWidgets      import SettingsHeaderWidget, YesNoCancelDialog, YesNoCancelEnum
from PySide6.QtCore          import Qt
from PySide6.QtGui           import QCloseEvent
from PySide6.QtWidgets       import QPushButton, QVBoxLayout, QWidget
from src.config              import CONFIG, STYLE
import copy
import src.config                as config
import src.utils                 as utils

# =--------------------------------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =--------------------------= #
# ISettingsContentWidget class #
# =--------------------------= #

class ISettingsContentWidget(QWidget):
    """
    The ISettingsContent Widget class that allow to edit
    the configuration used by the whole HotClick software.
    This class is inherited by every SettingsDialog
    menu content widget.
    """

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self, title: str, description: str, parent: QWidget) -> None:
        """
         Initializer method.

         :param title: The title of the ThemeWidget.
         :type title: str
         :param description: The description of the ThemeWidget.
         :type description: str
         :param parent: The parent of the ThemeWidget to instantiate.
         :type parent: QWidget
         """

        # Call the super class's initializer method.
        super().__init__(parent)

        # Set the straight-forward attributes.
        self._title: str = title
        self._description: str = description
        self._settings_changed: bool = False
        self._old_config: Dict[
            str, Union[int, str, List[int], Dict[str, Dict[str, Union[str, int]]], Dict[str, str]]
        ] = copy.deepcopy(CONFIG)
        self._old_style: Dict[str, Union[str, Dict[str, str]]] = copy.deepcopy(STYLE)

        # The init_ui method should be called directly
        # in the child classes init method.

    def _init_ui(self) -> None:
        """Initialize the UI of the ISettingsContentWidget instance itself."""

        # Initialize the main SettingsHeaderWidget's layout.
        self._main_layout: QVBoxLayout = QVBoxLayout(self)

        # Create the SettingsHeaderWidget.
        self._settings_header_widget: SettingsHeaderWidget = SettingsHeaderWidget(
            title=self._title,
            description=self._description,
            parent=self,
        )

        # Add the header label to the main layout.
        self._main_layout.addWidget(self._settings_header_widget)

        # Declare a None save button.
        self._save_button: Optional[QPushButton] = None

    # ================== #
    # Overridden methods #
    # ================== #

    def closeEvent(self, event: QCloseEvent):
        """
        Overridden closeEvent method.
        This method is called when the SettingsDialog instance get closed.

        :param PySide6.QtGui.QCloseEvent event: The QCloseEvent received.
        """

        # Call the super class's closeEvent method.
        super().closeEvent(event)

        # Clear the SettingsDialog's layout.
        utils.clear_layout(self.layout())

    # ============= #
    # Public method #
    # ============= #

    def ask_for_saving(self) -> bool:
        """
        Open a YesNoCancel Dialog to ask for saving the style changes.
        The boolean result indicate if the Cancel button has been clicked.

        :returns: True if the Cancel button has been clicked.
        :rtype: bool
        """

        # Declare a flag to return depending on is_valid
        # method result and the clicked button on the
        # YesNoCancel dialog.
        default_no_res: bool = False

        # If the is_valid method return False, open a YesNoCancel
        # to confirm for unsave the changes.
        if not self._is_valid():
            yes_no_cancel_dialog: YesNoCancelDialog = YesNoCancelDialog(
                "Invalid Settings",
                "Do you want to leave without saving ?",
                no_cancel_button=True,
                parent=self
            )
            yes_no_cancel_dialog.exec()

            # The behavior depends on the res value.
            if yes_no_cancel_dialog.result == YesNoCancelEnum.NO:
                # Return here.
                return True
            default_no_res = False
        else:
            # Open a YesNoCancel Dialog to apply the style changes.
            yes_no_cancel_dialog: YesNoCancelDialog = YesNoCancelDialog(
                "Confirmation",
                "Do you confirm your changes ?",
                parent=self
            )
            yes_no_cancel_dialog.exec()

            # Retrieve the result.
            res: YesNoCancelEnum = yes_no_cancel_dialog.result

            # The behavior depends on the res value.
            if res == YesNoCancelEnum.CANCEL:
                # Return True.
                return True

            elif res == YesNoCancelEnum.YES:
                # Save every change.
                self._save()

                # Return False.
                return False

        # Reset the CONFIG and STYLE dictionaries.
        utils.update_dict(CONFIG, value=self._old_config)
        utils.update_dict(STYLE, value=self._old_style)

        # Reset the settings_changed, old_config and old_style attributes.
        self._settings_changed = False
        self._old_config = copy.deepcopy(CONFIG)
        self._old_style = copy.deepcopy(STYLE)

        # Reset the widgets content.
        self._reset_widgets()

        # Update the whole HotClick software stylesheets.
        parent: Optional[QWidget] = self
        while parent.parent() is not None:
            parent = parent.parent()
        if hasattr(parent, "set_stylesheets"):
            parent.set_stylesheets()

        # Return default_no_res.
        return default_no_res

    def settings_just_changed(self, *widgets_content: Any) -> None:
        """
        Set the settings_changed attribute to True and update the save button
        being disabled or not.
        This method can be overridden to update the CONFIG/STYLE dictionaries
        when the widget changes, by calling this method directly when it happens.

        :param widgets_content: The changed row of widgets from the config_list.
        :type widgets_content: Tuple[QLabel or QPushButtonShortcut, QPushButtonShortcut]
        """

        # Update the save button being disabled or not.
        self._save_button.setEnabled(self._is_valid())

        # Update the settings attribute.
        self._settings_changed = True

    # ============== #
    # Private method #
    # ============== #

    def _add_save_button(self) -> None:
        """Add a save button to the bottom-right corner of the ISettingsContentWidget's main layout."""

        # Create the save button.
        self._save_button = QPushButton(
            text="Save",
            parent=self
        )
        self._save_button.clicked.connect(self._save)
        self._save_button.setEnabled(self._is_valid())

        # Add the save button to the main layout.
        self._main_layout.addWidget(self._save_button, alignment=Qt.AlignBottom | Qt.AlignRight)

    def _reset_widgets(self) -> None:
        """
        Reset the widgets of the ISettingsContentWidget.
        This method should be overridden in child classes.
        """
        pass

    def _is_valid(self) -> bool:
        """
        Return True if the content of the ISettingsContentWidget is valid and can be saved.
        This method should probably be overridden in child classes.
        """
        return True

    # =============== #
    # Callback method #
    # =============== #

    def _save(self) -> None:
        """Callback method when the save button get clicked."""

        # Reset the settings_changed, old_config and old_style attributes.
        self._settings_changed = False
        self._old_config = copy.deepcopy(CONFIG)
        self._old_style = copy.deepcopy(STYLE)

        # Save the style.
        config.save_style()

    # ================== #
    # Stylesheets method #
    # ================== #

    def _set_settings_header_widget_stylesheet(self) -> None:
        """Set the settings header widget Stylesheet."""

        # Set the Stylesheet.
        self._settings_header_widget.set_stylesheets()

    def _set_save_button_stylesheet(self) -> None:
        """Set the save button Stylesheet."""

        # Set the Stylesheet.
        self._save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #4a4a4a, stop: 0.5 #3a3a3a, stop: 1 #4a4a4a);
                border-radius: 10px;
                border: 2px solid #3a3a3a;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }}
            
            QPushButton:hover {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #5a5a5a, stop: 0.5 #4a4a4a, stop: 1 #5a5a5a);
                border: 2px solid #4a4a4a;
            }}
            
            QPushButton:pressed {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #3a3a3a, stop: 0.5 #2a2a2a, stop: 1 #3a3a3a);
                border: 2px solid #2a2a2a;
            }}
            
            QPushButton:disabled {{
                background-color: #808080;
                border: 2px solid #606060;
                color: #a0a0a0;
            }}
        """)

    def set_stylesheets(self) -> None:
        """Call every set_stylesheet method."""

        # Set the StyleSheets.
        self._set_settings_header_widget_stylesheet()
        self._set_save_button_stylesheet()

    # ============= #
    # Getter method #
    # ============= #

    @property
    def settings_changed(self) -> bool:
        """
        Getter method for the settings_changed attribute.

        :return: The style_changed attribute.
        :rtype: bool
        """
        return self._settings_changed

# =--------------------------------------------------------------------------------------------= #
