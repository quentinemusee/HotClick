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

from imain_window      import IMainWindow
from circle_window     import CircleWindow
from settings_dialog   import SettingsDialog
from PySide6.QtCore    import QPoint, QSize
from PySide6.QtGui     import QCursor
from PySide6.QtWidgets import QFileDialog, QSystemTrayIcon
from pynput.mouse      import Button, Controller
from pathlib           import Path
from utils             import PATH
import typing
import logger
import time
import keyboard
import utils

# =-----------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Declare the Mouse Controller.
MOUSE: Controller = Controller()

# =--------------------------= #


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

        # Calling the super class's initializer method.
        super().__init__()

        # Connect the different widgets to the corresponding callback methods.
        self._menu_bar.set_menu_callbacks(
            self.__file_new_callback,
            self.__file_open_callback,
            self.__file_save_as_callback,
            self.__settings_callback
        )
        self._hotkeys_radius_slider.valueChanged.connect(self.__slider_value_change)
        self._new_hotkey_button.clicked.connect(self.__new_hotkey)
        self._start_button.clicked.connect(self.__start)
        self._tray_icon.activated.connect(self.__tray_icon_activated)

        # Initialize and associate the logger to this window.
        logger.init_logger(self._status_bar)

        # Look for a config file to load.
        self._init_load_config()

        # Display a successful message on the StatusBar if the init_error_message
        # attribute is None, otherwise display such an error message.
        if self._init_error_message is None:
            logger.info("HotClick successfully launched!")
        else:
            logger.error(self._init_error_message)

    # =============== #
    # Private methods #
    # =============== #

    def __new_hotkey(self) -> None:
        """Create a new instance of CircleWindow."""

        # Instantiate a new CircleWindow.
        circle_window: CircleWindow = CircleWindow(
            self,
            position=QPoint(self._config["last_position"][0], self._config["last_position"][1]) if
                self._config["last_position"] is not None else None,
            size=QSize(self._config["radius"], self._config["radius"])
        )

        # Show it.
        circle_window.show()

        # Add it to the circle windows list.
        self._circle_windows.append(circle_window)

        # Add it to the config dictionary.
        circle_window_position: QPoint = circle_window.position
        circle_window_size: QSize = circle_window.size
        self._config["hotkeys"][circle_window.hotkey.lower()] = {
            "type": "Click",
            'x': circle_window_position.x(),
            'y': circle_window_position.y(),
            'w': circle_window_size.width(),
            'h': circle_window_size.height(),
        }

    def __slider_value_change(self) -> None:
        """Callback function when the hotkey size slider is updated."""

        # Update the size attribute.
        self._config["radius"] = int(self._hotkeys_radius_slider.value())
        self._hotkeys_radius_label.setText(f"""Hotkeys default radius: {self._config["radius"]}""")
        self._hotkeys_radius_label.adjustSize()

        # Save the config.
        self._write_save()

        # Trace.
        logger.info(f"""Hotkeys default radius: {self._config["radius"]}""")

    def __start(self) -> None:
        """Close every instance of CircleWindow and start the hotkey program."""

        # Ensure no CircleWindow has no associated hotkey
        # before to start the main hotkeys routine.
        if "" in self.hotkeys:
            print(self.hotkeys)
            logger.warning("Some hotkeys are not assigned!")
            return

        # Reset the CircleWindows.
        self._reset_circle_windows()

        # Save the config.
        self._write_save()

        # Set the MainWindow instance visible on the tray.
        self._tray_icon.setVisible(True)

        # Hide the MainWindow instance.
        self.hide()

        # Launch the main hotkey routine.
        self._hook: typing.Callable[..., None] = keyboard.on_press(self.__hotkey_routine)

        # Trace.
        logger.info("Program started")

    def __tray_icon_activated(self, reason: int) -> None:
        """
        Callback method when the tray icon get activated through any mouse click.

        :param int reason: An integer representing the type of mouse click.
        """

        # If the application got left-clicked, restore the application.
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Show the application
            self.show()

            # Set the MainWindow instance invisible on the tray
            self._tray_icon.hide()

            # Deactivate the keyboard listener for invoking the hotkey routine method.
            utils.unhook(self._hook)

            # Restore the CircleWindow by reloading the config file.
            self._load_save()

            # Display a successful message on the StatusBar.
            logger.info("HotClick successfully restored!")

        # Otherwise, if the application got right-clicked, show the tray context menu with the exit button.
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            pos = QCursor.pos()
            self._tray_menu.exec_(QPoint(pos.x(), pos.y() - 30))

    def __hotkey_routine(self, event: utils.KeyboardEvent):
        """
        un the hotkey routine for clicking on the previously creates CircleWindow instances.

        :param event: The QMouseEvent received.
        :type event: utils.KeyboardEvent
        """

        # Retrieve the event's hotkey string value.
        event_hotkey: str = event.name.lower()

        # If the event hotkey is "right shift", update the disable_hotkeys and return here.
        if event_hotkey == "right shift":
            self._disable_hotkeys = not self._disable_hotkeys
            return

        # If the disable_hotkeys is True, return.
        if self._disable_hotkeys:
            return

        # If the event hotkey is "esc", simulate a right click and return here.
        if event_hotkey == "esc":
            MOUSE.click(Button.right)
            return

        # Compute the base hotkey.
        base: str = ""
        if keyboard.is_pressed("ctrl"):
            base += "ctrl+"
        if keyboard.is_pressed("maj"):
            base += "maj+"
        if keyboard.is_pressed("alt"):
            base += "alt+"

        # Update the event_hotkey.
        event_hotkey = base + event_hotkey

        # If the event_hotkey match a previously defined CircleWindow's position, click it.
        if event_hotkey in self._config["hotkeys"]:
            # Get the current mouse position before clicking.
            original_position = MOUSE.position

            # Move the mouse to the location to click on.
            MOUSE.position = (
                self._config["hotkeys"][event_hotkey]['x'],
                self._config["hotkeys"][event_hotkey]['y']
            )

            time.sleep(0.02)

            # Simulate a Left Click.
            MOUSE.click(Button.left)

            # Move the mouse back to its original position.
            MOUSE.position = original_position

            # Trace.
            logger.info(f"Hotkey {event_hotkey} pressed")

    # ======================== #
    # MenuBar callback methods #
    # ======================== #

    def __file_new_callback(self) -> None:
        """Callback function when the "File -> New" button get clicked."""

        # Save the config.
        self._write_save()

        # Close and remove every element from the circle windows list.
        self._reset_circle_windows()

        # Reset the config dictionary.
        self._reset_config()

        # Use a config file called configX.json, X being the last number available.
        self._config_file = utils.next_config_file_name_available(PATH)

        # Create such an empty config file via saving the new config.
        self._write_save()

        # Update the StyleSheets.
        self._set_stylesheets()

    def __file_open_callback(self) -> None:
        """Callback function when the "File -> Open" button get clicked."""

        # Save the config.
        self._write_save()

        # Open a QFileDialog to select the config file to open.
        file_path: str
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Config", "", "JSON Files (*.json)")

        # If no json file has been selected, trace and return here.
        if not file_path:
            logger.warning("No config file has been selected")
            return

        # Open and use the selected config file.
        self._config_file = Path(file_path)
        self._load_save()

        # Update the StyleSheets.
        self._set_stylesheets()

    def __file_save_as_callback(self) -> None:
        """Callback function when the "File -> Save As" button get clicked."""

        # Save the config.
        self._write_save()

        # Open a QFileDialog to select the config file to open.
        file_path: str
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "JSON Files (*.json)")

        # If no json file has been selected, trace and return here.
        if not file_path:
            logger.warning("No config file has been selected")
            return

        # Open and save the selected config file.
        self._config_file = Path(file_path)
        self._write_save()

    def __settings_callback(self) -> None:
        """Callback function when the "Settings" button get clicked."""

        # Execute the SettingsDialog menu.
        setting_dialog: SettingsDialog = SettingsDialog(
            self._config["last_setting_menu"],
            self._config.copy()["style"],
            self
        )
        setting_dialog.exec()

        # Update the last_setting_menu in the config.
        self._update_config("last_setting_menu", value=setting_dialog.menu)

        # Update the settings if required.
        if setting_dialog.settings_changed:
            self._update_config("style", value=setting_dialog.style)
            self._set_stylesheets()

# =---------------------------------------------------------------------------------------------------------------= #
