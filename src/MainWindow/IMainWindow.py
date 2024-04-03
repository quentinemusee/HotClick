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

from typing             import Dict, List, Optional
from .MainMenuBar       import MainMenuBar
from src.SettingsDialog import SettingsDialog
from src.CircleWindow   import CircleWindow
from PySide6.QtCore     import Qt, QPoint, QSize, Slot
from PySide6.QtGui      import QAction, QCloseEvent, QIcon, QShortcut
from PySide6.QtWidgets  import QMainWindow, QFileDialog, QLabel, QMenu, QPushButton, QSlider, QStatusBar, \
    QSystemTrayIcon, QHBoxLayout, QVBoxLayout, QWidget
from pathlib            import Path
from src.utils          import PATH
from src.config         import CONFIG, CONFIG_FILE, STYLE
import typing
import src.logger           as logger
import os
import sys
import src.config          as config
import src.utils           as utils

# =-----------------------------------------------------------------------------------------------------= #


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
    by the Main Window class from the MainWindow.py file.
    """

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self) -> None:
        """Initializer method."""

        # Call the super class's init$ializer method.
        super().__init__()

        # Initialize the straight-forward attributes.
        self._circle_windows: List[CircleWindow] = []
        self._builtin_shortcuts: Dict[str, QShortcut] = {}
        self._custom_shortcuts: Dict[str, QShortcut] = {}
        self._init_error_message: Optional[str] = None
        self._last_hotkey: Optional[str] = None
        self._disable_hotkeys: bool = False

        # Initialize the UI.
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI of the CircleWindow instance itself."""

        # Set the Window Flag.
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

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

        # Initialize the SettingsDialog to None
        self._settings_dialog: Optional[SettingsDialog] = None

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

        # Create the config directory if it doesn't exist.
        config_path: Path = PATH / Path("configs")
        if not config_path.exists():
            config_path.mkdir()

        # Retrieve the list of json files at the same location as this file.
        json_files: List[str] = [
            str(file) for file in os.listdir(config_path) if str(file).endswith(".json")
        ]

        # If no json file is present, use an empty "config.json" file created when the hotkey routine will start.
        if not json_files:
            CONFIG_FILE[0] = config_path / Path("config.json")
            config.save_config()
            return

        # If one json only is present, use it as the config file.
        if len(json_files) == 1:
            CONFIG_FILE[0] = Path(config_path / Path(json_files[0]))
            # Try to load the config file and if
            # it failed, create a new config file.
            self._load_config()
            return

        # If several json files exist, open a QFileDialog to select one.
        file_path: str
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select the config file to open",
            dir=str(config_path),
            filter="JSON Files (*.json)",
        )

        # If no json file has been selected, exit the app.
        if not file_path:
            self.close()
            sys.exit(0)

        # Use the selected config file.
        CONFIG_FILE[0] = Path(file_path)

        # Try to load the config file and if
        # it failed, create a new config file.
        self._load_config()

    # ================== #
    # Overridden methods #
    # ================== #

    def closeEvent(self, event: QCloseEvent):
        """
        Overridden closeEvent method.
        This method is called when the IMainWindow instance get closed.

        :param PySide6.QtGui.QCloseEvent event: The QCloseEvent received.
        """

        # Call the super class's closeEvent method.
        super().closeEvent(event)

        # Reset the CircleWindows.
        self._reset_circle_windows()

        # Clear the IMainWindow's layout.
        utils.clear_layout(self.layout())

        # Trace.
        logger.info("Exit the app")

    # =================== #
    # Stylesheets methods #
    # =================== #

    def _set_main_window_stylesheet(self) -> None:
        """Set the IMainWindow StyleSheet."""

        # Set the StyleSheet.
        self.setStyleSheet(f"""
            background-color: {STYLE["background-color"]};
        """)
    
    def _set_hotkeys_menu_stylesheet(self) -> None:
        """Set the Hotkeys Menu StyleSheet."""

        # Set the StyleSheet.
        self._hotkeys_menu.setStyleSheet(f"""
            QWidget {{
                background-color: {STYLE["Custom"]["middleground-color"]};
            }}
        """)

    def _set_hotkeys_radius_label_stylesheet(self) -> None:
        """Set the Hotkeys Radius Label StyleSheet."""

        # Set the StyleSheet.
        self._hotkeys_radius_label.setStyleSheet(f"""
             QLabel {{
                 font-family: {STYLE["font-family"]};
                 font-size: 14px;
                 color: {STYLE["color"]};
                 font-weight: bold;
             }}
        """)

    def _set_hotkeys_radius_slider_stylesheet(self) -> None:
        """Set the Hotkeys Radius Slider StyleSheet."""

        # Set the StyleSheet.
        self._hotkeys_radius_slider.setStyleSheet(f"""
             QSlider::groove:horizontal {{
                 border: 1px solid #999999;
                 height: 10px;
                 margin: 0px;
                 border-radius: 5px;
             }}
             QSlider::handle:horizontal {{
                 background: qradialgradient(
                     spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                     stop:0.0 #9696FF,
                     stop:1.0 #9696FF
                 );
                 border: 1px solid #5c5c5c;
                 width: 20px;
                 margin: -2px 0;
                 border-radius: 10px;
             }}
             QSlider::add-page:horizontal {{
                 background: #999999;
                 border: 1px solid #999999;
                 height: 10px;
                 margin: 0px;
             }}
             QSlider::sub-page:horizontal {{
                 background: #999999;
                 background: qlineargradient(
                     x1: 0, y1: 0, x2: 0, y2: 1,
                     stop: 0 #FFFFFF,
                     stop: 1 #FFFFFF
                 );
                 border: 1px solid #999999;
                 height: 10px;
                 margin: 0px;
             }}
        """)

    def _set_new_hotkey_button_stylesheet(self) -> None:
        """Set the New Hotkey Button StyleSheet."""

        # Set the StyleSheet.
        self._new_hotkey_button.setStyleSheet(f"""
             QPushButton {{
                 background-color: {STYLE["QPushButton"]["background-color"]};
                 border-style: outset;
                 border-width: 2px;
                 border-radius: 10px;
                 border-color: white;
                 font: bold 14px;
                 min-width: 15em;
                 padding: 6px;
             }}
             QPushButton:pressed {{
                 background-color: {STYLE["QPushButton:pressed"]["background-color"]};
                 border-style: inset;
             }}
        """)

    def _set_start_button_stylesheet(self) -> None:
        """Set the Start Button StyleSheet."""

        # Set the StyleSheet.
        self._start_button.setStyleSheet(f"""
             QPushButton {{
                 background-color: {STYLE["QPushButton"]["background-color"]};
                 border-style: outset;
                 border-width: 2px;
                 border-radius: 10px;
                 border-color: beige;
                 font: bold 14px;
                 min-width: 6em;
                 padding: 6px;
             }}
             QPushButton:pressed {{
                 background-color: {STYLE["QPushButton:pressed"]["background-color"]};
                 border-style: inset;
             }}
        """)

    def _set_status_bar_stylesheet(self) -> None:
        """Set the Status Bar StyleSheet."""

        # Set the StyleSheet.
        self._status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {STYLE["QStatusBar"]["background-color"]};
                padding-left:8px;
                font-weight: bold;
            }}
        """)

    # =============================== #
    # Attributes manipulation methods #
    # =============================== #

    def clear_last_hotkey(self) -> None:
        """Set the last_hotkey attribute to None."""
        self._last_hotkey = None

    def _reset_circle_windows(self) -> None:
        """
        Reset the CircleWindows by closing them
        and resetting the circle windows list.
        """

        # Close, destroy and remove every element from the circle windows list.
        for circle_window in self._circle_windows:
            circle_window.close()
            circle_window.deleteLater()
        self._circle_windows = []

    def _reset_status_bar_stylesheet(self, message: str) -> None:
        """
        Reset the Stylesheet of the StatusBar if the given message is empty ("").

        :param str message: The new message that has been set to the StatusBar.
        """

        # Reset the stylesheet if the message is being cleared.
        if not message:
            self._set_status_bar_stylesheet()

    # ========================= #
    # Config read/write methods #
    # ========================= #

    # Turn the load_config method into a slot to
    # make it callable using QMetaObject.invokeMethod
    # to ensure this method is called in the main thread.
    @Slot()
    def _load_config(self, no_load: bool = False) -> bool:
        """
        Restore the IMainWindow's attributes and widgets
        depending on the content of the json parsed config_file attribute.
        Return the result of the loading.
        If no_load is True, don't load but exist the current CONFIG dictionary.

        :param no_load: If True, don't load but exist the current CONFIG dictionary. By default, False.
        :type no_load: bool
        :returns: The boolean result of the loading.$$
        :rtype: bool
        """

        # Reset the current config.
        config.reset_config()

        # Load the config_file attribute content.
        # If the loading is a success, restore the
        # CircleWindows and shortcuts.
        if config.load_config() if not no_load else True:
            # Reset the CircleWindows as well as the config.
            self._reset_circle_windows()

            # Restore the CircleWindow instances.
            for hotkey in CONFIG["hotkeys"]:
                # Instantiate a new CircleWindow.
                circle_window: CircleWindow = CircleWindow(
                    self,
                    hotkey,
                    QPoint(CONFIG["hotkeys"][hotkey]['x'], CONFIG["hotkeys"][hotkey]['y']),
                    QSize(CONFIG["hotkeys"][hotkey]['w'], CONFIG["hotkeys"][hotkey]['h']),
                )

                # Add it to the circle windows list.
                self._circle_windows.append(circle_window)

                # Show it.
                circle_window.show()

            # Update the hotkey size slider.
            self._hotkeys_radius_slider.setValue(CONFIG["radius"])

            # Return here.
            return True

        # The parsing is a failure: create a new
        # config file and update the init error message.
        CONFIG_FILE[0] = utils.next_config_file_name_available(PATH / Path("configs"))
        config.save_config()
        self._init_error_message = f"Config file corrupted, use a new \"{CONFIG_FILE[0].name}\" file"

    def _reset_config(self) -> None:
        """
        Reset the CONFIG dictionary.
        Save the new CONFIG dictionary to the config_file attribute.
        Call the _load_config method to update the IMainWindow
        """

        # Reset the CONFIG dictionary.
        config.reset_config()

        # Save the reset config.
        config.save_config()

        # Load the reset config.
        self._load_config(no_load=True)

    # ===================== #
    # Pseudo Getter methods #
    # ===================== #

    @property
    def hotkeys(self) -> List[str]:
        """
        Getter method for the hotkeys.

        :returns: The hotkeys.
        :rtype: List[str]
        """

        # Return the list of hotkeys from the CONFIG dictionary.
        return list(CONFIG["hotkeys"].keys())

    # ============== #
    # Getter methods #
    # ============== #

    @property
    def circle_windows(self) -> List[CircleWindow]:
        """
        Getter method for the circle_windows attribute.

        :returns: The circle_windows attribute.
        :rtype: List[CircleWindow]
        """
        return self._circle_windows

    @property
    def last_hotkey(self) -> Optional[str]:
        """
        Getter method for the last_hotkey attribute.

        :returns: The last_hotkey attribute.
        :rtype: Optional[str]
        """
        return self._last_hotkey

# =------------------------------------------------------------------------------------------------------------------= #
