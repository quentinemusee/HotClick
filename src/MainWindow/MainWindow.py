#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    MainWindow class used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from typing             import Any, Callable, Dict
from .IMainWindow       import IMainWindow
from src.SettingsDialog import SettingsDialog
from src.CircleWindow   import CircleWindow
from src.config         import CONFIG
from PySide6.QtCore     import Qt, QMetaObject, QPoint, QSize
from PySide6.QtGui      import QCloseEvent, QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets  import QFileDialog, QSystemTrayIcon
from pynput.mouse       import Button, Controller
from pathlib            import Path
from src.config         import CONFIG_FILE
from src.utils          import PATH
import typing
import src.logger           as logger
import keyboard
import src.config           as config
import src.utils            as utils

# =----------------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Declare the Mouse Controller.
MOUSE: Controller = Controller()

# Declare a hotkey routine flag.
HOTKEY_ROUTINE_IS_RUNNING: bool = False

# =---------------------------------= #


# =--------------= #
# MainWindow class #
# =--------------= #

class MainWindow(IMainWindow):
    """
    Main Window class that represent the main
    interface to create CircleWindow instances
    and run the main program in background.
    """

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self) -> None:
        """Initializer method."""

        # Call the super class's initializer method.
        super().__init__()

        # Connect the different widgets to the corresponding callback methods.
        self._menu_bar.set_menu_callbacks(
            self._file_new_callback,
            self._file_open_callback,
            self._file_save_as_callback,
            self._settings_callback
        )
        self._hotkeys_radius_slider.valueChanged.connect(self._slider_value_change)
        self._new_hotkey_button.clicked.connect(self._new_hotkey)
        self._start_button.clicked.connect(self._start)
        self._tray_icon.activated.connect(self._tray_icon_activated)

        # Initialize and associate the logger to this window.
        logger.init_logger(self._status_bar)

        # Look for a config file to load.
        self._init_load_config()

        # Load the theme file.
        config.load_style()

        # Initialize the UI style.
        self.set_stylesheets()

        # Set the software builtin shortcuts.
        self.update_builtin_shortcuts()

        # Initialize the main hotkey routine.
        self._hook: typing.Callable[[], None] = keyboard.on_press(self._hotkey_routine)

        # Display a successful message on the StatusBar if the init_error_message
        # attribute is None, otherwise display such an error message.
        if self._init_error_message is None:
            logger.info("HotClick successfully launched!")
        else:
            logger.error(self._init_error_message)

    # ================== #
    # Overridden methods #
    # ================== #

    def closeEvent(self, event: QCloseEvent):
        """
        Overridden closeEvent method.
        This method is called when the MainWindow instance get closed.

        :param PySide6.QtGui.QCloseEvent event: The QCloseEvent received.
        """

        # Unhook the hotkey_routine keyboard callback method.
        utils.unhook(self._hotkey_routine)

        # Call the super class's closeEvent method.
        super().closeEvent(event)

    # ============== #
    # Public methods #
    # ============== #

    def update_builtin_shortcuts(self) -> None:
        """Update the builtin shortcuts used by the software."""

        # Update the builtin shortcuts reading their
        # current value from the CONFIG dictionary.
        for action in CONFIG["shortcuts"]["builtin"]:
            if action in self._builtin_shortcuts:
                self._builtin_shortcuts[action].setEnabled(False)
            # Actually, it's not ~that~ dynamic, the
            # following part remains hardcoded.
            tmp: Dict[str, Callable[..., Any]] = {
                "New": self._file_new_callback,
                "Open": self._file_open_callback,
                "Save As...": self._file_save_as_callback,
                "Settings": self._settings_callback,
                "New Hotkey": self._new_hotkey,
                "Start": self._start,
            }
            if action in tmp:
                self._builtin_shortcuts[action]: QShortcut = QShortcut(
                    QKeySequence(CONFIG["shortcuts"]["builtin"][action]),
                    self
                )
                self._builtin_shortcuts[action].activated.connect(tmp[action])

    # =============== #
    # Private methods #
    # =============== #

    def _new_hotkey(self) -> None:
        """Create a new instance of CircleWindow."""

        # Instantiate a new CircleWindow.
        circle_window: CircleWindow = CircleWindow(
            self,
            position=QPoint(CONFIG["last_position"][0], CONFIG["last_position"][1]) if
            CONFIG["last_position"] is not None else None,
            size=QSize(CONFIG["radius"], CONFIG["radius"])
        )

        # Show it.
        circle_window.show()

        # Add it to the circle windows list.
        self._circle_windows.append(circle_window)

        # Add it to the config dictionary.
        circle_window_position: QPoint = circle_window.position
        circle_window_size: QSize = circle_window.size
        CONFIG["hotkeys"][circle_window.hotkey.lower()] = {
            "type": "Click",
            'x': circle_window_position.x(),
            'y': circle_window_position.y(),
            'w': circle_window_size.width(),
            'h': circle_window_size.height(),
        }

    def _slider_value_change(self) -> None:
        """Callback function when the hotkey size slider is updated."""

        # Update the size attribute.
        CONFIG["radius"] = int(self._hotkeys_radius_slider.value())
        self._hotkeys_radius_label.setText(f"""Hotkeys default radius: {CONFIG["radius"]}""")
        self._hotkeys_radius_label.adjustSize()

        # Save the config.
        config.save_config()

        # Trace.
        logger.info(f"""Hotkeys default radius: {CONFIG["radius"]}""")

    def _start(self) -> None:
        """Close every instance of CircleWindow and start the hotkey program."""

        # Make the HOTKEY_ROUTINE_IS_RUNNING global variable writable.
        global HOTKEY_ROUTINE_IS_RUNNING

        # Ensure no CircleWindow has no associated hotkey
        # before to start the main hotkeys routine.
        if "" in self.hotkeys:
            logger.warning("Some hotkeys are not assigned!")
            return

        # Reset the CircleWindows.
        self._reset_circle_windows()

        # Save the config.
        config.save_config()

        # Set the MainWindow instance visible on the tray.
        self._tray_icon.setVisible(True)

        # Set HOTKEY_ROUTINE_IS_RUNNING to True.
        HOTKEY_ROUTINE_IS_RUNNING = True

        # Hide the MainWindow instance.
        self.hide()

        # Trace.
        logger.info("Program started")

    def _tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason.Trigger) -> None:
        """
        Callback method when the tray icon get activated through any mouse click.

        :param reason: The type of mouse click used on the tray icon.$
        :type reason: QSystemTrayIcon.ActivationReason.Trigger
        """

        # Make the HOTKEY_ROUTINE_IS_RUNNING global variable writable.
        global HOTKEY_ROUTINE_IS_RUNNING

        # If the application got left-clicked, restore the application.
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Show the application&
            QMetaObject.invokeMethod(self, typing.cast(bytes, "show"), Qt.ConnectionType.QueuedConnection)

            # Set the MainWindow instance invisible on the tray
            # $self._tray_icon.hide()
            QMetaObject.invokeMethod(self._tray_icon, typing.cast(bytes, "hide"), Qt.ConnectionType.QueuedConnection)

            # Set HOTKEY_ROUTINE_IS_RUNNING to False.$
            HOTKEY_ROUTINE_IS_RUNNING = False

            # Restore the CircleWindow by reloading the config file.
            QMetaObject.invokeMethod(self, typing.cast(bytes, "_load_config"), Qt.ConnectionType.QueuedConnection)

            # Display a successful message on the StatusBar.
            logger.info("HotClick successfully restored!")

        # Otherwise, if the application got right-clicked, show the tray context menu with the exit button.
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            pos = QCursor.pos()
            self._tray_menu.exec(QPoint(pos.x(), pos.y() - 30))

    def _hotkey_routine(self, event: utils.KeyboardEvent) -> None:
        """
        Run the hotkey routine for clicking on the previously creates CircleWindow instances.

        :param event: The QMouseEvent received.
        :type event: utils.KeyboardEvent
        """

        # Retrieve the event's hotkey string value.
        original_event_hotkey: str = event.name.lower()

        # Retrieve the event's hotkey string.
        event_hotkey: str = utils.handle_hotkey(event)

        # If the event hotkey is the "Restore Application" shortcut,
        # even if the HOTKEY_ROUTINE_IS_RUNNING global variable is
        # still False, restore the application from being minimized
        # and return here.
        if event_hotkey.upper() == CONFIG["shortcuts"]["builtin"]["Restore Application"]:
            if self.isMinimized():
                self.showNormal()
                return

        # If the HOTKEY_ROUTINE_IS_RUNNING
        # global variable is False, return here.
        if not HOTKEY_ROUTINE_IS_RUNNING:
            return

        # If the event hotkey is the "Disable Hotkeys" shortcut,
        # update the disable_hotkeys attribute and return.
        if event_hotkey.upper() == CONFIG["shortcuts"]["builtin"]["Disable Hotkeys"]:
            self._disable_hotkeys = not self._disable_hotkeys
            return

        # If the disable_hotkeys is True, return.
        if self._disable_hotkeys:
            return

        # If the event hotkey is the "Restore Application" shortcut,
        # restore the MainWindow and return here.
        if event_hotkey.upper() == CONFIG["shortcuts"]["builtin"]["Restore Application"]:
            self._tray_icon_activated(QSystemTrayIcon.ActivationReason.Trigger)
            return

        # If the event_hotkey match a previously defined CircleWindow's position, click it.
        if event_hotkey in CONFIG["hotkeys"]:
            # Get the current mouse position before clicking.
            original_position = MOUSE.position

            while keyboard.is_pressed(original_event_hotkey):
                # Move the mouse to the location to click on.
                MOUSE.position = (
                    CONFIG["hotkeys"][event_hotkey]['x']-int(CONFIG["hotkeys"][event_hotkey]['w']/2),
                    CONFIG["hotkeys"][event_hotkey]['y']-int(CONFIG["hotkeys"][event_hotkey]['h']/2)
                )

            # Simulate a Left Click.
            MOUSE.click(Button.left)

            # Move the mouse back to its original position.
            MOUSE.position = original_position

            # Trace.
            logger.info(f"Hotkey {event_hotkey} pressed")
        # Otherwise, if the event_hotkey match a custom shortcut, execute it.
        elif event_hotkey in CONFIG["shortcuts"]["custom"]:
            bind_to: str = CONFIG["shortcuts"]["custom"][event_hotkey]
            if bind_to == "LeftButton":
                MOUSE.click(Button.left)
            elif bind_to == "RightButton":
                MOUSE.click(Button.right)

    # ======================== #
    # MenuBar callback methods #
    # ======================== #

    def _file_new_callback(self) -> None:
        """Callback function when the "File -> New" button get clicked."""

        # Save the config.
        config.save_config()

        # Close and remove every element from the circle windows list.
        self._reset_circle_windows()

        # Reset, save and load the config dictionary.
        self._reset_config()

        # Use a config file called configX.json, X being the last number available.
        CONFIG_FILE[0] = utils.next_config_file_name_available(PATH / Path("configs"))

        # Create such an empty config file via saving the new config.
        config.save_config()

        # Trace.
        logger.info(f"New config file \"{CONFIG_FILE[0].name}\" created!")

    def _file_open_callback(self) -> None:
        """Callback function when the "File -> Open" button get clicked."""

        # Save the config.
        config.save_config()

        # Open a QFileDialog to select the config file to open.
        file_path: str
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Config", "", "JSON Files (*.json)")

        # If no json file has been selected, trace and return here.
        if not file_path:
            logger.warning("No config file has been selected")
            return

        # Open and use the selected config file.
        CONFIG_FILE[0] = Path(file_path)
        self._load_config()

        # Trace.
        logger.info(f"Config file \"{CONFIG_FILE[0].name}\" loaded!")

    def _file_save_as_callback(self) -> None:
        """Callback function when the "File -> Save As" button get clicked."""

        # Save the config.
        config.save_config()

        # Create a temporary variable for holding the current config_file value.
        old_config_file: Path = CONFIG_FILE[0]

        # Open a QFileDialog to select the config file to open.
        file_path: str
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "JSON Files (*.json)")

        # If no json file has been selected, trace and return here.
        if not file_path:
            logger.warning("No config file has been selected")
            return

        # Open and save the selected config file.
        CONFIG_FILE[0] = Path(file_path)
        config.save_config()

        # Trace.
        logger.info(f"Config file \"{old_config_file.name}\" saved as \"{CONFIG_FILE[0].name}\"!")

    def _settings_callback(self) -> None:
        """Callback function when the "Settings" button get clicked."""

        # Execute the SettingsDialog menu.
        self._settings_dialog = SettingsDialog(self)
        self._settings_dialog.open()

    # =================== #
    # Stylesheets methods #
    # =================== #

    def set_stylesheets(self) -> None:
        """Call every set_stylesheet method."""

        # Set the MainWindow StyleSheets.
        self._set_main_window_stylesheet()
        self._set_hotkeys_menu_stylesheet()
        self._set_new_hotkey_button_stylesheet()
        self._set_hotkeys_radius_label_stylesheet()
        self._set_hotkeys_radius_slider_stylesheet()
        self._set_start_button_stylesheet()
        self._set_status_bar_stylesheet()

        # Set the SettingsDialog Stylesheets.
        if self._settings_dialog is not None:
            self._settings_dialog.set_stylesheets()

        # Set the CircleWindow Stylesheets calling
        # its repaint method to invoke the overridden
        # paintEvent method from the CircleWindow.
        for circle_window in self._circle_windows:
            circle_window.repaint()

# =---------------------------------------------------------------------------------------------------------------= #
