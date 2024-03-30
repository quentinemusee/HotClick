#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    CustomKeyMappingDialog class used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

# =--------------= #
# Libraries import #
# =--------------= #

from ...ISettingsContentWidget import ISettingsContentWidget
from src.UtilityWidgets        import QConfigList, QPushButtonShortcut
from PySide6.QtCore            import Qt
from PySide6.QtGui             import QCloseEvent, QKeyEvent
from PySide6.QtWidgets         import QDialog, QVBoxLayout, QWidget
from src.config                import CONFIG, STYLE
import src.utils                   as utils

# =----------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =--------------------------= #
# CustomKeyMappingDialog class #
# =--------------------------= #

class CustomKeyMappingDialog(QDialog):
    """
    CustomKeyMappingDialog Widget that allow to edit the
    custom key mapping used by the whole HotClick software.
    """

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self, parent: QWidget) -> None:
        """Initializer method."""

        # Call the super class's initializer method.
        super().__init__(parent)

        # Initialize the UI.
        self._init_ui()

        # Initialize the UI style.
        self.set_stylesheets()

    def _init_ui(self) -> None:
        """Initialize the UI of the SettingsWidget instance itself."""

        # Set the title of the Window.
        self.setWindowTitle("Custom Key Mapping")

        # Create the main layout.
        main_layout: QVBoxLayout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create the CustomKeyMappingWidget.
        self._custom_key_mapping_widget = CustomKeyMappingWidget(self)

        # Add the CustomKeyMappingWidget to the main layout.
        main_layout.addWidget(self._custom_key_mapping_widget)

        # Set the main layout as the CustomKeyMappingDialog's layout.
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

        # If any unsaved changes has been performed
        # on the config or style, ask for saving them.
        if self._custom_key_mapping_widget.settings_changed:
            # If the Cancel button get clicked, ignore the event.
            if self._custom_key_mapping_widget.ask_for_saving():
                event.ignore()
                return

        # Call the super class's closeEvent method.
        super().closeEvent(event)

        # Clear the SettingsDialog's layout.
        utils.clear_layout(self.layout())

    # =================== #
    # Stylesheets methods #
    # =================== #

    def set_stylesheets(self) -> None:
        """Call every set_stylesheet method."""

        # Set the CustomKeyMappingDialog StyleSheets.
        self._custom_key_mapping_widget.set_stylesheets()

# =--------------------------------------------------------------------= #


# =--------------------------= #
# CustomKeyMappingWidget class #
# =--------------------------= #

class CustomKeyMappingWidget(ISettingsContentWidget):
    """
    CustomKeyMappingWidget Widget that allow to edit the
    custom key mapping used by the whole HotClick software.
    """

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self, parent: QWidget) -> None:
        """Initializer method."""

        # Call the super class's initializer method.
        super().__init__(
            title="Application custom shortcuts",
            description="Customize the way your keyboard control the application: "
                        "Edit the custom key mapping you would like "
                        "to use when starting the program for your very personal needs.",
            parent=parent
        )

        # Initialize the UI.
        self._init_ui()

        # Initialize the UI style.
        self.set_stylesheets()

    def _init_ui(self) -> None:
        """Initialize the UI of the SettingsWidget instance itself."""

        # Call the super class's init_ui method.
        super()._init_ui()

        # Retrieve the main layout inherited from ISettingsContentWidget.
        main_layout: QVBoxLayout = self.layout()

        # Create the QConfigList.
        self._config_list: QConfigList = QConfigList(
            n=2,
            header_texts=("Bind ...", "To ..."),
            no_duplicates=[1],
            row_widgets=(
                lambda parent_: QPushButtonShortcut(),
                lambda parent_: QPushButtonShortcut(allow_mouse_buttons=True))
            ,
            initial=tuple(
                (
                    QPushButtonShortcut(text=bind),
                    QPushButtonShortcut(text=CONFIG["shortcuts"]["custom"][bind], allow_mouse_buttons=True),
                )
                for bind in CONFIG["shortcuts"]["custom"]
            ),
            validity_function=lambda *widgets: all(widget.text() for widget in widgets),
            widget_edited_callback=self.settings_just_changed,
            only_one_empty_cell=True,
            no_verif=True,
            style=STYLE,
            parent=self
        )

        # Add the QConfigList to the main layout.
        main_layout.addWidget(self._config_list)

        # Create and add the save button to the main layout.
        self._add_save_button()

    # ================== #
    # Overridden methods #
    # ================== #

    def keyPressEvent(self, event: QKeyEvent):
        """
        Overridden keyPressEvent method.
        This method is called when any keyboard shortcut is pressed.

        :param event: The QKeyEvent received.
        :type event: QKeyEvent
        """

        if event.key() == Qt.Key_Escape:
            event.accept()
        else:
            super().keyPressEvent(event)

    def _reset_widgets(self) -> None:
        """Reset the widgets of the ISettingsContentWidget."""
        for row_widgets in self._config_list.widgets:
            try:
                setattr(row_widgets[1], "shortcut", (CONFIG["shortcuts"]["custom"][getattr(row_widgets[0], "text")()]))
                getattr(row_widgets[1], "setText")(CONFIG["shortcuts"]["custom"][getattr(row_widgets[0], "text")()])
            except KeyError:
                continue

    def _save(self) -> None:
        """Callback method when the save button get clicked."""

        utils.update_dict(
            CONFIG,
            "shortcuts",
            "custom",
            value={e[0]: e[1] for e in self._config_list.widgets_content}
        )

        # Calling the super class's save method.
        super()._save()

        # Closing the CustomKeyMappingDialog.
        if hasattr(self.parent(), "done"):
            self.parent().done(0)

    def _is_valid(self) -> bool:
        """
        Return True if the content of the ISettingsContentWidget is valid and can be saved.
        This method should be overridden in child classes.
        """
        return self._config_list.is_valid

    # =================== #
    # Stylesheets methods #
    # =================== #

    def _set_custom_key_mapping_dialog_stylesheet(self) -> None:
        """Set the CustomKeyMappingWidget StyleSheet."""

        # Set the StyleSheet.
        self.setStyleSheet(f"""
            background-color: {STYLE["Custom"]["middleground-color"]};
        """)

    def _set_config_list_stylesheet(self) -> None:
        """Set the config list StyleSheet."""

        # Set the StyleSheet.
        self._config_list.set_stylesheets()

    def set_stylesheets(self) -> None:
        """Call every set_stylesheet method."""

        # Set the CustomKeyMappingWidget StyleSheets.
        super().set_stylesheets()
        self._set_custom_key_mapping_dialog_stylesheet()
        self._set_config_list_stylesheet()

# =-----------------------------------------------------------------------------------------= #
