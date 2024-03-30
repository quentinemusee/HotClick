#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    CircleWindow class used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from src.config        import CONFIG
from PySide6.QtCore    import Qt, QPoint, QRect, QSize
from PySide6.QtGui     import QColor, QFont, QPainter, QMouseEvent, QPaintEvent, QResizeEvent
from PySide6.QtWidgets import QSizeGrip, QWidget
from src.config        import STYLE
import typing
import src.logger          as logger
import keyboard
import string
import src.utils           as utils

# =---------------------------------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


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

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(
            self,
            virtual_parent: typing.Optional[QWidget] = None,
            hotkey: typing.Optional[str] = None,
            position: typing.Optional[QPoint] = None,
            size: QSize = QSize(60, 60)
    ) -> None:
        """
        Initializer method.
        If virtual_parent is provided, set such a virtual_parent to the CircleWindow.
        If a hotkey is provided, initialize the CircleWindow with such a hotkey.
        If a position is provided, initialize the CircleWindow at such coordinates.
        If a size is provided, initialize the CircleWindow with such a size.

        :param virtual_parent: The optional virtual_parent of the CircleWindow to instantiate. By default, None.
        :type virtual_parent: QWidget or None
        :param hotkey: The optional hotkey of the CircleWindow to instantiate. By default, None.
        :type hotkey: str or None
        :param position: The optional coordinates of the CircleWindow to instantiate. By default, None.
        :type position: PySide6.QtCore.QPoint or None
        :param size: The optional size of the CircleWindow to instantiate. By default, (60, 60).
        :type size: QSize or None
        """

        # Call the super class's initializer method.
        super().__init__()

        # Initialize the straight-forward attributes.
        self.__virtual_parent: typing.Optional[QWidget] = virtual_parent
        self.__old_position: typing.Optional[QPoint] = None
        self.__hotkey: str = hotkey if hotkey else \
            next(c for c in string.printable if c not in getattr(self.__virtual_parent, "hotkeys"))
        self.__input_hotkeys: typing.List[str] = []
        self.__last_input_hotkeys: typing.List[str] = []
        self.__hook: typing.Optional[typing.Callable[..., None]] = None
        self.__is_resizing: bool = False

        # Call the UI initialization method to initialize the UI itself.
        self.__init_ui(position, size)

        # Trace.
        logger.info(f"New hotkey \"{self.__hotkey.upper()}\" created")

    def __init_ui(
            self,
            position: typing.Optional[QPoint] = None,
            size: QSize = QSize(60, 60)
    ) -> None:
        """
        Initialize the UI of the CircleWindow instance itself.
        If a position is provided, initialize the UI at such coordinates.
        If a size is provided, initialize the CircleWindow with such a size.

        :param position: The optional coordinates of the UI to instantiate.
        :type position: PySide6.QtCore.QPoint or None
        :param size: The optional size of the CircleWindow to instantiate. By default, (60, 60).
        :type size: QSize or None
        """

        # Set the Window Flags.
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # Set the Translucent Background attribute.
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set the Geometry of the Window.
        self.setGeometry(100, 100, size.width(), size.height())

        # If a position is provided, move the UI.
        if position is not None:
            self.move(position.x() - self.width(), position.y() - self.height())
            # self.move(position)

        # Initialize the corner grip.
        self.__corner_grip: QSizeGrip = QSizeGrip(self)

    # ================== #
    # Overridden methods #
    # ================== #

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Overridden paintEvent method.
        This method is called when the Widget need to update its painting.
        When the update() method is called, paintEvent is invoked.

        :param PySide6.QtGui.QPaintEvent event: The QPaintEvent received.
        """

        # Initialize a QPainter instance.
        qp: QPainter = QPainter(self)

        # Set the QPainter instance antialiasing and brush color.
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setBrush(QColor("#80" + STYLE["Custom"]["circlewindow-background-color"][1:]))

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
        Overridden mousePressEvent method.
        This method is called when the left mouse button is pressed on the CircleWindow instance.

        :param PySide6.QtGui.QMouseEvent event: The QMouseEvent received.
        """

        # Make KEYBOARD_HOTKEY_INPUT_FLAG global variable writable.
        global KEYBOARD_HOTKEY_INPUT_FLAG
 
        # If the event is a left click, update the old position attribute.
        # The MainWindow's config dictionary will be updated once the mouse's click get released.
        if event.button() == Qt.LeftButton:
            self.__old_position = event.globalPosition().toPoint()

            # Trace.
            logger.info(f"Move the hotkey \"{self.__hotkey.upper()}\" from ({self.pos().x()};{self.pos().y()})")

        # Otherwise, if the event is a right click and KEYBOARD_HOTKEY_INPUT_FLAG is False
        # start the keyboard listener with the update_hotkey method as a callback.
        # The MainWindow's config dictionary will be updated once a new valid and unique hotkey get pressed.
        elif event.button() == Qt.RightButton and not KEYBOARD_HOTKEY_INPUT_FLAG:
            self.__hook = keyboard.on_press(self.__update_hotkey)
            KEYBOARD_HOTKEY_INPUT_FLAG = True

            # Trace.
            logger.info(f"Edit the hotkey \"{self.__hotkey.upper()}\"")

        # Otherwise, if the event is a middle click (scroll button), destroy the CircleWindow instance.
        # Update also the MainWindow's config dictionary.
        elif event.button() == Qt.MiddleButton:
            self.close()
            self.deleteLater()
            getattr(self.__virtual_parent, "circle_windows").remove(self)
            utils.update_dict(CONFIG, "hotkeys", self.__hotkey.lower(), delete=True)

            # Set KEYBOARD_HOTKEY_INPUT_FLAG to False
            # and unhook the hook function if it exists.
            if self.__hook is not None:
                KEYBOARD_HOTKEY_INPUT_FLAG = False
                utils.unhook(self.__hook)

            # Trace.
            logger.info(f"Delete the hotkey \"{self.__hotkey.upper()}\"")

        # Continue propagating the MousePressEvent.
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Overridden mousePressEvent method.
        This method is called when the left mouse button is pressed on the CircleWindow instance.

        :param PySide6.QtGui.QMouseEvent event: The QMouseEvent received.
        """

        # If the event is a left click, update the CONFIG dictionary.
        if event.button() == Qt.LeftButton:

            # Call the utils.update_dict method twice with the corresponding arguments.
            utils.update_dict(CONFIG, "last_position", value=[self.position.x(), self.position.y()])
            utils.update_dict(
                CONFIG,
                "hotkeys",
                self.hotkey.lower(),
                value={
                    "type": "Click",
                    'x': self.position.x(),
                    'y': self.position.y(),
                    'w': self.size.width(),
                    'h': self.size.height()
                }
            )

            # Trace.
            logger.info(f"Move the hotkey \"{self.__hotkey.upper()}\" to ({self.pos().x()};{self.pos().y()})")

        # Continue propagating the MousePressEvent.
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Overridden mouseMoveEvent method.
        This method is called when the mouse move with the CircleWindow instance focus.

        :param PySide6.QtGui.QMouseEvent event: The QMouseEvent received.
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

        # Continue propagating the MousePressEvent.
        super().mousePressEvent(event)

    def resizeEvent(self, event: QResizeEvent):
        """
        Overridden resizeEvent method.
        This method is called when the CircleWindow instance get resized.

        :param PySide6.QtGui.QResizeEvent event: The QMouseEvent received.
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

    def __update_hotkey(self, event: utils.KeyboardEvent):
        """
        Update the hotkey displayed on the CircleWindow instance.

        :param event: The QMouseEvent received.
        :type event: utils.KeyboardEvent
        """

        # Make KEYBOARD_HOTKEY_INPUT_FLAG global variable writable.
        global KEYBOARD_HOTKEY_INPUT_FLAG

        # Retrieve the event's hotkey string value.
        event_hotkey: str = event.name.lower()

        # If the hotkey has already been registered, return.
        if event_hotkey in self.__input_hotkeys:
            return

        # Add the new event hotkey to the input hotkey attribute.
        self.__input_hotkeys.append(event_hotkey)

        # If the hotkey isn't among ["ctrl", "maj", "alt"], unhook the keyboard listener,
        # set KEYBOARD_HOTKEY_INPUT_FLAG to False and update the CircleWindow instance's attributes
        if event_hotkey not in ["ctrl", "maj", "alt"]:

            # Ensure the hotkey isn't already applied to another CircleWindow
            hotkey: str = '+'.join(self.__input_hotkeys)
            if hotkey in getattr(self.__virtual_parent, "hotkeys"):
                logger.error(f"Hotkey \"{hotkey}\" is already assigned!")
                self.__input_hotkeys = []
                return

            utils.unhook(self.__hook)
            KEYBOARD_HOTKEY_INPUT_FLAG = False
            previous_hotkey: str = self.__hotkey
            self.__hotkey = hotkey
            self.__last_input_hotkeys = self.__input_hotkeys.copy()
            self.__input_hotkeys = []
            self.update()

            # Update the CONFIG dictionary by calling the utils.update_dict
            # method twice with the corresponding arguments.
            utils.update_dict(CONFIG, "hotkeys", previous_hotkey.lower(), delete=True)
            utils.update_dict(
                CONFIG,
                "hotkeys",
                self.hotkey.lower(),
                value={
                    "type": "Click",
                    'x': self.position.x(),
                    'y': self.position.y(),
                    'w': self.size.width(),
                    'h': self.size.height()
                }
            )

            # Trace.
            logger.info(f"Hotkey edited to \"{self.__hotkey.upper()}\"")

    def __update_grip(self) -> None:
        """This method update the grip."""

        # Update the content margins.
        self.setContentsMargins(8, 8, 8, 8)

        # Retrieve the current Rect.
        out_rect = self.rect()

        # Adjust the rect.
        in_rect = out_rect.adjusted(8, 8, -8, -8)

        # Update the grip geometry.
        self.__corner_grip.setGeometry(QRect(out_rect.topLeft(), in_rect.topLeft()))

    # ============== #
    # Getter methods #
    # ============== #

    @property
    def hotkey(self) -> str:
        """
        Getter method for the CircleWindow's hotkey attribute.

        :returns: The CircleWindow's hotkey.
        :rtype: str
        """
        return self.__hotkey

    @property
    def position(self) -> QPoint:
        """
        Getter method for the CircleWindow's coordinates.

        :returns: The CircleWindow's coordinates as a QPoint.
        :rtype: QPoint
        """
        return self.pos() + QPoint(self.width(), self.height())

    @property
    def size(self) -> QSize:
        """
        Getter method for the CircleWindow's size.

        :returns: The CircleWindow's size.
        :rtype: QSize
        """
        return QSize(self.geometry().width(), self.geometry().height())

# =----------------------------------------------------------------------------------------------------------= #
