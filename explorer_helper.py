"""Some functions to manage files and directories

This script contains some functions to help the user to manage files and
directories.

This file can be imported as a module and contains the following functions:

    * create_directory - creates a directory if it does not exist
    * load_json - loads a JSON file
    * write_csv - saves data into a CSV file
    * write_json - saves data into a JSON file
    * write_latex_table - saves data into a text file in a LaTex table format
    * write_text - saves data into a text file
"""

import csv
import json
import os
import tabulate

tabulate.LATEX_ESCAPE_RULES={}

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

def save_to_log(results, model, key, filename):
    """Saves the evolution of the confusion matrix and the f1-score in JSON file

    Parameters
    ----------
    results : dict
        The results of the classifier for different value of the threshold
    model : str
        The prefix string of the classifier
    """
    data = dict()
    for index, v in enumerate(results[key]):
        data[v] = dict()
        data[v]['tn'] = int(results['tn'][index])
        data[v]['tp'] = int(results['tp'][index])
        data[v]['fn'] = int(results['fn'][index])
        data[v]['fp'] = int(results['fp'][index])
        data[v]['score'] = float(results['score'][index])

    write_json(data, filename)

def write_csv(data, cols, filename):
    """Saves data into a CSV file

    Parameters
    ----------
    data : list
        The data to save in a CSV file
    cols: list
        The name of the columns
    filename : str
        The name of the CSV file in which the data must be saved
    """
    with open(filename,'w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(cols)
        csv_out.writerows(data)

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

def write_latex_table(data, filename):
    """Saves data into a text file in a LaTex table format

    Parameters
    ----------
    data :
        The data to save in a text file
    filename : str
        The name of the text file in which the data must be saved
    """
    latex_tab = tabulate.tabulate(data,tablefmt='latex')
    write_text(latex_tab, filename)

def write_text(data, filename):
    """Saves data into a text file

    Parameters
    ----------
    data :
        The data to save in a text file
    filename : str
        The name of the text file in which the data must be saved
    """
    with open(filename, 'w') as fp:
        fp.write(data)
