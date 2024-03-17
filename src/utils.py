#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This file contains every utility content
    used by the HotClick software.

     ___________________________________________________
    | REFER TO THE MAIN.PY FILE FOR THE CHANGEDOC TABLE |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

import typing
import keyboard

# =--------------= #


# =-------------------------------------------------= #
# REFER TO THE MAIN.PY FILE FOR THE AUTHORSHIP SECTON #
# =-------------------------------------------------= #


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
