#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    IMainWindow class used by the HotClick software.
    The IMainWindow class is an abstract class inherited
    by the MainWindow class and containing the
    attributes as well as the methods concerning
    these attributes used by the MainWindow class.
    Its only purpose is to make the code more readable.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from main_menu_bar     import MainMenuBar
from circle_window     import CircleWindow
from PySide6.QtCore    import Qt, QPoint, QSize
from PySide6.QtGui     import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QMainWindow, QFileDialog, QLabel, QMenu, QPushButton, QSlider, QStatusBar, \
    QSystemTrayIcon, QHBoxLayout, QVBoxLayout, QWidget
from pathlib           import Path
from utils             import PATH, LB, RB
import typing
import logger
import os
import sys
import json
import utils

# =----------------------------------------------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =---------------= #
# IMainWindow class #
# =---------------= #

class IMainWindow(QMainWindow):
    """
    IMain Window class that contains the attributes
    and methods concerning such attributes used
    by the Main Window class from the main_window.py file.
    """

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self) -> None:
        """Initializer method."""

        # Calling the super class's initializer method.
        super().__init__()

        # Initialize the straight-forward attributes.
        self._circle_windows: typing.List[CircleWindow] = []
        self._config: typing.Dict[
            str, typing.Union[
                int,
                str,
                typing.List[int],
                typing.Dict[str, typing.Dict[str, typing.Union[str, int, ]]],
                typing.Dict[str, str]
            ]
        ] = self.default_config
        self._init_error_message: typing.Optional[str] = None
        self._config_file: typing.Optional[Path] = None
        self._disable_hotkeys: bool = False

        # Initialize the UI.
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI of the CircleWindow instance itself."""

        # Set the title and icon of the Window.
        self.setWindowTitle("HotClick")
        self.setWindowIcon(QIcon(str(PATH / Path("img") / Path("icon.png"))))

        # Set the MainToolbar to the UI and create
        # a dummy attribute reference for convenience.
        self.setMenuBar(MainMenuBar(self))
        self._menu_bar: MainMenuBar = typing.cast(MainMenuBar, self.menuBar())

        # Create the main widget and set it as the central widget.
        main_widget: QWidget = QWidget()
        self.setCentralWidget(main_widget)

        # Create the main layout.
        main_layout: QVBoxLayout = QVBoxLayout(main_widget)

        # Create the hotkeys menu and top layout.
        self._hotkeys_menu: QWidget = QWidget()
        self._set_hotkeys_menu_stylesheet()
        top_layout: QVBoxLayout = QVBoxLayout(self._hotkeys_menu)

        # Create a QLabel indicating what's the purpose of the QSlider and add it to the top layout.
        self._hotkeys_radius_label: QLabel = QLabel("Hotkeys default radius: 60")
        self._hotkeys_radius_label.setAlignment(Qt.AlignCenter)
        self._set_hotkeys_radius_label_stylesheet()
        top_layout.addWidget(self._hotkeys_radius_label)

        # Create the QSlider for selecting the hotkeys to be created and add it to the tp layout.
        self._hotkeys_radius_slider: QSlider = QSlider(Qt.Orientation.Horizontal)
        self._hotkeys_radius_slider.setMinimum(50)
        self._hotkeys_radius_slider.setMaximum(400)
        self._hotkeys_radius_slider.setValue(60)
        self._set_hotkeys_radius_slider_stylesheet()
        top_layout.addWidget(self._hotkeys_radius_slider)

        # Create the QPushButton for adding new hotkeys and add it to the top layout
        self._new_hotkey_button = QPushButton("New Hotkey")
        self._set_new_hotkey_button_stylesheet()
        top_layout.addWidget(self._new_hotkey_button)

        # Add the top frame to the main layout.
        main_layout.addWidget(self._hotkeys_menu)

        # Create the bottom frame and layout.
        bottom_frame: QWidget = QWidget()
        bottom_layout: QHBoxLayout = QHBoxLayout(bottom_frame)

        # Create the start button for the bottom frame
        self._start_button = QPushButton("Start")
        self._set_start_button_stylesheet()
        bottom_layout.addWidget(self._start_button, alignment=Qt.AlignRight)

        # Add the bottom frame to the main layout
        main_layout.addWidget(bottom_frame)

        # Initialize a StatusBar and associate a callback function when its content get edited.
        # Create also a dummy attribute reference for convenience.
        self.setStatusBar(QStatusBar(self))
        self._status_bar: QStatusBar = self.statusBar()
        self._status_bar.messageChanged.connect(self._reset_status_bar_stylesheet)
        self._set_status_bar_stylesheet()
        self._status_bar: QStatusBar = self.statusBar()

        # Initialize the system tray icon, set is invisible yet and connect it to the tray icon activated method.
        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setIcon(QIcon(str(PATH / Path("img") / Path("icon.png"))))
        self._tray_icon.setVisible(False)
        self._tray_icon.setToolTip("HotClick")

        # Create a context menu for exiting the app from the tray.
        self._tray_menu = QMenu()
        self._close_action = QAction("Exit", self)
        self._close_action.triggered.connect(self.close)
        self._tray_menu.addAction(self._close_action)

        # Set the context menu for the tray icon.
        self._tray_icon.setContextMenu(self._tray_menu)

    def _init_load_config(self) -> None:
        """Look for a config file to load."""

        # Retrieve the list of json files at the same location as this file.
        json_files: typing.List[str] = [str(file) for file in os.listdir(PATH) if str(file).endswith(".json")]

        # If no json file is present, use an empty "config.json" file created when the hotkey routine will start.
        if not json_files:
            self._config_file = Path("config.json")
            return

        # If one json only is present, use it as the config file.
        if len(json_files) == 1:
            self._config_file = Path(PATH / Path(json_files[0]))
            # If the config file loading failed, create a new config file.
            if not self._load_save():
                self._config_file = utils.next_config_file_name_available(PATH)
                self._init_error_message = f"Config file corrupted, use a new " + \
                    f"\"{self._config_file.name}\" file"
                return
            return

        # If several json files exist, open a QFileDialog to select one.
        file_path: str
        file_path, _ = QFileDialog.getOpenFileName(None, "Select the config file to open", "", "JSON Files (*.json)")

        # If no json file has been selected, exit the app.
        if not file_path:
            self.close()
            sys.exit(0)

        # Use the selected config file.
        self._config_file = Path(file_path)

        # If the config file loading failed, create a new config file.
        if not self._load_save():
            self._config_file = utils.next_config_file_name_available(PATH)
            self._init_error_message = f"Config file corrupted, use a new " + \
                f"\"{self._config_file.name}\" file"

    # ================== #
    # Overridden methods #
    # ================== #

    def closeEvent(self, event: QCloseEvent):
        """
        Overridden closeEvent method.
        This method is called when the MainWindow instance get closed.

        :param PySide6.QtGui.QCloseEvent event: The QCloseEvent received.
        """

        # Reset the CircleWindows.
        self._reset_circle_windows()

        # Trace.
        logger.info("Exit the app")

    # =================== #
    # Stylesheets methods #
    # =================== #
    
    def _set_hotkeys_menu_stylesheet(self) -> None:
        """Set the Hotkeys Menu StyleSheet."""

        # Set the StyleSheet.
        self._hotkeys_menu.setStyleSheet(f"""
            QWidget {LB}
                background-color: {self.style["Hotkeys Menu Background Color"]};
            {RB}
        """)

    def _set_hotkeys_radius_label_stylesheet(self) -> None:
        """Set the Hotkeys Radius Label StyleSheet."""

        # Set the StyleSheet.
        self._hotkeys_radius_label.setStyleSheet(f"""
             QLabel {LB}
                 font-family: {self.style["Text Font"]};
                 font-size: 14px;
                 color: {self.style["Hotkeys Radius Label Color"]};
                 font-weight: bold;
             {RB}
        """)

    def _set_hotkeys_radius_slider_stylesheet(self) -> None:
        """Set the Hotkeys Radius Slider StyleSheet."""

        # Set the StyleSheet.
        self._hotkeys_radius_slider.setStyleSheet(f"""
             QSlider::groove:horizontal {LB}
                 border: 1px solid #999999;
                 height: 10px;
                 margin: 0px;
                 border-radius: 5px;
             {RB}
             QSlider::handle:horizontal {LB}
                 background: qradialgradient(
                     spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                     stop:0.0 {self.style["Hotkeys Radius Slider Remaining Color"]},
                     stop:1.0 {self.style["Hotkeys Radius Slider Remaining Color"]}
                 );
                 border: 1px solid #5c5c5c;
                 width: 20px;
                 margin: -2px 0;
                 border-radius: 10px;
             {RB}
             QSlider::add-page:horizontal {LB}
                 background: #999999;
                 border: 1px solid #999999;
                 height: 10px;
                 margin: 0px;
             {RB}
             QSlider::sub-page:horizontal {LB}
                 background: #999999;
                 background: qlineargradient(
                     x1: 0, y1: 0, x2: 0, y2: 1,
                     stop: 0 {self.style["Hotkeys Radius Slider Progression Color"]},
                     stop: 1 {self.style["Hotkeys Radius Slider Progression Color"]}
                 );
                 border: 1px solid #999999;
                 height: 10px;
                 margin: 0px;
             {RB}
        """)

    def _set_new_hotkey_button_stylesheet(self) -> None:
        """Set the New Hotkey Button StyleSheet."""

        # Set the StyleSheet.
        self._new_hotkey_button.setStyleSheet(f"""
             QPushButton {LB}
                 background-color: {self.style["New Hotkey Button Color"]};
                 border-style: outset;
                 border-width: 2px;
                 border-radius: 10px;
                 border-color: white;
                 font: bold 14px;
                 min-width: 15em;
                 padding: 6px;
             {RB}
             QPushButton:pressed {LB}
                 background-color: {self.style["New Hotkey Button Pressed Color"]};
                 border-style: inset;
             {RB}
        """)

    def _set_start_button_stylesheet(self) -> None:
        """Set the Start Button StyleSheet."""

        # Set the StyleSheet.
        self._start_button.setStyleSheet(f"""
             QPushButton {LB}
                 background-color: {self.style["Start Button Color"]};
                 border-style: outset;
                 border-width: 2px;
                 border-radius: 10px;
                 border-color: beige;
                 font: bold 14px;
                 min-width: 6em;
                 padding: 6px;
             {RB}
             QPushButton:pressed {LB}
                 background-color: {self.style["Start Button Pressed Color"]};
                 border-style: inset;
             {RB}
        """)

    def _set_status_bar_stylesheet(self) -> None:
        """Set the Status Bar StyleSheet."""

        # Set the StyleSheet.
        self._status_bar.setStyleSheet(f"""
            QStatusBar {LB}
                background-color: {self.style["Status Bar Color"]};
                padding-left:8px;
                font-weight: bold;
            {RB}
        """)

    def _set_stylesheets(self) -> None:
        """Call every set_stylesheet method."""

        # Set the StyleSheets.
        self._set_hotkeys_menu_stylesheet()
        self._set_new_hotkey_button_stylesheet()
        self._set_hotkeys_radius_label_stylesheet()
        self._set_hotkeys_radius_slider_stylesheet()
        self._set_start_button_stylesheet()
        self._set_status_bar_stylesheet()

    # ================================================== #
    # Public and Private Attributes manipulation methods #
    # ================================================== #

    def update_circle_window(self, circle_window: CircleWindow) -> None:
        """
        Update the given CircleWindow within the config dictionary.

        :param CircleWindow circle_window: The CircleWindow to update within the config dictionary.
        """

        # Call the update_config method twice with the corresponding arguments.
        self._update_config(
            "last_position",
            value=[circle_window.position.x(), circle_window.position.y()]
        )
        self._update_config(
            "hotkeys",
            circle_window.hotkey.lower(),
            value={
                "type": "Click",
                'x': circle_window.position.x(),
                'y': circle_window.position.y(),
                'w': circle_window.size.width(),
                'h': circle_window.size.height()
            }
        )

    def edit_circle_window(self, circle_window: CircleWindow, previous_hotkey: str) -> None:
        """
        Edit the given CircleWindow within the config dictionary.

        :param CircleWindow circle_window: The CircleWindow to edit within the config dictionary.
        :param str previous_hotkey: The previous hotkey of the CircleWindow to remove from the config dictionary.
        """

        # Call the update_config method twice with the corresponding arguments.
        self._update_config(
            "hotkeys",
            previous_hotkey.lower(),
            delete=True
        )
        self._update_config(
            "hotkeys",
            circle_window.hotkey.lower(),
            value={
                "type": "Click",
                'x': circle_window.position.x(),
                'y': circle_window.position.y(),
                'w': circle_window.size.width(),
                'h': circle_window.size.height()
            }
        )

    def remove_circle_window(self, circle_window: CircleWindow) -> None:
        """
        Remove the given CircleWindow from the circle windows list and the config dictionary.

        :param CircleWindow circle_window: The CircleWindow to remove from the circle_windows list and the config \
dictionary.
        """

        # Remove such a CircleWindow from the circle windows list.
        self._circle_windows.remove(circle_window)

        # Call the update_config method with the corresponding arguments.
        self._update_config(
            "hotkeys",
            circle_window.hotkey.lower(),
            delete=True
        )

    def _update_config(self, *keys: str, value: typing.Any = None, delete: bool = False) -> None:
        """
        Update the MainWindow's config dictionary.
        If a value is provided, assign such a value to the corresponding keys from the ainWindow's config dictionary.
        If delete is True, delete the corresponding keys from the ainWindow's config dictionary.

        :param str keys: keys to access the desired element from the MainWindow's config dictionary.
        :param Any value: The new value to set to such an element from the MainWindow's config dictionary. By default, \
None.
        :param bool delete: If True, delete the corresponding keys from the ainWindow's config dictionary.
        """

        # If no keys are provided, then config itself need to be assigned.
        if not len(keys):
            if delete:
                logger.error("Impossible to delete the _config dictionary itself.")
                return
            self._config = value
            return

        # Retrieve such an element from the given keys within the MainWindow's config dictionary.
        elem: typing.Dict[str, typing.Any] = self._config
        for key in keys[:-1]:
            elem = elem[key]

        # Delete it if delete is True, otherwise assign the given value.
        if delete:
            del elem[keys[-1]]
        else:
            elem[keys[-1]] = value

        # Save the config.
        self._write_save()

    def _reset_circle_windows(self) -> None:
        """
        Reset the CircleWindows by closing them
        and resetting the circle windows list.
        """

        # Close and remove every element from the circle windows list.
        for circle_window in self._circle_windows:
            circle_window.close()
        self._circle_windows = []

        # Save the config.
        self._write_save()

    def _reset_status_bar_stylesheet(self, message: str) -> None:
        """
        Reset the Stylesheet of the StatusBar if the given message is empty ("").

        :param str message: The new message that has been set to the StatusBar.
        """

        # Reset the stylesheet if the message is being cleared.
        if not message:
            self._set_status_bar_stylesheet()

    def _reset_config(self) -> None:
        """Reset the config dictionary."""

        # Reset the config dictionary with the default config.
        self._update_config(value=self.default_config)

    # ========================= #
    # Config read/write methods #
    # ========================= #

    def _load_save(self) -> bool:
        """
        Read the hotkeys from the config.json file.
        Return the result of the loading.

        :returns: The boolean result of the loading.
        :rtype: bool
        """

        # Try the whole save loading mechanism. In case
        # of any exception raised, abort the loading.
        try:
            # Open the config.json file.
            with open(self._config_file, 'r') as file:
                # Read its json-parsed content.
                json_data: typing.Dict[typing.Any, typing.Any] = json.load(file)

                # Ensure every hotkey contains the required attributes.
                for hotkey in json_data["hotkeys"]:
                    logger.info(
                        f"""Loaded hotkey ["{hotkey}": {json_data["hotkeys"][hotkey]["type"]}, """
                        f"""({json_data["hotkeys"][hotkey]['x']};{json_data["hotkeys"][hotkey]['y']})] """
                        f"""<{json_data["hotkeys"][hotkey]['w']};{json_data["hotkeys"][hotkey]['h']}>"""
                    )

                # Reset the CircleWindows as well as the config.
                self._reset_circle_windows()
                self._reset_config()

                # Restore the CircleWindow instances.
                for hotkey in json_data["hotkeys"]:
                    # Instantiate a new CircleWindow.
                    circle_window: CircleWindow = CircleWindow(
                        self,
                        hotkey,
                        QPoint(json_data["hotkeys"][hotkey]['x'], json_data["hotkeys"][hotkey]['y']),
                        QSize(json_data["hotkeys"][hotkey]['w'], json_data["hotkeys"][hotkey]['h']),
                    )

                    # Add it to the circle windows list.
                    self._circle_windows.append(circle_window)

                    # Show it.
                    circle_window.show()

                # Call the update_config method three time with the corresponding arguments
                # and ensure no key is missing from the loaded config.
                self._update_config("radius", value=json_data["radius"])
                self._update_config("last_position", value=json_data["last_position"])
                self._update_config("last_setting_menu", value=json_data["last_setting_menu"])
                self._update_config("hotkeys", value=json_data["hotkeys"])
                self._update_config("style", value=json_data["style"])

                # Update the hotkey size slider.
                self._hotkeys_radius_slider.setValue(self._config["radius"])

                # Update every config StyleSheets.
                self._set_stylesheets()

            # Trace.
            logger.info(f"Open the config inside \"{self._config_file.parent}\" directory")
            logger.info(f"Open the config called \"{self._config_file.name}\"")

            # Return True
            return True

        except Exception as e:
            logger.error("Exception raised while loading the config file: " + str(e))
            logger.error("Config file loading failed")

            # Return False
            return False

    def _write_save(self) -> None:
        """Save the current hotkeys to the config.json file."""

        # Try the whole save saving mechanism. In case
        # of any exception raised, abort the saving.
        try:
            # Open the config.json file.
            with open(self._config_file, 'w') as file:
                # Write the json-dumped config dictionary.
                file.write(json.dumps(self._config, indent=4))

            # Trace.
            logger.info(f"Save the config inside \"{self._config_file.parent}\" directory")
            logger.info(f"Save the config as \"{self._config_file.name}\"")

        except Exception as e:
            logger.error("Exception raised while writing the config file: " + str(e))
            logger.error("Config file writing failed")

    # ====================== #
    # Virtual Getter methods #
    # ====================== #

    @property
    def default_config(self) -> typing.Dict[
        str, typing.Union[
            int,
            str,
            typing.List[int],
            typing.Dict[str, typing.Dict[str, typing.Union[str, int, ]]],
            typing.Dict[str, str]
        ]
    ]:
        """
        Getter method for the default config.

        :returns: The default config.
        :rtype: typing.Dict[
    str, typing.Union[
        int,
        str,
        typing.List[int],
        typing.Dict[str, typing.Dict[str, typing.Union[str, int, ]]],
        typing.Dict[str, str]
    ]
]
        """
        return {
            "radius": 60,
            "last_position": None,
            "last_setting_menu": None,
            "hotkeys": {},
            "style": {
                "App Background Color": "#FFFFFF",
                "Hotkeys Menu Background Color": "#DCDCDC",
                "Hotkeys Radius Label Color": "#000000",
                "Hotkeys Radius Slider Progression Color": "#9696FF",
                "Hotkeys Radius Slider Remaining Color": "#FFFFFF",
                "New Hotkey Button Color": "#C8C8FF",
                "New Hotkey Button Pressed Color": "#6464C8",
                "Start Button Color": "#C8FFC8",
                "Start Button Pressed Color": "#64C864",
                "Status Bar Color": "#FF96FF",
                "Settings Background Color": "#FFFFFF",
                "Settings Menu Background Color": "#C8C832",
                "Settings Menu Content Background Color": "#FF9B37",
                "Hotkeys Circle Color": "#FF0000",
                "Text Font": "Titillium Web",
            }
        }

    @property
    def style(self) -> typing.Dict[str, str]:
        """
        Getter method for the style dictionary.

        :returns: The style dictionary.
        :rtype: List[str]
        """

        # Return the style dictionary from the config dictionary.
        return self._config["style"]

    @property
    def hotkeys(self) -> typing.List[str]:
        """
        Getter method for the MainWindow's hotkeys.

        :returns: The MainWindow's hotkeys.
        :rtype: List[str]
        """

        # Return the list of hotkeys the MainWindow has.
        return list(self._config["hotkeys"].keys())

# =------------------------------------------------------------------------------------------------------------------= #
