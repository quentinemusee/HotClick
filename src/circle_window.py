#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    CircleWindow class used by the HotClick software.

     ___________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGEDOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from PySide6.QtCore           import Qt, QPoint, QRect
from PySide6.QtGui            import QColor, QFont, QPainter, QMouseEvent, QPaintEvent, QResizeEvent
from PySide6.QtWidgets        import QSizeGrip, QWidget
from keyboard._keyboard_event import KeyboardEvent
import typing
import logger
import keyboard
import utils

# =----------------------------------------------------------------------------------------------= #


# =-------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTON #
# =-------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Declare a keyboard hotkey input flag.
KEYBOARD_HOTKEY_INPUT_FLAG: bool = False

# =----------------------------------= #


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
            self.__old_position = event.globalPosition().toPoint()

            # Trace is the CircleWindow instance just started moving.
            if not self.__is_moving:
                logger.info(f"hotkey {self.__hotkey} is moving")
                self.__is_moving = True

        # Otherwise, if the event is a right click and KEYBOARD_HOTKEY_INPUT_FLAG is False
        # start the keyboard listener with the update_hotkey method as a callback.
        elif event.button() == Qt.RightButton and KEYBOARD_HOTKEY_INPUT_FLAG == False:
            self.__hook: typing.Callable[..., None] = keyboard.on_press(self.__update_hotkey)
            KEYBOARD_HOTKEY_INPUT_FLAG = True

            # Trace.
            logger.info("Edit the hotkey")

        # Otherwise, if the event is a middle click (scroll button), destory the CircleWindow instance.
        elif event.button() == Qt.MiddleButton: # Check for middle mouse button press
            self.close()
            self.__is_destroyed = True

            # Trace.
            logger.info("Delete the hotkey")

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
            self.__old_position = event.globalPosition().toPoint()
            self.__is_resizing = False

        # If the mouse move with the left mouse button pressed, update the CircleWindow's position.
        if event.buttons() == Qt.LeftButton and self.__old_position is not None:
            tmp: QPoint = event.globalPosition().toPoint()
            delta: QPoint = QPoint(tmp - self.__old_position)
            self.move(int(self.x() + delta.x()), int(self.y() + delta.y()))
            self.__old_position = tmp

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

    def __init_UI(
            self,
            radius: typing.Optional[typing.Tuple[int, int]] = (60, 60),
            position: typing.Optional[QPoint] = None
    ) -> None:
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
            utils.unhook(self.__hook)
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

# =-----------------------------------------------------------------------------------------------------= #
