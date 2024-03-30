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

from typing            import Any, Callable, Dict, Optional, Type, TypeVar, Union
from PySide6.QtWidgets import QLayout, QLayoutItem
from pathlib           import Path
import src.logger          as logger
import os
import sys
import keyboard
import json

# =---------------------------------------------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Retrieve and declare the binary directory path.
PATH: Path = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else Path(__file__).parent.parent

# =---------------------------------------------------------------------------------------------------------= #


# =---= #
# Types #
# =---= #

KeyboardEvent: Type = TypeVar("KeyboardEvent")

# =----------------------------------------= #


# =-------------------= #
# Clear layout function #
# =-------------------= #

def clear_layout(layout: Optional[QLayout]) -> None:
    """
    Clear the given layout, calling the deleteLater
    method recursively on children widgets and layouts.

    :param str layout: The provided hex color.
    """

    # If layout is None, return here.
    if layout is None:
        return

    # Iterate over the given layout's items in
    # the reverse order to call the deleteLater
    # method on its widgets and the clear_layout
    # recursively on its children layouts.
    for i in reversed(range(layout.count())):
        item: QLayoutItem = layout.takeAt(i)
        if item.widget() is not None:
            item.widget().deleteLater()
            item.widget().setParent(None)
        elif item.layout() is not None:
            clear_layout(item.layout())

# =-------------------------------------------------= #


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


# =------------------------= #
# Is valid Shortcut function #
# =------------------------= #

def is_valid_shortcut(shortcut: str) -> bool:
    """
    Determine if the provided shortcut string is valid.

    :param shortcut: The shortcut string to be checked.
    :type shortcut: str
    """

    # Upper the shortcut to be case-insensitive.
    shortcut = shortcut.upper()

    # Remove any handled modifiers
    # in the handled order.
    if shortcut.startswith("SHIFT+"):
        shortcut = shortcut[6:]
    if shortcut.startswith("CTRL+"):
        shortcut = shortcut[5:]
    if shortcut.startswith("ALT+"):
        shortcut = shortcut[4:]

    # Expect the remaining
    # shortcut to be handled
    # by the ord function.
    try:
        ord(shortcut)
        return True
    except TypeError:
        return False

# =-------------------------------------------------= #


# =----------------= #
# Keyboard functions #
# =----------------= #

def handle_hotkey(event: KeyboardEvent) -> str:
    """
    Handle the given hotkey event, adding
    the ctrl, maj and alt optional transformers.
    Return the handled hotkey string.

    :param event: The QMouseEvent received.
    :type event: KeyboardEvent
    """

    # Retrieve the event's hotkey string value.
    event_hotkey: str = event.name.lower()

    # If the event_hotkey is a handled
    # transformer, use an empty string instead.
    if event_hotkey in ["ctrl", "maj", "alt"]:
        event_hotkey = ""

    # Compute the base hotkey.&
    base: str = ""
    if keyboard.is_pressed("ctrl"):
        base += "ctrl+"
    if keyboard.is_pressed("maj"):
        base += "maj+"
    if keyboard.is_pressed("alt"):
        base += "alt+"

    # Return the event hotkey with its base.
    return base + event_hotkey


def unhook(hook: Callable[..., Any]) -> None:
    """
    Unhook the given hook function.

    :param hook: The hook function to unhook.
    :type hook: typing.Callable[..., typing.Any]
    """

    # Try to unhook the given hook, and if an exception occurs, ignore it.
    try:
        # Call the keyboard's unhook method.
        keyboard.unhook(hook)
    except KeyError:
        pass
    except Exception as e:
        logger.critical(str(e))

# =--------------------------------------------------------------------= #


# =-----------------------= #
# Config file name function #
# =-----------------------= #

def next_config_file_name_available(path: Path) -> Path:
    """
    Compute the next config file name available (i.e.: non-existing).

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


# =-------------------------= #
# Dictionary utility function #
# =-------------------------= #

def json_write(dictionary: Dict[Any, Any], file: Path) -> None:
    """
    Write the dumped given dictionary to the provided file.

    :param dictionary: The dictionary to write to the provided file.
    :type dictionary: Dict[Any, Any]
    :param file: The file to be written the provided dictionary.
    :type file: pathlib.Path
    """

    # Open the provided file and write it
    # the dumped given dictionary.
    with open(file, 'w') as theme:
        theme.write(json.dumps(dictionary, indent=4))


def update_dict(dictionary: Dict[Any, Any], *keys: str, value: Any = None, delete: bool = False) -> None:
    """
    Edit the provided dictionary giving the keys to access the value to edit.
    If a value is provided, assign such a value to the corresponding keys from the dictionary argument.
    If delete is True, delete the corresponding keys from the dictionary argument.

    :param dictionary: The dictionary to edit the value.
    :type dictionary: Dict[Any, Any].
    :param keys: keys to access the desired element from the provided dictionary.
    :type keys: str
    :param value: The new value to set to such an element from the provided dictionary. By default, None.
    :type value: Any
    :param bool delete: If True, delete the corresponding keys from the provided dictionary.
    :type delete: bool
    """

    # If no keys are provided, then remove every value
    # and assign the ones from the values argument.
    # If value is not iterable, trace an error.
    if not len(keys):
        for key in list(dictionary.keys()):
            del dictionary[key]
        try:
            for key in value:
                dictionary[key] = value[key]
        except TypeError:
            logger.error("Trying to assign a non-iterable value to a dictionary.")
        return

    # Retrieve such an element from the given keys within the provided dictionary.
    elem: Dict[str, Any] = dictionary
    for key in keys[:-1]:
        elem = elem[key]

    # Delete it if delete is True, otherwise assign the given value.
    if delete:
        del elem[keys[-1]]
    else:
        elem[keys[-1]] = value


def access_dict(dictionary: Union[Dict[Any, Any], Any], *keys: str) -> Any:
    """
    Access the provided dictionary's value giving the keys to access such a value.

    :param dictionary: The dictionary to access the value.
    :type dictionary: Dict[Any, Any].
    :param keys: keys to access the desired element from the provided dictionary.
    :type keys: str
    """

    # If no more keys, return the dictionary argument itself.
    if not len(keys):
        return dictionary

    # Otherwise, call this function recursively with
    # the first key removed from the arguments.
    return access_dict(dictionary[keys[0]], *keys[1:])

# =---------------------------------------------------------------------------------------------------= #
