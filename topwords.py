"""Analyzes the top n-grams in PubMed publications

This script allows the user to have an overview over the most frequent n-grams
both in DIDA publications and Not-DIDA ones.

The maximum length of studied n-grams can be configured in the configuration
file.

The script can be run through the following command :
`python topwords.py CONFIG`
where `CONFIG` is the name of the configuration file situated in the `config`
folder (without the extension).
"""

import argparse
import sys

from copy import deepcopy
from nltk import ngrams

import display
import explorer_helper as exh
import pubmed_helper as pbmdh

CONFIG = None

DIRECTORY = "topwords"
FILENAME_TEMPLATE = "documents/{0}-back.json"
TOPGRAMS_FILENAME = DIRECTORY + "/{0}grams_{1}topwords_iter{2}.json"
STOPGRAMS_FILENAME = DIRECTORY + "/{0}grams_{1}stopwords_iter{2}.json"
STRICT_TOPGRAMS_FILENAME = DIRECTORY + "/strict_top_{0}_{1}grams.json"



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

def find_unique(set1, set2, uniques):
    """Finds words that are in a list but not in another one

    Parameters
    ----------
    set1 : list
        The first list of words
    set2 : list
        The second list of words
    uniques: list
        The list that will contain the words that are in `set1` but not in `set2`
    """
    for w1 in set1:
        found = False
        for w2 in set2:
            if w1[0] == w2[0]:
                found = True
                break
        if not found:
            uniques.append(w1)



""" TOP WORDS """

def cross_top_words(dida_data, notdida_data, initial_stopwords):
    """Applies cross top words (1-grams) analysis

    Parameters
    ----------
    dida_data : list
        The publications of DIDA
    notdida_data : list
        The publications of Not-DIDA
    initial_stopwords : list
        The initial stopwords
    """
    print("Starting cross top 1-grams analysis")

    max_top = CONFIG['NTOPWORDS']
    iteration = 0
    CTW = [1] # common top words
    topwords_dict = dict()
    stopwords_dict = dict()

    while CTW:
        # Loop until there is no common top words
        CTW.clear()

        # Insert PubTator annotations in the abstracts
        dida_docs = pbmdh.extract_features(deepcopy(dida_data), initial_stopwords)
        notdida_docs = pbmdh.extract_features(deepcopy(notdida_data), initial_stopwords)

        # Search top words of each publication
        top_dida = top_words(dida_docs)
        top_notdida = top_words(notdida_docs)

        # Search common top words
        find_common_words(top_dida, top_notdida, CTW)

        # Save top words
        topwords_dict['iteration'] = iteration
        topwords_dict['CTW'] = CTW
        topwords_dict['dida'] = top_dida
        topwords_dict['notdida'] = top_notdida
        exh.write_json(topwords_dict, TOPGRAMS_FILENAME.format(1, max_top, iteration))

        if CTW:
            # If there is common top words
            # Add them to stopwords
            initial_stopwords.extend(CTW)

            # Save new stopwords list
            stopwords_dict['stopwords'] = initial_stopwords
            iteration += 1
            exh.write_json(stopwords_dict, STOPGRAMS_FILENAME.format(1, max_top, iteration))

    display.display_ok("Cross top 1-grams analysis done")

def find_common_words(set1, set2, common):
    """Finds words that are in common between two lists of words

    Parameters
    ----------
    set1 : list
        The first list of words
    set2 : list
        The second list of words
    common: list
        The list in which the common words will be appended
    """
    for w1 in set1:
        for w2 in set2:
            if w1[0] == w2[0]:
                common.append(w1[0])
                break

def find_top_words(dida_data, notdida_data, initial_stopwords):
    """Searches the top words (1-grams) of publications

    Parameters
    ----------
    dida_data : list
        The publications of DIDA
    notdida_data : list
        The publications of Not-DIDA
    initial_stopwords : list
        The initial stopwords
    """
    # Cross top words analysis
    cross_top_words(deepcopy(dida_data), deepcopy(notdida_data), deepcopy(initial_stopwords))

    # Strict top words analysis
    strict_top_words(deepcopy(dida_data), deepcopy(notdida_data), deepcopy(initial_stopwords))

def strict_top_words(dida_data, notdida_data, initial_stopwords):
    """Applies strict top words (1-grams) analysis

    Parameters
    ----------
    dida_data : list
        The publications of DIDA
    notdida_data : list
        The publications of Not-DIDA
    initial_stopwords : list
        The initial stopwords
    """
    print("Starting strict top 1-grams analysis")

    strict_top = dict()
    max_top = CONFIG['NTOPWORDS']

    # Insert PubTator annotations in the abstracts
    dida_docs = pbmdh.extract_features(deepcopy(dida_data), initial_stopwords)
    notdida_docs = pbmdh.extract_features(deepcopy(notdida_data), initial_stopwords)

    # Ordered words by number of occurrences
    top_dida = top_words(dida_docs, split=False)
    top_notdida = top_words(notdida_docs, split=False)

    top_dida_l = []
    top_notdida_l = []

    # Find words that are in DIDA but not in Not-DIDA
    find_unique(top_dida, top_notdida, top_dida_l)

    # Find words that are in Not-DIDA but not in DIDA
    find_unique(top_notdida, top_dida, top_notdida_l)

    # Select best top words of DIDA
    if (len(top_dida_l) > max_top):
        top_dida_l = top_dida_l[len(top_dida_l)-max_top:]

    # Select best top words in Not-DIDA
    if (len(top_notdida_l) > max_top):
        top_notdida_l = top_notdida_l[len(top_notdida_l)-max_top:]

    # Save the results of the strict top words analysis
    strict_top['didatop'] = top_dida_l
    strict_top['notdidatop'] = top_notdida_l
    exh.write_json(strict_top, STRICT_TOPGRAMS_FILENAME.format(max_top, 1))

    display.display_ok("Strict top 1-grams analysis done")

def top_words(docs, split=True):
    """Orders words in a set of publications by number of occurrences

    Parameters
    ----------
    docs : list
        The set of publications
    split : boolean, optional
        `True` if only the top words must be returned

    Returns
    -------
    list
        list of the ordered words
    """
    top = dict()
    max_top = CONFIG['NTOPWORDS']
    for doc in docs:
        text = doc['text'].split(' ')
        for word in text:
            top[word] = top.get(word, 0) + 1
    top = sorted(top.items(), key=lambda kv: kv[1])

    if len(top) > max_top and split:
        # Only the top words are wanted
        top = top[len(top)-max_top:]

    return top



""" TOP GRAMS """

def count_ngrams(n, docs, grams_dict):
    """Counts the number of occurrences of each publications in a list

    Parameters
    ----------
    n : int
        The length of the n-grams
    docs : list
        The list of publications
    grams_dict : dict
        The counters of each n-gram occurrences
    """
    for doc in docs:
        grams = ngrams(doc['text'].split(), n)
        for gram in grams:
            grams_dict[gram] = grams_dict.get(gram, 0) + 1

def cross_ngrams(n, dida_grams, notdida_grams):
    """Applies cross n-grams analysis

    Parameters
    ----------
    n : int
        The length of the n-grams
    dida_grams : list
        The n-grams of DIDA publications
    notdida_grams : list
        The n-grams of Not-DIDA publications
    """
    print("Starting cross top {0}-grams analysis".format(n))

    iteration = 0
    CTG = [1] # common top grams
    blacklist = []
    topgrams_dict = dict()
    blacklist_dict = dict()
    max_top = CONFIG['NTOPWORDS']

    while CTG:
        # Loop until there is no common top grams
        CTG.clear()

        grams1 = deepcopy(dida_grams)
        grams2 = deepcopy(notdida_grams)

        # Select the best top grams
        if len(grams1) > max_top :
            grams1 = grams1[len(grams1)-max_top:]
        if len(grams2) > max_top :
            grams2 = grams2[len(grams2)-max_top:]

        # Search the common grams
        for gram1 in grams1:
            for gram2 in grams2:
                if gram1[0] == gram2[0] and not gram1[0] in blacklist :
                    CTG.append(gram1[0])
                    break

        # Save the top grams
        topgrams_dict['iteration'] = iteration
        topgrams_dict['CTG'] = CTG
        topgrams_dict['dida'] = grams1
        topgrams_dict['notdida'] = grams2
        exh.write_json(topgrams_dict, TOPGRAMS_FILENAME.format(n, max_top, iteration))

        if CTG :
            # If there is common top grams
            # Add them to the blacklist
            blacklist.extend(CTG)

            # Remove them from each set of grams
            for word in CTG :
                for gram in dida_grams:
                    if gram[0] == word:
                        dida_grams.remove(gram)
                        break
                for gram in notdida_grams:
                    if gram[0] == word:
                        notdida_grams.remove(gram)
                        break

            # Save the blacklist
            blacklist_dict['stopgrams'] = blacklist
            iteration += 1
            exh.write_json(blacklist_dict, STOPGRAMS_FILENAME.format(n, max_top, iteration))

    display.display_ok("Cross top {0}-grams analysis done".format(n))

def extract_ngrams(n, dida_data, notdida_data):
    """Extracts n-grams from publications

    Parameters
    ----------
    n : int
        The length of the n-grams
    dida_data : list
        The publications of DIDA
    notdida_data : list
        The publications of Not-DIDA
    """
    print("Extracting {0}-grams".format(n))

    initial_stopwords = pbmdh.STOPWORDS

    if n == 1:
        find_top_words(deepcopy(dida_data), deepcopy(notdida_data), deepcopy(initial_stopwords))
    else:
        find_top_ngrams(n, deepcopy(dida_data), deepcopy(notdida_data), deepcopy(initial_stopwords))

    display.display_ok("Extracting {0}-grams done".format(n))

def find_top_ngrams(n, dida_data, notdida_data, initial_stopwords):
    """Searches the top n-grams of publications

    Parameters
    ----------
    n : int
        The length of the n-grams
    dida_data : list
        The publications of DIDA
    notdida_data : list
        The publications of Not-DIDA
    initial_stopwords : list
        The initial stopwords
    """
    # Insert PubTator annotations in the abstracts
    dida_docs = pbmdh.extract_features(deepcopy(dida_data), initial_stopwords)
    notdida_docs = pbmdh.extract_features(deepcopy(notdida_data), initial_stopwords)

    # Order n-grams of DIDA publications by the number of occurrences
    dida_grams = dict()
    count_ngrams(n, dida_docs, dida_grams)
    dida_grams = sorted(dida_grams.items(), key=lambda kv: kv[1])

    # Order n-grams of Not-DIDA publications by the number of occurrences
    notdida_grams = dict()
    count_ngrams(n, notdida_docs, notdida_grams)
    notdida_grams = sorted(notdida_grams.items(), key=lambda kv: kv[1])

    # Cross top n-grams analysis
    cross_ngrams(n, deepcopy(dida_grams), deepcopy(notdida_grams))

    # Strict top n-grams analysis
    strict_ngrams(n, deepcopy(dida_grams), deepcopy(notdida_grams))

def strict_ngrams(n, dida_grams, notdida_grams):
    """Applies strict top n-grams analysis

    Parameters
    ----------
    n : int
        The length of the n-grams
    dida_grams : list
        The n-grams of DIDA publications
    notdida_grams : list
        The n-grams of Not-DIDA publications
    """
    print("Starting strict top {0}-grams analysis".format(n))

    didatop = []
    notdidatop = []
    strict_top = dict()
    max_top = CONFIG['NTOPWORDS']

    # Find n-grams that are in DIDA but not in Not-DIDA
    find_unique(dida_grams, notdida_grams, didatop)

    # Find n-grams that are in Not-DIDA but not in DIDA
    find_unique(notdida_grams, dida_grams, notdidatop)

    # Select the best top grams
    if (len(didatop) > max_top):
        didatop = didatop[len(didatop)-max_top:]
    if (len(notdidatop) > max_top):
        notdidatop = notdidatop[len(notdidatop)-max_top:]

    # Save the results of the strict top grams analysis
    strict_top['didatop'] = didatop
    strict_top['notdidatop'] = notdidatop
    exh.write_json(strict_top, STRICT_TOPGRAMS_FILENAME.format(max_top, n))

    display.display_ok("Strict top {0}-grams analysis done".format(n))



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
        extract_ngrams(i, deepcopy(dida_data), deepcopy(notdida_data))

if __name__ == "__main__":
    args = check_args(sys.argv)
    run(args)
