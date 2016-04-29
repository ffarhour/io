#!/usr/bin/env python
"""Contains useful functions that are not necessary for proper functionality of scripts.

Author: Farmehr Farhour f.farhour@gmail.com

Contains:
bcolors class: that can be imported and used to color commandline outputs using ANSI colors.
"""

class bcolors:
    """Used to implement ANSI colors without the need to remember the numbers.

    Does not contain any methods. Only contains variables.

    Usage: simply concatenate bcolors.<color> at the start of string to be printed,
        and bcolors.ENDC at the end of the string, to color the string with the
        specified color.
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
