"""Some functions to manage files and directories

This script contains some functions to help the user to manage files and
directories.

This file can be imported as a module and contains the following functions:

    * create_directory - creates a directory if it does not exist
    * load_json - loads a JSON file
    * write_json - saves data into a JSON file
    * write_csv - saves data into a CSV file
"""

import csv
import json
import os

def create_directory(dir_name):
    """Creates a directory if it does not exist

    Parameters
    ----------
    dir_name : str
        The name of the directory to create
    """
    if not os.path.exists(dir_name) or not os.path.isdir(dir_name):
            os.mkdir(dir_name)

def load_json(filename):
    """Loads a JSON file

    Parameters
    ----------
    filename : str
        The name of the JSON file to load

    Returns
    -------
    dict
        the content of the JSON file
    """
    with open(filename, 'r') as f:
        return json.load(f)

def write_json(data, filename):
    """Saves data into a JSON file

    Parameters
    ----------
    data :
        The data to save in a JSON file
    filename : str
        The name of the JSON file in which the data must be saved
    """
    with open(filename, 'w') as fp:
        json.dump(data, fp)

# TODO finish this documentation
def write_csv(data, cols, filename):
    """Saves data into a CSV file

    Parameters
    ----------
    data :
        The data to save in a CSV file
    cols:
        ???
    filename : str
        The name of the CSV file in which the data must be saved
    """
    with open(filename,'w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(cols)
        csv_out.writerows(data)
