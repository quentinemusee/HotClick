#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains every utility content
    used by the HotClick software.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from pathlib import Path
import typing
import os
import sys
import logger
import keyboard

# =------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Retrieve and declare the binary directory path.
PATH: Path = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else Path(__file__).parent.parent

# Left/Right braces characters and Backslash.
LB: str = '{'
RB: str = '}'
BS: str = '\\'

# =---------------------------------------------------------------------------------------------------------= #


# =---= #
# Types #
# =---= #

KeyboardEvent: typing.Type = typing.TypeVar("KeyboardEvent")

# =------------------------------------------------------= #


# =-------------------------= #
# Opposite HEX color function #
# =-------------------------= #

def opposite_hex_color(hex_color: str) -> str:
    """
    Return the opposite color of the provided one.

    :param str hex_color: The provided hex color.
    """

    # Ignore the '#' first char if it exists.
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]

    # Expect hex_color to be a 6 char long string,
    # but this function is unsafe and doesn't ensure it.
    out: str = '#'
    for i in range(3):
        tmp: str = hex(255 - int(hex_color[2*i:2*(i+1)], 16))[2:]
        if len(tmp) == 1:
            tmp = '0' + tmp
        out += tmp
    return out

# =-----------------------------------------------------------= #


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
    except Exception as e:
        logger.critical(str(e))

# =--------------------------------------------------------------------= #


# =-----------------------= #
# Config file name function #
# =-----------------------= #

def next_config_file_name_available(path: Path) -> Path:
    """
    Compute the next config file name available (i.e.: non existing).

    :param Path path: The directory to compute the next config file name available.
    :returns: The next config file name available.
    :rtype: Path
    """

    # Return PATH / config.json if such a file doesn't exist, otherwise
    # return PATH / configX.json, X being the first number available starting as 1.
    return (path / Path("config.json")) if not (path / Path("config.json")).exists() \
        else path / next(
        (Path(f"config{i}.json") for i in range(1, 2**16) if not (path / Path(f"config{i}.json")).exists())
    )

# =-----------------------------------------------------------------------------------------------------= #
