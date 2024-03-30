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

from typing                  import Optional, Union
from .KeyMappingWidget       import KeyMappingWidget
from .MenuWidget             import MenuWidget
from .ThemeWidget            import ThemeWidget
from PySide6.QtCore          import Qt
from PySide6.QtGui           import QCloseEvent, QResizeEvent
from PySide6.QtWidgets       import QDialog, QPushButton, QSplitter, QStackedLayout, QVBoxLayout, QWidget
from src.config              import CONFIG, STYLE
import src.config                as config
import src.utils                 as utils

# =---------------------------------------------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =------------------= #
# SettingsDialog class #
# =------------------= #

class SettingsDialog(QDialog):
    """
    Settings Dialog class that allow to edit
    the different settings available within
    the whole HotClick software.
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
        super().__init__(parent)

        # Initialize the straight-forward attribute.
        self._settings_changed: bool = False

        # Initialize the UI.
        self._init_ui()

        # Initialize the UI style.
        self.set_stylesheets()

    def _init_ui(self) -> None:
        """Initialize the UI of the SettingsDialog instance itself."""

        # Set the title of the Window.
        self.setWindowTitle("Settings")

        # Set the layout of the SettingsDialog.
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create the QSplitter.
        self._splitter: QSplitter = QSplitter(Qt.Horizontal, parent=self)
        layout.addWidget(self._splitter)

        # Create the menu and menu content widgets.
        self._menu_widget: MenuWidget = MenuWidget(self, self._menu_button_selected)
        self._menu_content_widget: Union[QWidget, ThemeWidget, KeyMappingWidget] = QWidget(self)

        # Create the menu content stacked layout.
        self._menu_content_stacked_layout: QStackedLayout = QStackedLayout(self)

        # Add the different widgets to the stacked layout.
        self._menu_content_stacked_layout.addWidget(QWidget(self))           # No selection.
        self._menu_content_stacked_layout.addWidget(ThemeWidget(self))       # Theme widget.
        self._menu_content_stacked_layout.addWidget(KeyMappingWidget(self))  # Shortcut widget.

        # Set the menu_content_stacked_layout as the menu_content_widget's layout.
        self._menu_content_widget.setLayout(self._menu_content_stacked_layout)

        # Add the widgets to the splitter.
        self._splitter.addWidget(self._menu_widget)
        self._splitter.addWidget(self._menu_content_widget)

        # Ensure the splitter won't make its widget collapse.
        self._splitter.setCollapsible(0, False)

        # Set the geometry whole Dialog as well as
        # for the two widgets contained inside the splitter.
        self.setMinimumSize(1000, 562)

        # If last_setting_menu is not None, call
        # the associated callback method directly.
        if CONFIG["last_setting_menu"] is not None:
            last_setting_menu_button: QPushButton = self._menu_widget.menu_buttons[CONFIG["last_setting_menu"]]
            last_setting_menu_button.setChecked(True)
            self._menu_button_selected(last_setting_menu_button, direct_call=True)

    # ================== #
    # Overridden methods #
    # ================== #

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Overridden resizeEvent method.
        This method is called when the SettingsDialog instance get resized.

        :param PySide6.QtGui.QResizeEvent event: The QMouseEvent received.
        """

        # Call the super class resizeEvent method.
        super().resizeEvent(event)

        # Update the size restriction of the splitter widgets.
        self._update_spliter_widets_size_restrictions()

    def closeEvent(self, event: QCloseEvent):
        """
        Overridden closeEvent method.
        This method is called when the SettingsDialog instance get closed.

        :param PySide6.QtGui.QCloseEvent event: The QCloseEvent received.
        """

        # Before to go further, ensure that if any unsaved
        # changes has been performed on the config or style.
        menu_content_widget: Union[
            QWidget,
            ThemeWidget,
            KeyMappingWidget
        ] = self._menu_content_stacked_layout.currentWidget()

        # If any unsaved changes has been performed
        # on the config or style, ask for saving them.
        if hasattr(menu_content_widget, "settings_changed") and menu_content_widget.settings_changed:
            # If the Cancel button get clicked, ignore the event.
            if menu_content_widget.ask_for_saving():
                event.ignore()
                return

        # Call the super class's closeEvent method.
        super().closeEvent(event)

        # Call the MainWindow's update_builtin_shortcuts method.
        if hasattr(self.parent(), "update_builtin_shortcuts"):
            self.parent().update_builtin_shortcuts()

        # Clear the SettingsDialog's layout.
        utils.clear_layout(self.layout())

    # =============== #
    # Private methods #
    # =============== #

    def _update_spliter_widets_size_restrictions(self) -> None:
        """Update the size restrictions of the splitter's widgets."""

        # Update the two widgets of the
        # Splitter minimum and maximum sizes.
        self._menu_widget.setMinimumWidth(int(self.width()/5))
        self._menu_widget.setMaximumWidth(int(1.5*int(self.width()/5)))
        self._menu_content_widget.setMinimumWidth(int(3.5*int(self.width()/5)))
        self._menu_content_widget.setMaximumWidth(4*int(self.width()/5))

    # ================ #
    # Callback methods #
    # ================ #

    def _menu_button_selected(self, button: QPushButton, direct_call: bool = False) -> None:
        """
        Callback method used when any menu button get clicked.
        If direct_call is True, don't uncheck the previously checked button.

        :param PySide6.QtWidgets.QPushButton button: The PushButton clicked.
        :param bool direct_call: If True, don't uncheck the previously checked button. By default, False
        """

        # If the given button is already checked, uncheck it and return here.
        if not button.isChecked():
            button.setChecked(not button.isChecked())
            return

        # Before to go further, ensure that if any unsaved
        # changes has been performed on the config or style.
        menu_content_widget: Union[
            QWidget,
            ThemeWidget,
            KeyMappingWidget
        ] = self._menu_content_stacked_layout.currentWidget()

        # Retrieve the last setting menu if it exists.
        last_setting_menu_str: Optional[str] = CONFIG.get("last_setting_menu", None)

        # If any unsaved changes has been performed
        # on the config or style, ask for saving them.
        if hasattr(menu_content_widget, "settings_changed") and menu_content_widget.settings_changed:
            # If the Cancel button get clicked, ignore the event.
            if menu_content_widget.ask_for_saving():
                button.setChecked(not button.isChecked())
                return

        # Uncheck the previously checked menu if required.
        if not direct_call and last_setting_menu_str is not None:
            last_setting_menu: QPushButton = self._menu_widget.menu_buttons[last_setting_menu_str]
            last_setting_menu.setChecked(not last_setting_menu.isChecked())
            last_setting_menu.update()

        # Update the last_setting_menu attribute.
        CONFIG["last_setting_menu"] = button.text()

        # Save the CONFIG dictionary.
        config.save_config()

        # Update the SettingsDialog display.
        self.set_stylesheets()

        # Display the corresponding menu on the menu
        # content widget and update its StyleSheet.
        button_text: str = button.text()
        if button_text == "Theme":
            self._menu_content_stacked_layout.setCurrentIndex(1)
        elif button_text == "Shortcut":
            self._menu_content_stacked_layout.setCurrentIndex(2)

    # =================== #
    # Stylesheets methods #
    # =================== #

    def _set_settings_stylesheet(self) -> None:
        """Set the SettingsDialog StyleSheet."""

        # Set the StyleSheet.
        self.setStyleSheet(f"""
            background-color: {STYLE["background-color"]};
        """)

    def _set_menu_content_widget_stylesheet(self) -> None:
        """
        Set the menu content widget StyleSheet.
        This style may be overridden once a menu
        content is displayed.
        """

        # Set the StyleSheet.
        self._menu_content_widget.setStyleSheet(f"""
            background-color: {STYLE["Custom"]["middleground-color"]};
        """)

    def set_stylesheets(self) -> None:
        """Call every set_stylesheet method."""

        # Set the SettingsDialog StyleSheets.
        self._set_settings_stylesheet()
        self._set_menu_content_widget_stylesheet()

        # Set the MenuWidget Stylesheets.
        self._menu_widget.set_stylesheets()

        # Set the currently displayed menu content widget Stylesheets.
        menu_content_widget = self._menu_content_stacked_layout.currentWidget()
        if hasattr(menu_content_widget, "set_stylesheets"):
            menu_content_widget.set_stylesheets()

# =------------------------------------------------------------------------------------------------------------------= #
