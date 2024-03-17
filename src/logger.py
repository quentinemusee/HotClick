#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to
    the logger used by the HotClick software.

     ___________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGEDOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from colorama   import Fore, Style
from datetime   import datetime
from logging    import LogRecord
import typing
import logging
import colorama

# =----------------------------= #


# =-------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTON #
# =-------------------------------------------------= #


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

    # ================= #
    # Overriden methods #
    # ================= #

    def format(self, record: LogRecord) -> str:
        """
        Overriden format method.
        This method is called when the associated logger is tracing.

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


# =------------------------------= #
# Logging tracng wrapper functions #
# =------------------------------= #

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


# Once imported, initialize the colorama stdout
# handling and the logger automatically.
if LOGGER is None:
    colorama.init()
    init_logger()
