#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains everything related to the
    configurations files used by the HotClick software.
    These configurations files are the user hotkey and
    custom key mapping configurations as well as the
    theme file.

     ____________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGE DOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from typing       import Any, Dict, List, Union
from pathlib      import Path
from src.utils    import PATH
import copy
import json
import src.logger     as logger
import src.utils      as utils

# =--------------------------------------= #


# =--------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTION #
# =--------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# CONFIG_FILE path.
CONFIG_FILE: List[Path] = [Path(r"C:\Users\quent\Desktop\HotClick\configs\config.json")]

# CONFIG and DEFAULT_CONFIG dictionaries.
DEFAULT_CONFIG: Dict[str, Union[int, str, List[int], Dict[str, Dict[str, Union[str, int]]], Dict[str, str]]] = {
    "radius": 60,
    "last_position": None,
    "last_setting_menu": None,
    "hotkeys": {},
    "shortcuts": {
        "builtin": {
            "New": "CTRL+N",
            "Open": "CTRL+O",
            "Save As...": "CTRL+S",
            "Settings": "CTRL+ALT+S",
            "New Hotkey": 'N',
            "Start": 'S',
            "Disable Hotkeys": '*'
        },
        "custom": {}
    }
}
CONFIG = copy.deepcopy(DEFAULT_CONFIG)

# STYLE and DEFAULT_STYLE dictionaries.
DEFAULT_STYLE: Dict[str, Union[str, Dict[str, str]]] = {
    "color": "#ffe7e7",
    "background-color": "#367582",
    "font-family": "Titillium Web",
    "QPushButton": {
        "background-color": "#c6b9e8"
    },
    "QPushButton:checked": {
        "background-color": "#64826d"
    },
    "QPushButton:pressed": {
        "background-color": "#4b3d82"
    },
    "QPushButton:disabled": {
        "background-color": "#333333"
    },
    "QPushButton:hover": {
        "border-color": "#4488BB"
    },
    "QStatusBar": {
        "background-color": "#18529a"
    },
    "Custom": {
        "middleground-color": "#106c94",
        "invalid-color": "#FF0000",
        "selected-background-color": "#087e06"
    }
}
STYLE = copy.deepcopy(DEFAULT_STYLE)

# =------------------------------------------= #


# =----------------------= #
# Config utility functions #
# =----------------------= #

def load_config() -> bool:
    """
    Load the CONFIG_FILE to the CONFIG dictionary
    and return the boolean result of such a parsing.

    :returns: The boolean result of the parsing
    :rtype: bool
    """

    # If CONFIG_FILE is an empty list, return false.
    if not CONFIG_FILE:
        return False

    # Make the CONFIG global variable writable.
    global CONFIG

    # Try the whole config loading mechanism. In case
    # of any exception raised, abort the loading.
    try:
        # Open the config.json file.
        with open(CONFIG_FILE[0], 'r') as file:
            # Read its json-parsed content.
            loaded_config: Dict[Any, Any] = json.load(file)

            # Ensure the config contains the "radius" value.
            logger.info(f"""Loaded radius: {loaded_config["radius"]}""")

            # Ensure the config contains the "last_position" value.
            logger.info(f"""Loaded last position: {loaded_config["last_position"]}""")

            # Ensure the config contains the "last_setting_menu" value.
            logger.info(f"""Loaded last setting menu: {loaded_config["last_setting_menu"]}""")

            # Ensure every hotkey contains the required values.
            for hotkey in loaded_config["hotkeys"]:
                logger.info(
                    f"""Loaded hotkey: ["{hotkey}": {loaded_config["hotkeys"][hotkey]["type"]}, """
                    f"""({loaded_config["hotkeys"][hotkey]['x']};{loaded_config["hotkeys"][hotkey]['y']})] """
                    f"""<{loaded_config["hotkeys"][hotkey]['w']};{loaded_config["hotkeys"][hotkey]['h']}>"""
                )

            # Ensure every shortcut contains the required values.
            for shortcut in loaded_config["shortcuts"]["builtin"]:
                logger.info(
                    f"""Loaded builtin shortcut: [{shortcut}: {loaded_config["shortcuts"]["builtin"][shortcut]}"""
                )
            for shortcut in loaded_config["shortcuts"]["custom"]:
                logger.info(
                    f"""Loaded custom shortcut: [{shortcut}: {loaded_config["shortcuts"]["custom"][shortcut]}"""
                )

            # Update the CONFIG dictionary.
            for key in loaded_config.keys():
                utils.update_dict(CONFIG, key, value=loaded_config[key])

        # Trace.
        logger.info(f"Open the config inside \"{CONFIG_FILE[0].parent}\" directory")
        logger.info(f"Open the config called \"{CONFIG_FILE[0].name}\"")

        # The parsing is a success: return True.
        return True

    except (FileNotFoundError, PermissionError, IsADirectoryError, json.JSONDecodeError, TypeError, KeyError) as e:
        # Trace such an exception.
        logger.error("Exception raised while loading the config file: " + str(e))
        logger.error("Config file loading failed")

        # The parsing is a failure: return False.
        return False


def save_config() -> None:
    """
    Save the CONFIG dictionary to the CONFIG_FILE.
    This function is a wrapper to utils.json_write.
    """

    # Call utils.json_write with the appropriated arguments.
    utils.json_write(CONFIG, CONFIG_FILE[0])


def reset_config() -> None:
    """
    Reset the CONFIG dictionary.
    This function is a wrapper to update_dict.
    """

    # Call update_dict with the appropriated arguments.
    utils.update_dict(CONFIG, value=DEFAULT_CONFIG)

# =-------------------------------------------------------------------------------------------------------------= #


# =---------------------= #
# Theme utility functions #
# =---------------------= #

def load_style() -> bool:
    """
    Load the theme.json file to the STYLE dictionary
    and return the boolean result of such a parsing.

    :returns: The boolean result of the parsing
    :rtype: bool
    """

    # Make the STYLE global variable writable.
    global STYLE

    # Try the whole style loading mechanism. In case
    # of any exception raised, abort the loading.
    try:
        # Open the theme.json file and load its content.
        with open(PATH / Path("theme.json")) as theme:
            loaded_style: Dict[Any, Any] = json.load(theme)

            # Update the STYLE dictionary.
            for key in loaded_style.keys():
                utils.update_dict(STYLE, key, value=loaded_style[key])

        # The parsing is a success: return True.
        return True

    except Exception as e:
        # Trace such an exception.
        logger.error("Exception raised while loading the theme file: " + str(e))
        logger.error("Theme file loading failed")

        # The parsing is a failure: return False.
        return False


def save_style() -> None:
    """
    Save the STYLE dictionary to the theme file.
    This function is a wrapper to utils.json_write.
    """

    # Call utils.json_write with the appropriated arguments.
    utils.json_write(STYLE, PATH / Path("theme.json"))

# =-----------------------------------------------------------------= #
