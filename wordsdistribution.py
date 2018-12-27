"""Analyzes the n-grams distributions in PubMed publications

This script allows the user to have an overview on the distribution of n-grams
in PubMed publications in order to use the Words Distribution based classifiers.

The maximum length of studied n-grams can be configured in the configuration
file.

The script can be run through the following command :
`python wordsdistribution.py CONFIG`
where `CONFIG` is the name of the configuration file situated in the `config`
folder (without the extension).
"""

import argparse
import sys

import display
import explorer_helper as exh
import ngrams_helper as ngh

CONFIG = None

DIRECTORY = "wordsdistribution"
FILENAME_TEMPLATE = "documents/{0}.json"
FILENAME = DIRECTORY + "/{0}-grams.csv"



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



""" FUNCTIONS """

def merge_ngrams(grams1, grams2):
    """Merge to list of n-grams by keeping their score in each class

    Parameters
    ----------
    grams1 : list
        The first list of n-grams
    grams2 : list
        The second list of n-grams

    Returns
    -------
    dict
        a dict object containing the score of each n-gram in each class
    """
    print("Merging n-grams")
    merged = dict()
    dida = CONFIG['DIDA_DOCS']
    notdida = CONFIG['NOTDIDA_DOCS']

    for gram in grams1:
        if not gram[0] in merged:
            # Create the gram
            merged[gram[0]] = dict()
            merged[gram[0]][dida] = gram[1]
            # Prepare value for notDIDA
            merged[gram[0]][notdida] = 0

    for gram in grams2:
        if not gram[0] in merged:
            # Create the gram
            merged[gram[0]] = dict()
            # Value is 0 for DIDA because gram was not in grams1
            merged[gram[0]][dida] = 0
        merged[gram[0]][notdida] = gram[1]

    display.display_ok("Merging done")

    return merged

def ordered(merged, f_score):
    """Order n-grams of a dict using a particular score function

    Parameters
    ----------
    merged : dict
        The dict containing n-grams and their score for each class
    f_score : function
        The score function to use to order n-grams

    Returns
    -------
    list
        the ordered list of n-grams
    """
    print("Ordering grams")

    dida = CONFIG['DIDA_DOCS']
    notdida = CONFIG['NOTDIDA_DOCS']

    merged = sorted(merged.items(), key=lambda kv: f_score(kv[1][dida], kv[1][notdida]))
    merged.reverse()

    display.display_ok("Ordering done")

    return merged

def save_to_file(merged, n):
    """Save a list of n-grams in a CSV file

    Parameters
    ----------
    merged : list
        The list containing n-grams and their score for each class
    n : int
        The length of the n-grams
    """
    dida = CONFIG['DIDA_DOCS']
    notdida = CONFIG['NOTDIDA_DOCS']

    l_merged = []
    for word in merged:
        ngram = "(" + word[0] + ")"
        l_merged.append((ngram, word[1][dida], word[1][notdida], (word[1][dida] - word[1][notdida])))

    exh.write_csv(l_merged, ["N-gram", "% DIDA", "% NotDIDA", "Diff"], FILENAME.format(n))
    display.display_info("Results saved in " + FILENAME.format(n))



""" SCORE FUNCTIONS """

def score(d, n):
    """Perform the absolute value of difference between DIDA score and NotDIDA score

    Parameters
    ----------
    d : float
        The DIDA score of a gram
    n : float
        The NotDIDA score of a gram

    Returns
    -------
    float
        the absolute value of the difference
    """
    return abs(d-n)



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

    exh.create_directory(DIRECTORY)

    print("Loading publications")
    # Load DIDA publications
    dida_data = exh.load_json(FILENAME_TEMPLATE.format(CONFIG['DIDA_DOCS']))
    # Load Not-DIDA publications
    notdida_data = exh.load_json(FILENAME_TEMPLATE.format(CONFIG['NOTDIDA_DOCS']))
    display.display_ok("Loading publications done")

    n = CONFIG['NGRAMS']

    for i in range(1, n+1):
        print("Starting analysis for {0}-grams".format(i))

        print("Couting occurrences for DIDA")
        dida_occurrences = ngh.count_occurrences(i, dida_data)
        dida_normalized = ngh.normalize_occurrences(dida_occurrences, len(dida_data))
        display.display_ok("Counting occurrences for DIDA done")

        print("Couting occurrences for NotDIDA")
        notdida_occurrences = ngh.count_occurrences(i, notdida_data)
        notdida_normalized = ngh.normalize_occurrences(notdida_occurrences, len(notdida_data))
        display.display_ok("Counting occurrences for NotDIDA done")

        # Merge n-grams in the same list
        merged = merge_ngrams(dida_normalized, notdida_normalized)

        # Order n-grams by difference
        merged = ordered(merged, score)

        # Save results
        save_to_file(merged, i)

        display.display_ok("Analysis for {0}-grams done".format(i))

if __name__ == "__main__":
    args = check_args(sys.argv)
    run(args)
