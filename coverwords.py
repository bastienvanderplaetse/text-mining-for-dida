"""Analyzes the top n-grams in PubMed publications

This script allows the user to have an overview on which n-grams are required to
cover all the publications of each class. It also handles this issue as a
set cover problem.

The maximum length of studied n-grams can be configured in the configuration
file.

The script can be run through the following command :
`python coverwords.py CONFIG`
where `CONFIG` is the name of the configuration file situated in the `config`
folder (without the extension).
"""

import argparse
import sys

import numpy as np

from SetCoverPy import setcover

import display
import explorer_helper as exh
import ngrams_helper as ngh
import plotter as plt

CONFIG = None

DIRECTORY = "coverwords"
FILENAME_TEMPLATE = "documents/{0}.json"
ALL_NGRAMS_FILENAME = DIRECTORY + "/all_{0}grams_{1}.txt"
FIGURE_NAME = "{0} - {1}-grams"
FIG_FILENAME = DIRECTORY + "/all_{0}grams_{1}.png"
SET_COVER_FILENAME = DIRECTORY + "/set_cover_{0}_{1}grams.json"
SCORE_FILENAME = DIRECTORY + "/score_set_cover_{0}_{1}grams.txt"
TOPWORDS_FILENAME = DIRECTORY + "/topwords.json"



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

def check_score(set_cover, subsets, sets, objects):
    """Evaluates a set cover of n-grams

    Parameters
    ----------
    set_cover : list
        The set cover to evaluate
    subsets : list
        The collections of objects
    sets: list
        All the collections of objects
    objects: list
        All the objects

    Returns
    -------
    str
        text containing the scores informations
    """
    set_cover_size = len(set_cover)
    n_subsets = len(subsets)
    n_sets = len(sets)
    n_obj = len(objects)

    tot_covered_objs = []
    for subset in subsets:
        for obj in subset[3]:
            if not obj in tot_covered_objs:
                tot_covered_objs.append(obj)
    n_tot_covered_objs = len(tot_covered_objs)

    covered_objs = []
    for set in set_cover:
        for obj in set[3]:
            if not obj in covered_objs:
                covered_objs.append(obj)
    n_covered_objs = len(covered_objs)

    scores = "Total of n-grams : " + str(n_sets) + "\n" \
    + "Number of n-grams above the half : " + str(n_subsets) + "\n" \
    + "--" + "\n" \
    + "Total of documents : " + str(n_obj) + "\n" \
    + "Total of documents in n-grams above the half : " + str(n_tot_covered_objs) + "\n" \
    + "--" + "\n" \
    + "Number of n-grams in set cover : " + str(set_cover_size) + "\n" \
    + "Number of documents covered by set cover : " + str(n_covered_objs) + "\n" \
    + "Score above the half : " + str(n_covered_objs/n_tot_covered_objs) + "\n" \
    + "Score global : " + str(n_covered_objs/n_obj) + "\n" \
    + "--" + "\n" \
    + "Set Cover : " + "\n"

    for set in set_cover:
        scores = scores + "("
        for w in set[0].split(', '):
            scores = scores + w + " - "
        scores = scores + ")" + "\n"

    return scores

def filter(occurrences):
    """Filters the n-grams to keep only the most relevant ones

    Parameters
    ----------
    occurrences : list
        The list of occurrences as returned by
        ngrams_helper.normalize_occurences

    Returns
    -------
    list
        the most relevant n-grams
    """
    threshold = occurrences[0][1] * CONFIG['TETA_COVERWORDS']
    occs = filter_words(occurrences, threshold)
    return occs

def filter_words(occurrences, threshold): # returns occurrences above threshold
    """Filters the n-grams to keep only the ones having a documents coverage
    greater than a given threshold

    Parameters
    ----------
    occurrences : list
        The list of occurrences as returned by
        ngrams_helper.normalize_occurences
    threshold : float
        The threshold

    Returns
    -------
    list
        the n-grams having a documents coverage greater than the threshold
    """
    occs = []
    for occ in occurrences:
        if occ[1] >= threshold:
            occs.append(occ)
    return occs

def find_set_cover(grams, docs):
    """Marks all the n-grams required to cover all documents of a set

    Parameters
    ----------
    grams : list
        The list of occurrences as returned by
        ngrams_helper.normalize_occurences
    docs : list
        The documents to cover
    """
    pmids = []
    covered_pmids = []
    for doc in docs:
        pmids.append(doc['pmid'])
        covered_pmids.append(False)

    for i, gram in enumerate(grams):
        for pmid in gram[3]:
            index = pmids.index(pmid)
            covered_pmids[index] = True # Mark the document
            gram = (gram[0], gram[1], gram[2], gram[3], True) # Mark the n-gram
            grams[i] = gram
        if not False in covered_pmids: # All documents are covered
            break

def get_set_cover(occurrences):
    """Solves the Minimum Set Cover problem with n-grams as collections and
    documents as objects

    Parameters
    ----------
    occurrences : list
        The collections of documents

    Returns
    -------
    list
        the n-grams having a documents coverage greater than the threshold
    """
    pmids = []
    t = 0
    for gram in occurrences:
        for pmid in gram[3]:
            if not pmid in pmids:
                pmids.append(pmid)

    ncols = len(occurrences)
    mrows = len(pmids)

    relationship_matrix = np.zeros(shape=(mrows, ncols), dtype=bool)
    cost = np.ones(ncols)

    for row in range(mrows):
        for col in range(ncols):
            if pmids[row] in occurrences[col][3]:
                relationship_matrix[row, col] = True

    g = setcover.SetCover(relationship_matrix, cost)
    display.disable_print()
    solution, time_used = g.SolveSCP()
    display.enable_print()

    cover = []
    for i in range(ncols):
        if g.s[i]:
            cover.append(occurrences[i])

    return cover

def plot(occurrences, data_class, n):
    """Plots the n-grams and their coverage

    Parameters
    ----------
    occurrences : list
        The list of occurrences as returned by
        ngrams_helper.normalize_occurences
    data_class : str
        The class to handle
    n : int
        The length of the n-grams
    """
    plot_marked = []
    plot_notmarked = []
    threshold = occurrences[0][1] * CONFIG['TETA_COVERWORDS']

    for item in occurrences:
        if item[4]:
            plot_marked.append(item)
        else:
            plot_notmarked.append(item)

    marked_plotlist = [(e3, e2) for e1, e2, e3, e4, e5 in plot_marked]
    notmarked_plotlist = [(e3, e2) for e1, e2, e3, e4, e5 in plot_notmarked]

    lists = [marked_plotlist, notmarked_plotlist]
    colors = ["red", "blue"]
    threshold_color = "green"
    xlabel = "Number of occurences"
    ylabel = "Covered publications"
    figname = FIGURE_NAME.format(data_class.upper(), n)
    filename = FIG_FILENAME.format(n, data_class)
    plt.plot_dots(lists, colors, threshold, threshold_color, xlabel, ylabel, figname, filename)

def save_to_file(occurrences, n, data_class):
    """Saves the n-grams in a LaTeX table format

    Parameters
    ----------
    occurrences : list
        The list of occurrences as returned by
        ngrams_helper.normalize_occurences
    n : int
        The length of the n-grams
    data_class : str
        The class to handle
    """
    grams = []
    for occ in occurrences:
        grams.append([occ[0], occ[1], occ[2], occ[4]])

    exh.write_latex_table(grams, ALL_NGRAMS_FILENAME.format(n, data_class))

def save_topwords(topwords):
    """Saves all the n-grams selected in set covers in a JSON file

    Parameters
    ----------
    topwords : list
        All the n-grams selected in set covers
    """
    top = []
    for topword in topwords:
        if not tuple(topword[0]) in top :
            top.append(tuple(topword[0]))

    exh.write_json(top, TOPWORDS_FILENAME)



""" EXECUTION """

def process_ngrams(n, data, data_class):
    """Searches the top n-grams of a publications set and computes the set cover

    Parameters
    ----------
    n : int
        The length of the n-grams
    data : list
        The publications list to handle
    data_class : str
        The class to handle

    Returns
    -------
    list
        n-grams above the threshold fixed in config file
    list
        set cover with n-grams above the threshold
    """
    print("Process for {0}".format(data_class))

    # Number of documents in data
    n_data = len(data)

    # Count occurrences for each n-grams
    print("Counting occurrences")
    occurrences = ngh.count_occurrences(n, data)

    # Normalize the occurrences
    print("Normalizing occurrences")
    normalized = ngh.normalize_occurrences(occurrences, n_data)

    # Find n-grams above a given threshold (see Config file)
    print("Filtering occurrences")
    subsets = filter(normalized)

    # Find top n-grams covering all documents
    print("Searching full set cover")
    find_set_cover(normalized, data)

    # Save all the normalized n-grams
    save_to_file(normalized, n, data_class)

    # Plot the n-grams
    plot(normalized, data_class, n)

    # Find the Set Cover based on best n-grams
    print("Searching partial set cover")
    set_cover = get_set_cover(subsets)
    exh.write_json(set_cover, SET_COVER_FILENAME.format(data_class, n))

    print("Computing score of partial set cover")
    scores = check_score(set_cover, subsets, normalized, data)
    exh.write_text(scores, SCORE_FILENAME.format(data_class, n))

    display.display_ok("Process for {0} done".format(data_class))

    return subsets, set_cover

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

    subsets_dida = []
    subsets_notdida = []

    covers = []
    for i in range(1, n+1):
        print("Starting analysis for {0}-grams".format(i))

        # Process on DIDA class
        subset, set_cover = process_ngrams(i, dida_data, "dida")
        subsets_dida.extend(subset)
        covers.extend(set_cover)

        # Process on Not-DIDA class
        subset, set_cover = process_ngrams(i, notdida_data, "notdida")
        subsets_notdida.extend(subset)
        covers.extend(set_cover)

        display.display_ok("Analysis for {0}-grams done".format(i))

    print("Searching set cover with all grams for DIDA")
    set_cover = get_set_cover(subsets_dida)
    scores = check_score(set_cover, subsets_dida, subsets_dida, dida_data)
    exh.write_text(scores, SCORE_FILENAME.format("dida", "all"))
    display.display_ok("Done")

    print("Searching set cover with all grams for NotDIDA")
    set_cover = get_set_cover(subsets_notdida)
    scores = check_score(set_cover, subsets_notdida, subsets_notdida, notdida_data)
    exh.write_text(scores, SCORE_FILENAME.format("notdida", "all"))
    display.display_ok("Done")

    save_topwords(covers)
    display.display_info("All results were saved in {0} directory".format(DIRECTORY))

if __name__ == "__main__":
    args = check_args(sys.argv)
    run(args)
