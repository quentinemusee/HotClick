#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    YesNoCancelDialog class used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

# =--------------= #
# Libraries import #
# =--------------= #

from PySide6.QtGui     import QCloseEvent
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget
from enum              import Enum
import typing

# =-------------------------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =------------------= #
# YesNoCancelEnum enum #
# =------------------= #

class YesNoCancelEnum(Enum):
    """Yes / No / Cancel enum."""
    UNKNOWN = 0
    YES     = 1
    NO      = 2
    CANCEL  = 3

# =---------------------------= #


# =------------------= #
# SettingsDialog class #
# =------------------= #

class YesNoCancelDialog(QDialog):
    """
    Yes No Cancel Dialog class that is
    a QDialog with a text and three options.
    """

    # ================== #
    # Initializer method #
    # ================== #

    def __init__(
            self,
            title: str,
            text: str,
            no_cancel_button: bool = False,
            parent: typing.Optional[QWidget] = None
    ) -> None:
        """
        Initializer method.
        If parent is provided, set such a parent to the YesNoCancelDialog.

        :param str title: The title of the YesNoCancelDialog.
        :param str text: The text of the YesNoCancelDialog.
        :param bool no_cancel_button:: If True, don't add a cancel button.
        :param parent: The optional parent of the YesNoCancelDialog to instantiate. By default, None.
        :type parent: QWidget or None
        """

        # Call the super class's initializer method.
        super().__init__(parent)

        # Initialize the straight-forward attribute.
        self.__result: YesNoCancelEnum = YesNoCancelEnum.UNKNOWN

        # Set the title of the Window.
        self.setWindowTitle(title)

        # Set the Button Box.
        if not no_cancel_button:
            self.buttonBox = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.No |
                QDialogButtonBox.StandardButton.Cancel
            )
        else:
            self.buttonBox = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.No
            )
        self.buttonBox.accepted.connect(self.yes)
        self.buttonBox.button(QDialogButtonBox.StandardButton.No).clicked.connect(self.no)
        if not no_cancel_button:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.cancel)

        # Set the QDialog's layout Label text.
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel(text))
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    # ================== #
    # Overridden methods #
    # ================== #

    def closeEvent(self, event: QCloseEvent):
        """
        Overridden closeEvent method.
        This method is called when the YesNoCancelDialog instance get closed.

        :param PySide6.QtGui.QCloseEvent event: The QCloseEvent received.
        """

        # If the result attribute is YesNoCancelEnum.UNKNOWN
        # set it to YesNoCancelEnum.CANCEL.
        if self.__result == YesNoCancelEnum.UNKNOWN:
            self.__result = YesNoCancelEnum.CANCEL

    # ================ #
    # Callback methods #
    # ================ #

    def yes(self) -> None:
        """Yes button callback."""

        # Update the res attribute.
        self.__result = YesNoCancelEnum.YES

        # Close the YesNoCancelDialog.
        self.close()

    def no(self) -> None:
        """No button callback."""

        # Update the res attribute.
        self.__result = YesNoCancelEnum.NO

        # Close the YesNoCancelDialog.
        self.close()

    def cancel(self) -> None:
        """Cancel button callback."""

        # Update the res attribute.
        self.__result = YesNoCancelEnum.CANCEL

        # Close the YesNoCancelDialog.
        self.close()

    # ============= #
    # Getter method #
    # ============= #

    @property
    def result(self) -> YesNoCancelEnum:
        """
        Getter method for the YesNoCancelDialog's result attribute.

        :returns: The YesNoCancelDialog's style.
        :rtype: YesNoCancelEnum
        """
        return self.__result

# =------------------------------------------------------------------------------------------------------------------= #
