import argparse
import sys

from copy import deepcopy

import display
import explorer_helper as exh

CONFIG = None
DIRECTORY = "wordsclustering"
FILENAME_TEMPLATE = "documents/{0}.json"

""" CONFIGURATION """

def check_args(argv):
    """Checks and parses the arguments of the command typed by the user

    Parameters
    ----------
    argv :
        The arguments of the command typed by the user

    Returns
    -------
    ArgumentParser
        the values of the arguments of the commande typed by the user
    """
    parser = argparse.ArgumentParser(description="Searches the top words in a\
        publications file")
    parser.add_argument('CONFIG', type=str, help="the name of the configuration file (without extension)")
    args = parser.parse_args()

    return args

""" EXECUTION """

def run(args):
    """Executes the main process of the script

    Parameters
    ----------
    args : ArgumentParser
        The arguments of the command typed by the user
    """
    global CONFIG
    CONFIG = exh.load_json("config/{0}.json".format(args.CONFIG))

    print("Loading publications")
    # Load DIDA publications
    dida_data = exh.load_json(FILENAME_TEMPLATE.format(CONFIG['DIDA_DOCS']))
    # Load Not-DIDA publications
    notdida_data = exh.load_json(FILENAME_TEMPLATE.format(CONFIG['NOTDIDA_DOCS']))

    docs = [deepcopy(dida_data), deepcopy(notdida_data)]
    display.display_ok("Loading publications done")

    data_filename = DIRECTORY + '/' + CONFIG['ALL_CLUSTERS_FILENAME']
    data = exh.load_json(data_filename)

    print(data)

if __name__ == "__main__":
    args = check_args(sys.argv)
    run(args)
