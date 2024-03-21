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

from yes_no_cancel_dialog import YesNoCancelDialog, YesNoCancelEnum
from PySide6.QtCore       import Qt
from PySide6.QtGui        import QCloseEvent, QColor, QResizeEvent
from PySide6.QtWidgets    import QColorDialog, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSplitter, \
    QVBoxLayout, QWidget
from pathlib              import Path
from utils                import PATH, LB, RB, BS
import typing
import utils

# =-----------------------------------------------------------------------------------------------------------= #


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

    # ================== #
    # Initializer method #
    # ================== #

    def __init__(
            self,
            last_setting_menu: typing.Optional[str],
            style: typing.Dict[str, str],
            parent: typing.Optional[QWidget] = None
    ) -> None:
        """
        Initializer method.
        If parent is provided, set such a parent to the SettingsDialog.

        :param str last_setting_menu: The name of the last setting menu opened. Can be None.
        :param style: The style dictionary.
        :type style: typing.Dict[str, str]
        :param parent: The optional parent of the SettingsDialog to instantiate. By default, None.
        :type parent: QWidget or None
        """

        # Calling the super class's initializer method.
        super().__init__(parent)

        # Initialize the straight-forward attribute.
        self.__settings_changed: bool = False
        self.__style: typing.Dict[str, str] = style
        self.__last_checked_button: typing.Optional[str] = last_setting_menu
        self.__menu_buttons: typing.Dict[str, QPushButton] = {}
        self.__menu_content_labels: typing.List[QLabel] = []
        self.__menu_content_values: typing.Dict[str, typing.Union[QLineEdit, QPushButton]] = {}

        # Initialize the UI.
        self._init_ui()

        # Set the SettingsDialog instance StyleSheet.
        self.__set_settings_stylesheet()

        # If last_setting_menu is not None, call
        # the associated callback method directly.
        if last_setting_menu is not None:
            self.__menu_buttons[last_setting_menu].setChecked(True)
            self.__set_menu_button_stylesheet(self.__menu_buttons[last_setting_menu])
            self.__menu_button_selected(self.__menu_buttons[last_setting_menu], direct_call=True)

    def _init_ui(self) -> None:
        """Initialize the UI of the SettingsDialog instance itself."""

        # Set the title of the Window.
        self.setWindowTitle("Settings")

        # Set the layout of the QDialog.
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create the QSplitter.
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Create the menu and menu content widgets.
        self._init_menu_ui()
        self.__set_menu_stylesheet()
        self.__menu_content: QWidget = QWidget()
        self.__set_menu_content_stylesheet()

        # Add the widgets to the splitter.
        splitter.addWidget(self.__menu)
        splitter.addWidget(self.__menu_content)

        # Set the geometry whole Dialog as well as
        # for the two widgets contained inside the splitter.
        self.setMinimumSize(1000, 562)

    def _init_menu_ui(self) -> None:
        """Initialize the UI of the SettingsDialog's Splitter's menu."""

        # Initialize the menu.
        self.__menu = QWidget()

        # Create a QVBoxLayout for the menu.
        menu_layout = QVBoxLayout()
        self.__menu.setLayout(menu_layout)

        # Create a Style button.
        style_button = QPushButton("Style")
        style_button.setCheckable(True)
        style_button.clicked.connect(lambda: self.__menu_button_selected(style_button))
        self.__menu_buttons["Style"] = style_button
        self.__set_menu_button_stylesheet(style_button)

        # Add the Style button to the menu layout, aligned to the top.
        menu_layout.addWidget(self.__menu_buttons["Style"], alignment=Qt.AlignTop)

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

        # Update the two widgets of the
        # Splitter minimum and maximum sizes.
        self.__menu.setMinimumWidth(int(self.width()/5))
        self.__menu.setMaximumWidth(int(1.5*int(self.width()/5)))
        self.__menu_content.setMinimumWidth(int(3.5*int(self.width()/5)))
        self.__menu_content.setMaximumWidth(4*int(self.width()/5))

    def closeEvent(self, event: QCloseEvent):
        """
        Overridden closeEvent method.
        This method is called when the SettingsDialog instance get closed.

        :param PySide6.QtGui.QCloseEvent event: The QCloseEvent received.
        """

        # If the settings_changed attribute is True,
        # ask for saving the changed or cancel.
        if self.__settings_changed:
            yes_no_cancel_dialog: YesNoCancelDialog = YesNoCancelDialog(
                "Confirmation",
                "Do you confirm your changes ?",
                self
            )
            yes_no_cancel_dialog.exec()

            # Retrieve the result.
            res: YesNoCancelEnum = yes_no_cancel_dialog.result

            # If the result is YesNoCancelEnum.YES, close and return here.
            if res == YesNoCancelEnum.YES:
                return

            # Else if the result is YesNoCancelEnum.NO, set the
            # settings_changed attributes to False, close and return here.
            elif res == YesNoCancelEnum.NO:
                self.__settings_changed = False
                return

            # Otherwise, if the result is YesNoCancelEnum.CANCEL, ignore the event.
            event.ignore()

    # =============== #
    # Private methods #
    # =============== #

    def __display_style_menu(self) -> None:
        """Display the Style menu."""

        # Create the VBoxLayout for the whole menu content widget.
        vertical_layout: QVBoxLayout = QVBoxLayout()

        # Create and add an "App Background Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("App Background Color"))

        # Create and add a "Hotkeys Menu Background" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("Hotkeys Menu Background Color"))

        # Create and add a "Hotkeys Radius Label Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("Hotkeys Radius Label Color"))

        # Create and add a "Hotkeys Radius Slider Progression Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("Hotkeys Radius Slider Progression Color"))

        # Create and add a "Hotkeys Radius Slider Remaining Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("Hotkeys Radius Slider Remaining Color"))

        # Create and add a "New Hotkey Button Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("New Hotkey Button Color"))

        # Create and add a "New Hotkey Button Pressed Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("New Hotkey Button Pressed Color"))

        # Create and add a "Start Button Pressed Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("Start Button Color"))

        # Create and add a "Status Bar Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("Status Bar Color"))

        # Create and add a "Settings Background Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("Settings Background Color"))

        # Create and add a "Settings Menu Background Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("Settings Menu Background Color"))

        # Create and add a "Settings Menu Content Background Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("Settings Menu Content Background Color"))

        # Create and add a "Hotkeys Circle Color" selection to the vertical_layout.
        vertical_layout.addLayout(self.__create_horizontal_color_setting("Hotkeys Circle Color"))

        # Add a Stretch to put the hotkeys horizontal
        # layout just under the previous horizontal layout.
        vertical_layout.addStretch()

        # Add the layout to the  menu content central widget.
        self.__menu_content.setLayout(vertical_layout, )

    # ================================== #
    # High level utility private methods #
    # ================================== #

    def __create_horizontal_color_setting(self, text: str) -> QHBoxLayout:
        """
        Create a horizontal setting containing a QLabel and a QPushButton with a color icon.
        The text of the QLabel shall be provided. The callback method __color_button_clicked will use it as a parameter.
        This method is a wrapper method to __create_horizontal_setting, with some default arguments.

        :param str text: The string the QLabel should contain.
        :returns: The resulting QHBoxLayout.
        :rtype: QHBoxLayout
        """

        # Call and return the __create_horizontal_setting
        # method with the appropriated arguments.
        return SettingsDialog.__create_horizontal_setting(
            {
                "Widget"         : QLabel(text),
                "Align"          : Qt.AlignLeft,
                "AppendToList"   : self.__menu_content_labels,
                "SetAlignment"   : Qt.AlignCenter,
                "SetFixedWidth"  : 310,
                "StyleSheetFunc" : self.__set_menu_content_label_stylesheet,
                "Text"           : text,
            },
            {
                "Widget"         : QPushButton(),
                "Align"          : Qt.AlignRight,
                "AppendToDict"   : (self.__menu_content_values, text),
                "ClickedConnect" : self.__color_button_clicked,
                "StyleSheetFunc" : SettingsDialog.__set_menu_content_color_button_stylesheet,
                "Text"           : text,
            }
        )

    # ================================= #
    # Low level utility private methods #
    # ================================= #

    @staticmethod
    def __create_horizontal_setting(*widgets_data: typing.Dict[str, typing.Union[typing.Any]]) -> QHBoxLayout:
        """
        Create a horizontal setting (i.e.: a multiple QWidgets with a StyleSheet, some extra
        parameters and aligned within a QHBoxLayout), and return the resulting QHBoxLayout.

        :param widgets_style_align: Any dictionary containing multiple elements: The Widget, its alignment and any \
extra parameters.
        :type widgets_style_align: typing.Dict[str, typing.Union[typing.Any]]
        :returns: The resulting QHBoxLayout.
        :rtype: QHBoxLayout
        """

        # Create the QHBoxLayout.
        layout: QHBoxLayout = QHBoxLayout()

        # For each provided widget, edit its StyleSheet, align it
        # and apply the optional parameters provided.
        for widget_data in widgets_data:
            widget: typing.Any = widget_data["Widget"]
            # "Text" is a mandatory key.
            text: str = widget_data.pop("Text")
            if "Align" in widget_data:
                layout.addWidget(widget, alignment=(widget_data["Align"]))
            if "AppendToList" in widget_data:
                widget_data["AppendToList"].append(widget)
            if "AppendToDict" in widget_data:
                dictionary, key = widget_data["AppendToDict"]
                dictionary[key] = widget
            if "ClickedConnect" in widget_data:
                widget.clicked.connect(lambda _event: widget_data["ClickedConnect"](widget, text))
            if "SetAlignment" in widget_data:
                widget.setAlignment(widget_data["SetAlignment"])
            if "SetFixedWidth" in widget_data:
                widget.setFixedWidth(widget_data["SetFixedWidth"])
            if "SetText" in widget_data:
                widget.setText(widget_data["SetText"])
            if "StyleSheet" in widget_data:
                widget.setStyleSheet(widget_data["StyleSheet"])
            if "StyleSheetFunc" in widget_data:
                widget_data["StyleSheetFunc"](widget)
            if "TextChangedConnect" in widget_data:
                widget.textChanged.connect(lambda _event: widget_data["TextChangedConnect"](widget, text))

        # Return the QHBoxLayout.
        return layout

    # =================== #
    # Stylesheets methods #
    # =================== #

    def __set_settings_stylesheet(self) -> None:
        """Set the SettingsDialog StyleSheet."""

        # Set the StyleSheet.
        self.setStyleSheet(f"""
            background-color: {self.__style["Settings Background Color"]};
        """)

    def __set_menu_stylesheet(self) -> None:
        """Set the Menu StyleSheet."""

        # Set the StyleSheet.
        self.__menu.setStyleSheet(f"""
            background-color: {self.__style["Settings Menu Background Color"]};
        """)

    def __set_menu_content_stylesheet(self) -> None:
        """Set the Menu Content StyleSheet."""

        # Set the StyleSheet.
        self.__menu_content.setStyleSheet(f"""
            background-color: {self.__style["Settings Menu Content Background Color"]};
        """)

    def __set_menu_button_stylesheet(self, menu_button: QPushButton) -> None:
        """
        Set the given Menu Button StyleSheet.

        :param PySide6.QtWidgets.QPushButton menu_button: The Menu Button to set the StyleSheet.
        """

        # Set the StyleSheet depending on the Menu Button being checked.
        if menu_button.isChecked():
            menu_button.setStyleSheet(f"""
                QPushButton {LB}
                    background-color: {self.__style["Settings Menu Content Background Color"]};
                    color: rgb(255, 255, 255);
                    font-family: {self.__style["Text Font"]};
                    font-size: 20px;
                    border: 2px solid rgb(255, 255, 255);
                    border-radius: 10px;
                    padding: 5px;
                {RB}
            """)
        else:
            menu_button.setStyleSheet(f"""
                QPushButton {LB}
                    background-color: {self.__style["Settings Menu Background Color"]};
                    color: rgb(255, 255, 255);
                    font-family: {self.__style["Text Font"]};
                    font-size: 20px;
                    border: 2px solid rgb(255, 255, 255);
                    border-radius: 10px;
                    padding: 5px;
                {RB}
            """)

    def __set_menu_content_label_stylesheet(self, label: QLabel) -> None:
        """
        Set the given Menu Content Label StyleSheet.

        :param PySide6.QtWidgets.QLabel label: The Menu Content Label to set the StyleSheet.
        """

        # Set the StyleSheet depending on .
        label.setStyleSheet(f"""
            QLabel {LB}
                background-color: {self.__style[label.text()]};
                color: {utils.opposite_hex_color(self.__style[label.text()])
                    if QColor(self.__style[label.text()]).isValid() else "rgb(255, 255, 255)"};
                font-family: {self.__style["Text Font"]};
                font-size: 16px;
                border: 2px solid rgb(255, 255, 255);
                border-radius: 10px;
                padding: 2px;
            {RB}
        """)

    @staticmethod
    def __set_menu_content_color_button_stylesheet(color_button: QPushButton) -> None:
        """
        Set the given Menu Content color button StyleSheet.

        :param PySide6.QtWidgets.QPushButton color_button: The Menu Content color button to set the StyleSheet.
        """

        # Set the StyleSheet.
        color_button.setStyleSheet(f"""\
            QPushButton {LB}
                border-image: url({str(
                    PATH / Path("img") / Path("color_selection.png")
                ).replace(
                    BS, '/'
                )}) 0 0 0 0 stretch stretch;
                height: 50;
                width: 50;
            {RB}
        """)

    # ================ #
    # Callback methods #
    # ================ #

    def __menu_button_selected(self, button: QPushButton, direct_call: bool = False) -> None:
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

        # Uncheck the previously checked button if required.
        if not direct_call and self.__last_checked_button is not None:
            self.__menu_buttons[self.__last_checked_button].setChecked(
                not self.__menu_buttons[self.__last_checked_button].isChecked()
            )

        # Update the last_checked_button attribute.
        self.__last_checked_button = button.text()

        # Reset the menu_content_labels and menu_content_values lists.
        for e in self.__menu_content_labels:
            e.destroy()
        for k, v in self.__menu_content_values:
            v.destroy()
        self.__menu_content_labels = []
        self.__menu_content_values = {}

        # Display the corresponding menu on the menu
        # content widget and update its StyleSheet.
        if button == self.__menu_buttons["Style"]:
            self.__set_menu_button_stylesheet(button)
            self.__display_style_menu()

    def __color_button_clicked(self, _color_button: QPushButton, style_text: str) -> None:
        """
        Callback method used when any color button get clicked.

        :param PySide6.QtWidgets.QPushButton _color_button: The clicked QPushButton.
        :param str style_text: The Style text associated to the QPushButton.
        """

        # Open a QColorDialog and wait for a color to be selected.
        color: QColor = QColorDialog.getColor(initial=self.__style[style_text])

        # If the QColorDialog has been closed, return here.
        if not color.isValid():
            return

        # Update the style dictionary.
        self.__style[style_text] = color.name()

        # Update the settings changed attribute.
        self.__settings_changed = True

    # ====================== #
    # Virtual Getter methods #
    # ====================== #

    @property
    def menu(self) -> typing.Optional[str]:
        """
        Getter method for menu.

        :returns: The menu text.
        :rtype: str or None
        """
        return self.__last_checked_button

    # ============== #
    # Getter methods #
    # ============== #

    @property
    def settings_changed(self) -> bool:
        """
        Getter method for the SettingsDialog's settings_changed attribute.

        :returns: The SettingsDialog's settings_changed.
        :rtype: bool
        """
        return self.__settings_changed

    @property
    def style(self) -> typing.Dict[str, str]:
        """
        Getter method for the SettingsDialog's style attribute.

        :returns: The SettingsDialog's style.
        :rtype: typing.Dict[str, str]
        """
        return self.__style

# =------------------------------------------------------------------------------------------------------------------= #
