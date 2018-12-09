"""Prepare PubMed publications before classification tasks

This script allows the user to prepare PubMed publications before classification.
This process is done by extracting n-grams for each publication. The maximum
value of `n` can be modified in the configuration file.

The script can be run through the following command :
`python prepare.py FILE OUTPUT CONFIG`
where `FILE` is a .txt file containing a list of PMIDs or a .json file
containing publications downloaded with the `download.py` script,
`OUPUT` is the name of the output file to save the publications and their n-grams
(this name must be the same as the configuration field `DIDA_DOCS` or
`NOTDIDA_DOCS` for easier use)
and `CONFIG` is the name of the configuration file situated in the `config`
folder (without the extension).
"""

import argparse
import sys

import display
import explorer_helper as exh
import ngrams_helper as ngh
import pubmed_helper as pbmdh

CONFIG = None

DIRECTORY = "documents"
BACK_FILENAME = DIRECTORY + "/{0}-back.json"
NGRAMS_FILENAME = DIRECTORY + "/{0}.json"
LEGAL_EXTENSIONS = ["txt", "json"]



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
    parser = argparse.ArgumentParser(description="Prepares publications \
        for classification")
    parser.add_argument('FILE', type=str, help="the name of the file \
        containing PMIDs or publications at JSON format. \
        Can eventually containing the corresponding label")
    parser.add_argument('OUTPUT', type=str, help="the name of the output \
        file (without extension)")
    parser.add_argument('CONFIG', type=str, help="the name of the configuration \
        file (without extension)")

    args = parser.parse_args()

    return args



""" FUNCTIONS """

def read_file(filename, extension):
    """Returns publications based on a text file containing PMIDs or a JSON file
    containing publications

    Parameters
    ----------
    filename :
        The name of the file to read
    extension :
        The extension of the file

    Returns
    -------
    list
        a list of publications at JSON format
    """
    if extension == "txt":
        print("Received a text file - Reading PMIDs list")
        # Read each PMID in the file
        f = open(filename)
        lines = f.readlines()
        pmids = []
        for line in lines:
            pmids.append(line.replace('\n', ''))
        f.close()

        # Downloads and returns publications
        print("Downloading publications")
        return pbmdh.download_publications(pmids)
    elif extension == "json":
        print("Received a JSON file - Getting publications")
        return exh.load_json(filename)



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

    # Extension of the input file
    extension = args.FILE.split('.')[-1]

    if extension in LEGAL_EXTENSIONS:
        exh.create_directory(DIRECTORY)

        # Get publications
        print("Getting publications")
        documents_l = read_file(args.FILE, extension)
        display.display_ok("Getting publications done")

        # Save publications
        filename = BACK_FILENAME.format(args.OUTPUT)
        exh.write_json(documents_l, filename)
        display.display_info("Publications saved in {0}".format(filename))

        # Insert PubTator annotations in the abstracts
        print("Inserting PubTator annotations in abstracts")
        docs = pbmdh.extract_features(documents_l)
        display.display_ok("Inserting PubTator annotations in abstracts done")

        # Extract n-grams
        print("Extracting n-grams")
        ngh.extract_ngrams(docs, CONFIG['NGRAMS'])
        display.display_ok("Extracting n-grams done")

        # Save publications and their n-grams
        filename = NGRAMS_FILENAME.format(args.OUTPUT)
        exh.write_json(docs, filename)
        display.display_info("Publications and n-grams saved in {0}".format(filename))
    else:
        # The input file has not a valid extension
        display.display_fail("Extension of input file not supported. Required : txt or json. Received : {0}".format(extension))
        sys.exit(0)

if __name__=="__main__":
    args = check_args(sys.argv)
    run(args)
