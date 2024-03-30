#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to
    the logger used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from PySide6.QtGui     import QColor, QPalette
from PySide6.QtWidgets import QStatusBar
from colorama          import Fore, Style
from datetime          import datetime
from logging           import LogRecord
import typing
import logging
import colorama

# =----------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Declare the logger
LOGGER: typing.Optional[logging.Logger] = None

# =----------------------------------------= #


# =-------------------= #
# CustomFormatter class #
# =-------------------= #

class CustomFormatter(logging.Formatter):
    """Custom Formatter class that simply override the format method."""

    # ================== #
    # Overridden methods #
    # ================== #

    def format(self, record: LogRecord) -> str:
        """
        Overridden format method.
        This method is called when the associated logger is tracing.

        :param record: The QPaintEvent received.
        :type record: logging.LogRecord
        """

        # Define color codes for different log levels
        # and update the associated StatusBar's style.
        color: str
        palette = getattr(LOGGER, "status_bar").palette()
        if record.levelno == logging.WARNING:
            color = Fore.YELLOW
            palette.setColor(QPalette.WindowText, QColor("yellow"))
        elif record.levelno == logging.INFO:
            color = Fore.GREEN
            palette.setColor(QPalette.WindowText, QColor("green"))
        elif record.levelno == logging.ERROR:
            color = Fore.RED
            palette.setColor(QPalette.WindowText, QColor("red"))
        elif record.levelno == logging.CRITICAL:
            color = Fore.LIGHTRED_EX
            palette.setColor(QPalette.WindowText, QColor("red").lighter(150))
        else:
            color = Fore.RESET
        getattr(LOGGER, "status_bar").setPalette(palette)

        # Update the associated StatusBar's text.
        getattr(LOGGER, "status_bar").showMessage(record.msg)
        
        # Format the log message with the color code and include the current time.
        now: datetime = datetime.now()
        out: str = f"""{Fore.CYAN}{now.strftime("%Y-%m-%d")} {Fore.LIGHTMAGENTA_EX}{now.strftime("%H:%M:%S.%f")}""" \
            f"""{Style.RESET_ALL} | {color}{record.levelname}{(8-len(record.levelname))*' '}{Style.RESET_ALL} |""" \
            f""" {color}{record.msg}{Style.RESET_ALL}"""

        # Return the formatted log message for the LOGGER to print it.
        return out


# =---------------------------------------------------------------------------------------------------------------= #


# =-------------------------------= #
# Logging tracing wrapper functions #
# =-------------------------------= #

def warning(*trace: str) -> None:
    """
    Wrapper function for the LOGGER.warning method.

    :param str trace: The trace to use for the warning.
    """

    # Call the LOGGER.warning method.
    LOGGER.warning(*trace)


def info(*trace: str) -> None:
    """
    Wrapper function for the LOGGER.info method.

    :param str trace: The trace to use for the info.
    """

    # Call the LOGGER.info method.
    LOGGER.info(*trace)


def error(*trace: str) -> None:
    """
    Wrapper function for the LOGGER.error method.

    :param str trace: The trace to use for the error.
    """

    # Call the LOGGER.error method.
    LOGGER.error(*trace)


def critical(*trace: str) -> None:
    """
    Wrapper function for the LOGGER.critical method.

    :param str trace: The trace to use for the critical.
    """

    # Call the LOGGER.critical method.
    LOGGER.critical(*trace)

# =--------------------------------------------------= #


# =----------------------------= #
# Logger initialization function #
# =----------------------------= #

def init_logger(status_bar: QStatusBar) -> None:
    """
    Initialize the program logger.

    :param QStatusBar status_bar: The QStatusBar to associate with this logger.
    """

    # Initialize the colorama stdout handling.
    colorama.init()

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

    # Add a new attribute to the logger: the QStatusBar to associate with it.
    setattr(LOGGER, "status_bar", status_bar)

# =-------------------------------------------------------------------------= #
