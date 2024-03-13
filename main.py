#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This program is a HUD allowing to
    bind hotkeys to click on screen.

     _____________________________________________________________________
    | VERSION | DATE YYYY-MM-DD |                 CONTENT                 |
    |=====================================================================|
    |  0.1.0  |      2024-03-12 | Initial release.                        |
    |---------|-----------------|-----------------------------------------|
    |  0.2.0  |      2024-03-13 | Add a mechanism to deactivate hotkeys   |
    |         |                 | when pressing the "right shift" key.    |
    |         |                 | Double the sleep time before hotkey     |
    |         |                 | click to ensure the click isn't done    |
    |         |                 | too early.                              |
    |         |                 | Handle hotkeys's ellipse with a width   |
    |         |                 | different than its height.              |
    |         |                 | Fix the hotkey's position from being    |
    |         |                 | offseted after several HUD restoration. |
    |---------|-----------------|-----------------------------------------|
    |  0.3.0  |      2024-03-13 | Add a mechanism to select the config    |
    |         |                 | file when several are available.        |
    |         |                 | Add a relative path config file parsing |
    |         |                 | mechanism.                              |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from PyQt5.QtWidgets          import QApplication, QMainWindow, QPushButton, QWidget, QInputDialog, QShortcut, \
    QSystemTrayIcon, QMenu, QAction, QSizeGrip, QSlider, QLabel, QFileDialog
from PyQt5.QtCore             import Qt, QPoint, QSize, QRect
from PyQt5.QtGui              import QPainter, QColor, QFont, QKeyEvent, QIcon, QCursor, QPaintEvent, QMouseEvent, \
QCloseEvent, QResizeEvent
from pathlib                  import Path
from keyboard._keyboard_event import KeyboardEvent
from datetime                 import datetime
from pynput.mouse             import Button, Controller
from colorama                 import Fore, Style
from logging                  import LogRecord
import typing
import os
import sys
import time
import keyboard
import json
import colorama
import logging

#TODO: Load/save the config file from a relatif path.
#TODO: display a config selection menu if several son are detected.

# =--------------------------------------------------------------------------------------------------------------= #


# =--------= #
# Authorship #
# =--------= #

__author__       = "Quentin Raimbaud"
__contact__      = "quentin.raimbaud.contact@gmail.com"
__date__         = "2024-03-13"
__maintainer__   = "Quentin Raimbaud"
__status__       = "Development"
__version__      = "0.3.0"

# =-------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Declare the logger
LOGGER: typing.Optional[logging.Logger] = None

# Declare the Mouse Controller.
MOUSE: Controller = Controller()

# Declare a keyboard hotkey input flag.
KEYBOARD_HOTKEY_INPUT_FLAG: bool = False

# Declare a disable flag.
DISABLE_FLAG: bool = False

# =----------------------------------------= #


# =-----------------------------= #
# Logging initialization function #
# =-----------------------------= #

def init_logger() -> None:
    """Initialize the program logger."""

    # Make the LOGGER global variable writable.
    global LOGGER

    # Initialize the logger with the default DEBUG level.
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)

    # Create a console handler.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Set the custom formatter for the console handler.
    console_handler.setFormatter(CustomFormatter())

    # Add the console handler to the LOGGER.
    LOGGER.addHandler(console_handler)

# =---------------------------------------------------= #


# =-------------= #
# Unhook function #
# =-------------= #

def unhook(hook: typing.Callable[..., typing.Any]) -> None:
    """
    Unhook the given hook function.

    :param hook: The hook function to unhook.
    :type hook: typing.Callable[..., typing.Any]
    """

    # Try to unhook the given hook, and if an exception occurs, ignore it.
    try:
        # Call the keyboard's unhook method.
        keyboard.unhook(hook)
    except Exception:
        pass

# =--------------------------------------------------------------------= #


# =-------------------= #
# CustomFormatter class #
# =-------------------= #

class CustomFormatter(logging.Formatter):
    """Custom Formatter class that simply override the format method.""" 

    # ================= #
    # Overriden methods #
    # ================= #

    def format(self, record: LogRecord) -> str:
        """
        Overriden format method.
        This method is called when the associated logging is tracing.

        :param record: The QPaintEvent received.
        :type record: logging.LogRecord
        """

        # Define color codes for different log levels.
        color: str
        if record.levelno == logging.WARNING:
            color = Fore.YELLOW
        elif record.levelno == logging.INFO:
            color = Fore.GREEN
        elif record.levelno == logging.ERROR:
            color = Fore.RED
        elif record.levelno == logging.CRITICAL:
            color = Fore.LIGHTRED_EX
        else:
            color = Fore.RESET
        
        # Format the log message with the color code and include the current time.
        now: datetime = datetime.now()
        return f"""{Fore.CYAN}{now.strftime("%Y-%m-%d")} {Fore.LIGHTMAGENTA_EX}{now.strftime("%H:%M:%S.%f")}""" \
            f"""{Style.RESET_ALL} | {color}{record.levelname}{(8-len(record.levelname))*' '}{Style.RESET_ALL} |""" \
            f""" {color}{record.msg}{Style.RESET_ALL}"""


# =--------------------------------------------------------------------------------------------------------------= #


# =----------------= #
# CircleWindow class #
# =----------------= #

class CircleWindow(QWidget):
    """
    Circle Window class that represent a painted movable
    frameless circle containing an editable hotkey.
    """ 

    # ================== #
    # Initializer method #
    # ================== #

    def __init__(
            self,
            hotkey_radius: typing.Tuple[int, int] = (60, 60),
            hotkey: typing.Optional[str] = None,
            position: typing.Optional[QPoint] = None
    ) -> None:
        """
        Initializer method.
        If a hotkey_radius is provided, initialize the CircleWindow with such a radius.
        If a hotkey is provided, initialize the CircleWindow with such a hotkey.
        If a position is provided, initialize the CircleWindow at such coordonates.

        :param hotkey_radius: The optional radius of the CircleWindow to instanciate. By default, (60, 60).
        :type hotkey_radius: Tuple[int, int]
        :param hotkey: The optional hotkey of the CircleWindow to instanciate. By default, None.
        :type hotkey: str or None
        :param position: The optional coordonates of the CircleWindow to instanciate. By default, None.
        :type postion: PyQt5.QtCore.QPoint or None
        """

        # Calling the super class's initializer method.
        super().__init__()

        # Initialize the straight-forward attributes.
        self.__old_position: QPoint = None
        self.__hotkey: str = hotkey if hotkey else "&"
        self.__input_hotkeys: typing.List[str] = []
        self.__last_input_hotkeys: typing.List[str] = []
        self.__is_moving: bool = False
        self.__is_resizing: bool = False
        self.__is_destroyed: bool = False

        # Call the UI initialization method to initialize the UI itself.
        self.__init_UI(hotkey_radius, position)

    # ================= #
    # Overriden methods #
    # ================= #

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Overriden paintEvent method.
        This method is called when the Widget need to update its painting.
        When the update() method is called, paintEvent is invoked.

        :param event: The QPaintEvent received.
        :type event: PyQt5.QtGui.QPaintEvent
        """

        # Initialize a QPainter instance.
        qp: QPainter = QPainter(self)

        # Set the QPainter instance antialiasing and brush color.
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setBrush(QColor(255, 0, 0, 127))

        # Give the QPainter instance an Ellipse shape.
        qp.drawEllipse(8, 8, self.width()-8, self.height()-8)
        
        # Give the QPainter instance a custom font.
        # The font depends on the number of hotkeys.
        if len(self.__last_input_hotkeys) <= 1:
            qp.setFont(QFont("Arial", 22, QFont.Bold))
        elif len(self.__last_input_hotkeys) == 2:
            qp.setFont(QFont("Arial", 14, QFont.Bold))
        elif len(self.__last_input_hotkeys) == 3:
            qp.setFont(QFont("Arial", 8, QFont.Bold))
        else:
            qp.setFont(QFont("Arial", 5, QFont.Bold))
        
        # Draw the text "A" centered within the QPainter instance.
        qp.drawText(QRect(8, 8, self.width()-8, self.height()-8), Qt.AlignCenter, self.__hotkey.upper())

    def mousePressEvent(self, event: QMouseEvent):
        """
        Overriden mousePressEvent method.
        This method is called when the left mouse button is pressed on the CircleWindow instance.

        :param event: The QMouseEvent received.
        :type event: PyQt5.QtGui.QMouseEvent
        """

        # Make KEYBOARD_HOTKEY_INPUT_FLAG global variable writable.
        global KEYBOARD_HOTKEY_INPUT_FLAG
 
        # If the event is a left click, update the old position attribute.
        if event.button() == Qt.LeftButton:
            self.__old_position = event.globalPos()

            # Trace is the CircleWindow instance just started moving.
            if not self.__is_moving:
                LOGGER.info(f"hotkey {self.__hotkey} is moving")
                self.__is_moving = True

        # Otherwise, if the event is a right click and KEYBOARD_HOTKEY_INPUT_FLAG is False
        # start the keyboard listener with the update_hotkey method as a callback.
        elif event.button() == Qt.RightButton and KEYBOARD_HOTKEY_INPUT_FLAG == False:
            self.__hook: typing.Callable[..., None] = keyboard.on_press(self.__update_hotkey)
            KEYBOARD_HOTKEY_INPUT_FLAG = True

            # Trace.
            LOGGER.info("Edit the hotkey")

        # Otherwise, if the event is a middle click (scroll button), destory the CircleWindow instance.
        elif event.button() == Qt.MiddleButton: # Check for middle mouse button press
            self.close()
            self.__is_destroyed = True

            # Trace.
            LOGGER.info("Delete the hotkey")

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Overriden mousePressEvent method.
        This method is called when the left mouse button is pressed on the CircleWindow instance.

        :param event: The QMouseEvent received.
        :type event: PyQt5.QtGui.QMouseEvent
        """

        # Update the is_moving attribute;
        self.__is_moving = False

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Overriden mouseMoveEvent method.
        This method is called when the mouse move with the CircleWindow instance focus.

        :param event: The QMouseEvent received.
        :type event: PyQt5.QtGui.QMouseEvent
        """

        # If is_resizing is True, update the old position attribute.
        if self.__is_resizing:
            self.__old_position = event.globalPos()
            self.__is_resizing = False

        # If the mouse move with the left mouse button pressed, update the CircleWindow's position.
        if event.buttons() == Qt.LeftButton and self.__old_position is not None:
            delta: QPoint = QPoint(event.globalPos() - self.__old_position)
            self.move(int(self.x() + delta.x()), int(self.y() + delta.y()))
            self.__old_position = event.globalPos()

    def resizeEvent(self, event: QResizeEvent):
        """
        Overriden resizeEvent method.
        This method is called when the CircleWindow instance get resized.

        :param event: The QMouseEvent received.
        :type event: PyQt5.QtGui.QResizeEvent
        """
        
        # Call the super class resizeEvent method.
        super().resizeEvent(event)

        # Update the grip.
        self.__update_grip()

        # Keep in memory that the CircleWindow instance is getting resized, not moved.
        self.__is_resizing = True

    # =============== #
    # Private methods # 
    # =============== #

    def __init_UI(self, radius: typing.Optional[typing.Tuple[int, int]] = (60, 60), position: typing.Optional[QPoint] = None) -> None:
        """
        Initialize the UI of the CircleWindow instance itself.
        If a hotkey_radius is provided, initialize the CircleWindow with such a radius.
        If a position is provided, initialize the UI at such coordonates.

        :param hotkey_radius: The optional radius of the CircleWindow to instanciate. By default, (60, 60).
        :type hotkey_radius: Tuple[int, int]
        :param position: The optional coordonates of the UI to instanciate.
        :type postion: PyQt5.QtCore.QPoint or None
        """

        # Set the Window Flags.
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # Set the Trahslucent Background attribute.
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set the Geometry of the Window.
        self.setGeometry(int((radius[0])/2), int((radius[1])/2), radius[0], radius[1])

        # If a position is provided, move the UI.
        if position is not None:
            rect: QRect = self.geometry() # Get the widget's geometry
            self.move(int(position.x() - rect.width() / 2), int(position.y() - rect.height() / 2))

        # Initialize the corner grip.
        self.__corner_grip: QSizeGrip = QSizeGrip(self)


    def __update_hotkey(self, event: KeyboardEvent):
        """
        Update the hotkey displayed on the CircleWindow instance.

        :param event: The QMouseEvent received.
        :type event: keyboard._keyboard_event.KeyboardEvent
        """

        # Make KEYBOARD_HOTKEY_INPUT_FLAG global variable writable.
        global KEYBOARD_HOTKEY_INPUT_FLAG

        # Retrieve the event's hotkey's string value.
        event_hotkey: str = event.name.lower()

        # If the hotkey has already been registered, return here.
        if event_hotkey in self.__input_hotkeys:
            return

        # Add the new event hotkey to the input hotkey attribute.
        self.__input_hotkeys.append(event_hotkey)

        # If the hotkey isn't among ["ctrl", "maj", "alt"], unhook the keyboard listener,
        # set KEYBOARD_HOTKEY_INPUT_FLAG to False, update the CircleWindow instance's
        # attributes, update the drawing and return here.
        if event_hotkey not in ["ctrl", "maj", "alt"]:
            unhook(self.__hook)
            KEYBOARD_HOTKEY_INPUT_FLAG = False
            self.__hotkey = '+'.join(self.__input_hotkeys)
            self.__last_input_hotkeys = self.__input_hotkeys.copy()
            self.__input_hotkeys = []
            self.update()
            return

    def __update_grip(self) -> None:
        """This method update the grip."""

        # Update the content margins.
        self.setContentsMargins(8, 8, 8, 8)

        # Retrieve the current Rect.
        outRect = self.rect()

        # Adjust the rect.
        inRect = outRect.adjusted(8, 8, -8, -8)

        # Update the grip grometry.
        self.__corner_grip.setGeometry(QRect(outRect.topLeft(), inRect.topLeft()))

    # ============== #
    # Getter methods #
    # ============== #

    @property
    def radius(self) -> typing.Tuple[int, int]:
        """Getter method for the radius attribute."""
        tmp: QSize = self.rect().size()
        return (tmp.width(), tmp.height())

    @property
    def is_destroyed(self) -> bool:
        """Getter method for the is_destroyed attribute."""
        return self.__is_destroyed

    def get_click_position_and_hotkey(self) -> typing.Tuple[str, QPoint]:
        """
        Return both the hotkey and the centered position of the CircleWindow instance.

        :returns: A tuple containing the the hotkey and the centered position of the CircleWindow instance.
        :rtype: Tuple[str, PyQt5.QtCore.QPoint]
        """

        # Simply returns the centered position and the hotkey of the CircleWindow instance
        rect: QRect = self.geometry() # Get the widget's geometry
        center_x: int = int(rect.x() + rect.width() / 2)
        center_y: int = int(rect.y() + rect.height() / 2)
        return self.__hotkey,  QPoint(center_x, center_y)

# =--------------------------------------------------------------------------------------------------------= #


# =----------------= #
# CircleWindow class #
# =----------------= #

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
        LOGGER.info("Exit the app")

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
        self.__hotkey_size_label.move(100, 10)
        self.__hotkey_size_label.setText("Hotkeys radius: 60")

        # Set the context menu for the tray icon.
        self.__tray_icon.setContextMenu(self.__tray_menu)

        # Retrieve the list of json files at the same location as this file.
        jsons: typing.List[str] = [file for file in os.listdir('.') if file.endswith(".json")]

        # If no json file is present, use an empty "config.json" file created when the hotkey routine will start.
        if not jsons:
            self.__hotkey_size_label.setText(__file__ + " | " + str(Path(__file__).parent))
            self.__config_file = Path("config.json")
            return

        # If one json only is present, use it as the config file.
        if len(jsons) == 1:
            self.__config_file = Path(jsons[0])
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
        LOGGER.info("New hotkey created")

    def __slider_value_change(self) -> None:
        """Callback function when the hotkey size slider is updated."""

        # Update the size attribute.
        self.__hotkeys["radius"] = int(self.__hotkey_size_slider.value())
        self.__hotkey_size_label.setText(f"""Hotkeys radius: {self.__hotkeys["radius"]}""")

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
                LOGGER.warning("Duplicate Hotkey:", hotkey.lower())
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
        LOGGER.info("Program started")

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
            unhook(self.__hook)

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
            LOGGER.info("Restore the application")

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

        # Make DISABLE_FLAG global variable writable.
        global DISABLE_FLAG

        # Retrieve the event's hotkey's string value.
        event_hotkey: str = event.name.lower()

        # If the event hotkey is "right shift", update DISABLE_FLAG and return.
        if event_hotkey == "right shift":
            DISABLE_FLAG = not DISABLE_FLAG
            return

        # If DISABLE_FLAG is True, return here.
        if DISABLE_FLAG:
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
            LOGGER.info(f"Hotkey {event_hotkey} pressed")

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
                    LOGGER.info(
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
            LOGGER.error("Exception encountered while loading the config.json file:", e)


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
            LOGGER.info(f"Save the configuration to config.json")

        except Exception as e:
            LOGGER.error("Exception encountered while saving the config.json file:", e)


# =-------------------------------------------------------------------------------------------------------= #


# =-----------------------------= #
# Logging initialization function #
# =-----------------------------= #

def init_logger() -> None:
    """Initialize the program logger."""

    # Make the LOGGER global variable writable.
    global LOGGER

    # Initialize the logger with the default DEBUG level.
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)

    # Create a console handler.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Set the custom formatter for the console handler.
    console_handler.setFormatter(CustomFormatter())

    # Add the console handler to the LOGGER.
    LOGGER.addHandler(console_handler)

# =---------------------------------------------------= #


# =-----------= #
# Main function #
# =-----------= #

def main() -> None:
    """Main function."""

    # Initialize the colorama stdout handling.
    colorama.init()

    # Initialize the logger.
    init_logger()

    # Initialize the QApplication.
    app = QApplication([])

    # Initialize the MainWindow and show it.
    main_window = MainWindow()
    main_window.show()

    # Run te QApplication.
    app.exec_()

# =----------------------------------------= #


#   Run the main function is
# this script is run directly.
if __name__ == '__main__':
    main()
