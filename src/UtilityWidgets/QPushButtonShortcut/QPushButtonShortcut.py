#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    QPushButtonShortcut is a single-file PySide6 custom QWidget
    class representing a QPushButton whose text get modifier
    when clicked, and wait for a shortcut to be entered.
    These shortcuts can be any combinations of keys with the
    "SHIFT", "CTRL" and "ALT" modifiers, as well as mouse buttons.
    When a QPushButtonShortcut get clicked, a TransparentFullscreenWindow
    instance is created, filling every screen and indication that
    a shortcut is waiting to be input. This TransparentFullscreenWindow
    handle any keyboard and mouse events.
    This file also contains the TransparentFullscreenWindow class
    that is used when clicking the QPushButtonShortcut for handling
    any click on the different screens of the user.

     _____________________________________________________________________
    | VERSION | DATE YYYY-MM-DD |                 CONTENT                 |
    |=====================================================================|
    |  1.0.0  |      2024-03-23 | Initial and fully functional commit.    |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

# =--------------= #
# Libraries import #
# =--------------= #

from typing            import Callable, Optional, Type, Union
from PySide6.QtCore    import Qt, QEvent, QMetaObject
from PySide6.QtGui     import QCloseEvent, QColor, QFont, QIcon, QKeyEvent, QPainter, QPaintEvent, QPixmap, QMouseEvent
from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QWidget
import typing
import keyboard
import src.utils           as utils

# =-----------------------------------------------------------------------------------------------------------------= #


# =--------= #
# Authorship #
# =--------= #

__author__       = "Quentin Raimbaud"
__contact__      = "quentin.raimbaud.contact@gmail.com"
__date__         = "2024-03-23"
__license__      = "LGPL-2.1"
__maintainer__   = "Quentin Raimbaud"
__status__       = "Development"
__version__      = "1.0.0"

# =-------------------------------------------------= #


# =-------------------------------= #
# TransparentFullscreenWindow class #
# =-------------------------------= #

class TransparentFullscreenWindow(QDialog):

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(self, _allow_mouse_buttons: bool = False) -> None:
        """Initializer method."""

        # Call the super class's initializer method.
        super().__init__()

        # Set the straight-forward attributes.
        self._allow_mouse_buttons: bool = _allow_mouse_buttons
        self._hotkey_routine_hook: Callable[[], None] = keyboard.on_press(self._hotkey_pressed)
        self._shortcut: str = ""
        self._to_be_closed: bool = False

        # Initialize the UI.
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the QPushButtonShortcut's UI."""

        # Set the Window Flags.
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        self.setMouseTracking(True)
        self.grabMouse()

        # Use an event filter to ensure this Window
        # receive any keyboard input & mouse event
        # if the allow_mouse_buttons attribute is True.
        QApplication.instance().installEventFilter(self)

    # ================== #
    # Overridden methods #
    # ================== #

    def closeEvent(self, event: QCloseEvent):
        """
        Overridden closeEvent method.
        This method is called when the QPushButtonShortcut instance get closed.

        :param PySide6.QtGui.QCloseEvent event: The QCloseEvent received.
        """

        # Unhook the hotkey_routine keyboard callback method.
        utils.unhook(self._hotkey_routine_hook)

        # Call the super class's closeEvent method.
        super().closeEvent(event)

    def eventFilter(self, watched: QWidget, event: QEvent) -> bool:

        # Handle any QEvent.KeyPress event and QEvent.MouseButtonPress
        # events if the allow_mouse_buttons attribute is True.
        event_type: Type = event.type()
        if event_type == QEvent.KeyPress:
            self.keyPressEvent(event)
        elif self._allow_mouse_buttons and event_type in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick):
            if event_type == QEvent.MouseButtonPress:
                self.mousePressEvent(event)
            else:
                self.mouseDoubleClickEvent(event)
        else:
            # Handle the remaining event normally.
            return super().eventFilter(watched, event)

        # Ensure the event is not handled by watched.
        return True

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Overridden mousePressEvent method.
        This method is called when the left mouse button is pressed on the QPushButtonShortcut.

        :param event: The QMouseEvent received.
        :type event: QMouseEvent
        """

        # Handle the click event if the
        # allow_mouse_buttons is True.
        if self._allow_mouse_buttons:
            # Update the shortcut attribute and close.
            self._shortcut = '.'.join(str(event.button()).split('.')[1:])
            self._to_be_closed = True

        # Continue propagating the MousePressEvent.
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """
        Overridden mouseDoubleClickEvent method.
        This method is called when any mouse button is double-clicked on the QPushButtonShortcut.

        :param event: The QMouseEvent received.
        :type event: QMouseEvent
        """

        # Handle the click event if the
        # allow_mouse_buttons is True.
        if self._allow_mouse_buttons:
            # Update the shortcut attribute and close.
            self._shortcut = "Double" + '.'.join(str(event.button()).split('.')[1:])
            self._to_be_closed = True

        # Continue propagating the MousePressEvent.
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Overridden mouseReleaseEvent method.
        This method is called when any mouse button is released.

        :param event: The QMouseEvent received.
        :type event: QMouseEvent
        """

        # Handle the click event if the
        # allow_mouse_buttons is True.
        if self._allow_mouse_buttons and self._to_be_closed:
            # Close the window when any mouse button is released.
            self.close()

        # Continue propagating the MousePressEvent.
        super().mousePressEvent(event)

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
        qp.setBrush(QColor(50, 50, 50, 127))

        # Initialize the variables to calculate the
        # total width and height of all screens.
        total_width: int = 0
        total_height: int = 0

        # Iterate over all screens and draw the text on each one.
        for screen in QApplication.screens():
            # Set the font size to be large enough to be readable.
            qp.setFont(QFont("Arial", 70, QFont.Bold))

            # Draw the text "Input your shortcut" centered on the current screen.
            qp.drawText(screen.geometry(), Qt.AlignCenter, "Input your shortcut")

            # Increment the size computing variables.
            total_width += screen.geometry().width()
            total_height = max(total_height, screen.geometry().height())

        # Draw a rectangle that covers all screens
        qp.drawRect(0, 0, total_width, total_height)

    # ============== #
    # Private method #
    # ============== #

    def _hotkey_pressed(self, event: utils.KeyboardEvent) -> None:
        """
        This method is called when any keyboard shortcut is pressed.

        :param event: The QKeyEvent received.
        :type event: QKeyEvent
        """

        # Retrieve the event's hotkey string.
        event_hotkey = utils.handle_hotkey(event)

        # If the event hotkey is not a handled transformer,
        # update the shortcut and close the QPushButtonShortcut.
        if not event_hotkey.endswith('+'):
            self._shortcut = event_hotkey
            QMetaObject.invokeMethod(self, typing.cast(bytes, "close"), Qt.ConnectionType.QueuedConnection)

    # ============= #
    # Getter method #
    # ============= #

    @property
    def shortcut(self) -> str:
        """
        Getter method for the shortcut attribute.

        :returns: The shortcut attribute.
        :rtype: str
        """
        return self._shortcut


# =-----------------------------------------------------------------------------------------------= #


# =-----------------------= #
# QPushButtonShortcut class #
# =-----------------------= #

class QPushButtonShortcut(QPushButton):
    """QPushButtonShortcut class representing a shortcut QPushButton."""

    # =================== #
    # Initializer methods #
    # =================== #

    def __init__(
            self,
            parent: Optional[QWidget] = None,
            text: Optional[str] = None,
            icon: Union[QIcon, QPixmap] = None,
            display_upper: bool = True,
            allow_mouse_buttons: bool = False
    ) -> None:
        """
        Initializer method.
        If parent is provided, set such a parent to the QConfigList.
        If text is provided, set such a text to the QConfigList.
        If icon is provided, set such an icon to the QConfigList.

        :param parent: The optional parent of the QConfigList to instantiate. By default, None.
        :type parent: QWidget or None
        :param text: The optional text of the QConfigList to instantiate. By default, None.
        :type text: str or None
        :param icon: The optional icon of the QConfigList to instantiate. By default, None.
        display_upper
        :type icon: QIcon or QPixmap
        :param display_upper: If True, display the button text in uppercase. By default, True.
        type display_upper: bool
        :param allow_mouse_buttons: If True, allow QMouseButtons handling while defining a shortcut. By default, False.
        type allow_mouse_buttons: bool
        """

        # Call the super class's initializer method.
        if icon is not None:
            if text is not None:
                if parent is not None:
                    super().__init__(parent=parent, text=text, icon=icon)
                else:
                    super().__init__(text=text, icon=icon)
            else:
                if parent is not None:
                    super().__init__(parent=parent, icon=icon)
                else:
                    super().__init__(icon=icon)
        else:
            if text is not None:
                if parent is not None:
                    super().__init__(parent=parent, text=text)
                else:
                    super().__init__(text=text)
            else:
                if parent is not None:
                    super().__init__(parent=parent)
                else:
                    super().__init__()

        # Set the straight-forward attributes.
        self._shortcut: str = text
        self._allow_mouse_buttons: bool = allow_mouse_buttons
        self._display_upper: bool = display_upper

        # If a text is provided and display_upper
        # is True, ensure to upper such a text.
        if text is not None and self._display_upper:
            self.setText(text.upper())

    # ================== #
    # Overridden methods #
    # ================== #

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Overridden mousePressEvent method.
        This method is called when any mouse button is pressed on the QPushButtonShortcut.

        :param event: The QMouseEvent received.
        :type event: QMouseEvent
        """

        # Create and show the transparent window
        # to handle any keyboard or mouse input.
        transparent_window = TransparentFullscreenWindow(
            _allow_mouse_buttons=self._allow_mouse_buttons
        )
        transparent_window.exec()

        # Retrieve and update both the
        # QPushButtonShortcut text and shortcut attribute.
        self._shortcut = transparent_window.shortcut
        self.setText(self._shortcut.upper() if self._display_upper else self._shortcut)

        # Continue propagating the MousePressEvent.
        super().mousePressEvent(event)

    def text(self) -> str:
        """
        Overridden text method.
        Instead of returning the QPushButtonShortcut's text (which can be uppercase
        if the display_upper attribute is True), return the shortcut attribute

        :returns: The QPushButtonShortcut's shortcut attribute.
        :rtype: str
        """
        return self._shortcut

    # ==================== #
    # Pseudo getter method #
    # ==================== #

    @property
    def true_text(self) -> str:
        """
        Pseudo getter method for the "real" text attribute, not the shortcut.

        :returns: The QPushButtonShortcut's real text attribute.
        :rtype: str
        """
        return self.text()

    # ==================== #
    # Getter/setter method #
    # ==================== #

    @property
    def shortcut(self) -> str:
        """
        Getter method for the shortcut attribute.

        :returns: The shortcut attribute.
        :rtype: str
        """
        return self._shortcut

    @shortcut.setter
    def shortcut(self, new_shortcut: str) -> None:
        """
        Setter method for the shortcut attribute.

        :param str new_shortcut: The shortcut to set..
        """
        self._shortcut = new_shortcut

# =-----------------------------------------------------------------------------------------------------------------= #
