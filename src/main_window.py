#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    MainWindow class used by the HotClick software.

     ___________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGEDOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from circle_window            import CircleWindow
from PySide6.QtCore           import Qt, QPoint
from PySide6.QtGui            import QAction, QIcon, QCloseEvent
from PySide6.QtWidgets        import QMainWindow, QFileDialog, QLabel, QMenu, QPushButton, QSlider, QSystemTrayIcon
from keyboard._keyboard_event import KeyboardEvent
from pynput.mouse             import Button, Controller
from pathlib                  import Path
import typing
import os
import sys
import time
import keyboard
import json
import logger
import utils

# =-------------------------------------------------------------------------------------------------------------= #


# =-------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTON #
# =-------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Declare the Mouse Controller.
MOUSE: Controller = Controller()

# Retrieve and declare the binary directory path.
PATH: Path = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else Path(__file__).parent.parent

# =---------------------------------------------------------------------------------------------------------= #


# =--------------= #
# MainWindow class #
# =--------------= #

class MainWindow(QMainWindow):
    """
    Main Window class that represent the main
    interface to create CircleWindow instances
    and run the main program in background.
    """

    # ================== #
    # Initializer method #
    # ================== #

    def __init__(self) -> None:
        """Initializer method."""

        # Calling the super class's initializer method.
        super().__init__()

        # Initialize the straight-forward attributes.
        self.__circle_windows: typing.List[CircleWindow] = []
        self.__hotkeys: typing.Dict[
            str, typing.Union[int, typing.Dict[str, typing.Dict[str, typing.Union[str, int]]]]
        ] = {"radius": 60, "hotkeys": {}}
        self.__input_hotkeys: typing.List[str] = []
        self.__config_file: typing.Optional[Path] = None
        self.__disable_hotkeys: bool = False

        # Call the UI initialization method to initialize the UI itself.
        self.__init_UI()

    # ================= #
    # Overriden methods #
    # ================= #

    def closeEvent(self, event: QCloseEvent):
        """
        Overriden closeEvent method.
        This method is called when the MainWindow instance get closed.

        :param event: The QCloseEvent received.
        :type event: PyQt5.QtGui.QCloseEvent
        """

        # Close every window.
        for circle_window in self.__circle_windows:
            circle_window.close()

        # Call the super class's closeEvent method with the received QCloseEvent.
        super().closeEvent(event)

        # Trace.
        logger.info("Exit the app")

        sys.exit(0)

    # =============== #
    # Private methods #
    # =============== #

    def __init_UI(self) -> None:
        """Initialize the UI of the CircleWindow instance itself."""

        # Set the Geometry of the Window.
        self.setGeometry(300, 300, 300, 200)

        # Set the title of the Window.
        self.setWindowTitle("HotClick")

        # Initialize the "New Hotkey" Push Button, connect it to the
        # new hotkey method and place it on the Main Window instance.
        self.__new_hotkey_button = QPushButton("New Hotkey", self)
        self.__new_hotkey_button.clicked.connect(self.__new_hotkey)
        self.__new_hotkey_button.move(100, 80)
        
        # Initialize the "Start" Push Button, connect it to the
        # start method and place it on the Main Window instance.
        self.__start_button = QPushButton("Start", self)
        self.__start_button.clicked.connect(self.__start)
        self.__start_button.move(100, 120)

        # Initialize system tray icon, set is invisible yet and connect it to the tray icon activated method.
        self.__tray_icon = QSystemTrayIcon(self)
        self.__tray_icon.setIcon(QIcon("icon.png"))
        self.__tray_icon.setVisible(False)
        self.__tray_icon.setToolTip("HotClick")
        self.__tray_icon.activated.connect(self.__tray_icon_activated)

        # Create a context menu for exiting the app from the tray.
        self.__tray_menu = QMenu()
        self.__close_action = QAction("Exit", self)
        self.__close_action.triggered.connect(self.close)
        self.__tray_menu.addAction(self.__close_action)

        # Initialize the slider for the default hotkeys size.
        self.__hotkey_size_slider = QSlider(Qt.Horizontal, self)
        self.__hotkey_size_slider.setMinimum(50)
        self.__hotkey_size_slider.setMaximum(400)
        self.__hotkey_size_slider.setValue(60)
        self.__hotkey_size_slider.setTickPosition(QSlider.TicksBelow)
        self.__hotkey_size_slider.setTickInterval(5)
        self.__hotkey_size_slider.move(100, 40)
        self.__hotkey_size_slider.show()
        self.__hotkey_size_slider.valueChanged.connect(self.__slider_value_change)

        # Instanciate a label to assign to the slider.
        self.__hotkey_size_label = QLabel(self)
        self.__hotkey_size_label.setAlignment(Qt.AlignCenter)
        self.__hotkey_size_label.move(100, 20)
        self.__hotkey_size_label.setText("Hotkeys radius: 60")
        self.__hotkey_size_label.adjustSize()

        # Set the context menu for the tray icon.
        self.__tray_icon.setContextMenu(self.__tray_menu)

        # Retrieve the list of json files at the same location as this file.
        jsons: typing.List[str] = [file for file in os.listdir(PATH) if file.endswith(".json")]

        # If no json file is present, use an empty "config.json" file created when the hotkey routine will start.
        if not jsons:
            self.__config_file = Path("config.json")
            return

        # If one json only is present, use it as the config file.
        if len(jsons) == 1:
            self.__config_file = Path(PATH / Path(jsons[0]))
            self.__load_save()
            return

        # If several jsons exist, open a QFileDialog to select one.
        file_path: str
        file_path, _ = QFileDialog.getOpenFileName(None, "Select the config file", "", "JSON Files (*.json)")

        # If no json file has been selected, exit the app.
        if not file_path:
            self.close()

        # Use the selected config file.
        self.__config_file = Path(file_path)
        self.__load_save()

    def __new_hotkey(self) -> None:
        """Create a new instance of CircleWindow."""

        # Instanciate a new CircleWindow.
        circle_window: CircleWindow = CircleWindow((self.__hotkeys["radius"], self.__hotkeys["radius"]))

        # Show it.
        circle_window.show()

        # Add it to the circle windows list.
        self.__circle_windows.append(circle_window)

        # Trace.
        logger.info("New hotkey created")

    def __slider_value_change(self) -> None:
        """Callback function when the hotkey size slider is updated."""

        # Update the size attribute.
        self.__hotkeys["radius"] = int(self.__hotkey_size_slider.value())
        self.__hotkey_size_label.setText(f"""Hotkeys radius: {self.__hotkeys["radius"]}""")
        self.__hotkey_size_label.adjustSize()

    def __start(self) -> None:
        """Close every instance of CircleWindow and start the hotkey program."""

        # Retrieve the hotkey and centered coordonate of every CircleWindow instances and close them.
        for circle_window in self.__circle_windows:
            # Retrieve the hotkey and centered coordonate of the CircleWindow instance;
            hotkey: str
            position: QPoint
            hotkey, position = circle_window.get_click_position_and_hotkey()

            # If the CircleWindow instance has been destroyed, continue.
            if circle_window.is_destroyed:
                continue

            # If a duplicate hotkey has been found, reset the hotkeys dictonary and return.
            if hotkey.lower() in self.__hotkeys["hotkeys"]:
                logger.warning("Duplicate Hotkey:", hotkey.lower())
                self.__hotkeys = {"radius": self.__hotkeys["radius"], "hotkeys": {}}
                return

            # Update the hotkeys dictonary.
            rect: QRect = self.rect()
            self.__hotkeys["hotkeys"][hotkey.lower()] = {
                "type": "Click",
                "radius": circle_window.radius,
                'x': position.x(),
                'y': position.y()
            }

        # If this point is reached, no duplicate hotkey has been found:
        # close and remove every element from the circle windows list.
        for circle_window in self.__circle_windows:
            circle_window.close()
        self.__circle_windows = []

        # Save the configuration.
        self.__write_save()

        # Set the MainWindow instance visible on the tray.
        self.__tray_icon.setVisible(True)

        # Hide the MainWindow instance.
        self.hide() # Hide the main window

        # Launch the main hotkey routine.
        self.__hook: typing.Callable[..., None] = keyboard.on_press(self.__hotkey_routine)

        # Trace.
        logger.info("Program started")

    def __tray_icon_activated(self, reason: int) -> None:
        """
        Callback method when the tray icon get activated through any mouse click.

        :param int reason: An integer representing the type of mouse click.
        """

        # If the application got left-clicked, restore the application.
        if reason == QSystemTrayIcon.Trigger:
            # Show the application
            self.show()

            # Set the MainWindow instance invisible on the tray
            self.__tray_icon.hide()

            # Deactivate the keyboard listener for invoking the hotkey routine method.
            utils.unhook(self.__hook)

            # Restore the CircleWindow from the hotkeys dictionary.
            for hotkey in self.__hotkeys["hotkeys"]:
                # Instanciate a new CircleWindow.
                circle_window: CircleWindow = CircleWindow(
                    tuple(self.__hotkeys["hotkeys"][hotkey]["radius"]),
                    hotkey,
                    QPoint(self.__hotkeys["hotkeys"][hotkey]['x'],self.__hotkeys["hotkeys"][hotkey]['y'])
                )

                # Show it.
                circle_window.show()

                # Add it to the circle windows list.
                self.__circle_windows.append(circle_window)

            # Reset the hotkeys dictionary.
            self.__hotkeys = {"radius": self.__hotkeys["radius"], "hotkeys": {}}

            # Trace.
            logger.info("Restore the application")

        # Otherwise, if the application got right-clicked, show the tray context menu with the exit button.
        elif reason == QSystemTrayIcon.Context:
            pos = QCursor.pos()
            self.__tray_menu.exec_(QPoint(pos.x(), pos.y() - 30))

    def __hotkey_routine(self, event: KeyboardEvent):
        """
        un the hotkey routine for clicking on the previously creates CircleWindow instances.

        :param event: The QMouseEvent received.
        :type event: keyboard._keyboard_event.KeyboardEvent
        """

        # Retrieve the event's hotkey's string value.
        event_hotkey: str = event.name.lower()

        # If the event hotkey is "right shift", update the disable_hotkeys and return.
        if event_hotkey == "right shift":
            self.__disable_hotkeys = not self.__disable_hotkeys
            return

        # If the disable_hotkeys is True, return here.
        if self.__disable_hotkeys:
            return

        # If the event hotkey is "esc", simulate a right click and return.
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
        if event_hotkey in self.__hotkeys["hotkeys"]:
            # Get the current mouse position before clicking.
            original_position = MOUSE.position

            # Move the mouse to the location to click on.
            MOUSE.position = (
                self.__hotkeys["hotkeys"][event_hotkey]['x'],
                self.__hotkeys["hotkeys"][event_hotkey]['y']
            )

            time.sleep(0.02)

            # Simulate a Left Click.
            MOUSE.click(Button.left)

            # Move the mouse back to its original position.
            MOUSE.position = original_position

            # Trace.
            logger.info(f"Hotkey {event_hotkey} pressed")

    def __load_save(self) -> None:
        """Read the hotkeys from the config.json file."""

        # Try the whole save loading mechanism. In case
        # of any exception raised, abort the loading.
        try:
            # Open the config.json file.
            with open(self.__config_file, 'r') as file:
                # Read its json-parsed content.
                json_data: typing.Dict[typing.Any, typing.Any] = json.load(file)

                # Ensure every hotkey contains a type, x and y.
                for hotkey in json_data["hotkeys"]:
                    logger.info(
                        f"""Loaded hotkey ["{hotkey}": {json_data["hotkeys"][hotkey]["type"]}, """
                        f"""({json_data["hotkeys"][hotkey]['x']};{json_data["hotkeys"][hotkey]['y']})]"""
                    )

                # Restore the CircleWindow instances.
                for hotkey in json_data["hotkeys"]:
                    # Instanciate a new CircleWindow.
                    circle_window: CircleWindow = CircleWindow(
                        tuple(json_data["hotkeys"][hotkey]["radius"]),
                        hotkey,
                        QPoint(json_data["hotkeys"][hotkey]['x'], json_data["hotkeys"][hotkey]['y'])
                    )

                    # Show it.
                    circle_window.show()

                    # Add it to the circle windows list.
                    self.__circle_windows.append(circle_window)

                # Restore the radius.
                self.__hotkeys["radius"] = json_data["radius"]
                self.__hotkey_size_slider.setValue(self.__hotkeys["radius"])


        except Exception as e:
            raise e
            logger.error("Exception encountered while loading the config.json file:", e)


    def __write_save(self) -> None:
        """Save the current hotkeys to the config.json file."""

        # Try the whole save saving mechanism. In case
        # of any exception raised, abort the saving.
        try:
            # Open the config.json file.
            with open(self.__config_file, 'w') as file:
                # Write the json-dumped hotkeys dictionary.
                file.write(json.dumps(self.__hotkeys, indent=4))

            # Trace.
            logger.info(f"Save the configuration to config.json")

        except Exception as e:
            logger.error("Exception encountered while saving the config.json file:", e)

# =-----------------------------------------------------------------------------------------------------------= #
