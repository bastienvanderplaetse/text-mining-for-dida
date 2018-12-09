"""Some functions to make custom displays

This script contains some functions to help the user to display colored messages.

This file can be imported as a module and contains the following functions:

    * display - prints a message with a specific color
    * display_fail - prints an error message in red
    * display_ok - prints a success message in green
    * display_info - prints an informative message in blue
"""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def display(message, color):
    """Prints a message with a specific color

    Parameters
    ----------
    message : str
        The message to print
    color : bcolors
        The color used to print the message
    """
    print(color + bcolors.BOLD + message + bcolors.ENDC)

def display_fail(message):
    """Prints an error message in red

    Parameters
    ----------
    message : str
        The message to print
    """
    display(message, bcolors.FAIL)

def display_ok(message):
    """Prints a success message in green

    Parameters
    ----------
    message : str
        The message to print
    """
    display(message, bcolors.OKGREEN)

def display_info(message):
    """Prints an informative message in blue

    Parameters
    ----------
    message : str
        The message to print
    """
    display(message, bcolors.OKBLUE)
