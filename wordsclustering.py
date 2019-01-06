import argparse
import sys

import numpy as np

from copy import deepcopy

import display
import explorer_helper as exh
import ibmethod as ib

CONFIG = None

DIRECTORY = "wordsclustering"
FILENAME_TEMPLATE = "documents/{0}.json"

W = []
Pw = dict()
Ndw = dict()
Pcw = None
Ncw = None
n_docs = []

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
def save_clusters(clusters):
    data = dict()
    data['clusters'] = clusters
    data['Ndw'] = Ndw
    data['W'] = W

    directory = DIRECTORY + '/' + CONFIG['ALL_CLUSTERS_DIRECTORY']
    exh.create_directory(directory)

    # filename = DIRECTORY + '/' + CONFIG['ALL_CLUSTERS_FILENAME']
    filename = directory + "/ndw.json"
    exh.write_json(Ndw, filename)

    filename = directory + "/W.json"
    exh.write_json(W, filename)

    cluster_directory = directory + "/clusters"
    exh.create_directory(cluster_directory)

    for i, c in clusters.items():
        filename = cluster_directory + "/{0}.json".format(i)
        exh.write_json(c, filename)

    display.display_info("Data clusters saved into " + directory)

''' WORDS INFORMATION EXTRACTION '''

def extract_words_information(all_docs):
    n_words = 0
    for i in range(len(all_docs)):
        s = "Extracting words of documents set {0} / {1}".format(i+1, len(all_docs))
        print (s, end="\r")
        # print("Extract words of documents set {0} / {1}".format((i+1), len(all_docs)))
        # category = CLASSES[i]
        category = CONFIG['CLUSTERING_CLASSES'][i]
        Ndw[category] = dict()

        for doc in all_docs[i]:
            pmid = doc['pmid']
            Ndw[category][pmid] = dict()
            for word in doc['text'].split(' '):
                if not word in W:
                    W.append(word)
                    Pw[word] = 0
                Pw[word] += 1

                if not word in Ndw[category][pmid]:
                    Ndw[category][pmid][word] = 0
                Ndw[category][pmid][word] += 1
                n_words += 1

    print(s)

    W.sort()

    for word in W:
        Pw[word] = Pw[word] / n_words



''' JOIN PROBABILITY DISTRIBUTION '''

def word_occurences_in_category(category, word):
    if Ncw[category][word] == 0:
        tot = 0
        cat_name = CONFIG['CLUSTERING_CLASSES'][category] #CLASSES[category]
        w_label = W[word]

        for doc_id in Ndw[cat_name]:
            if w_label in Ndw[cat_name][doc_id]:
                tot += Ndw[cat_name][doc_id][w_label]

        Ncw[category][word] = tot + 0.5

    return Ncw[category][word]


def joint_probability_distribution():
    global Pcw, Ncw

    n_c = len(CONFIG['CLUSTERING_CLASSES'])#len(CLASSES)
    n_w = len(W)
    Pcw = np.zeros((n_c, n_w))
    Ncw = np.zeros((n_c, n_w))

    for c in range(n_c):
        for w in range(n_w):
            Pcw[c, w] = word_occurences_in_category(c, w)

    Pcw = Pcw / sum(sum(Pcw))

''' EXECUTION '''

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

    # docs = [deepcopy(dida_data), deepcopy(notdida_data)]
    docs = [deepcopy(notdida_data), deepcopy(dida_data)]
    display.display_ok("Loading publications done")

    print("Starting extraction of words information")
    extract_words_information(docs)
    display.display_ok("Extraction of words information done")

    print("Computing joint probability distribution")
    joint_probability_distribution()
    display.display_ok("Computing joint probability distribution done")

    print("Starting IB method")
    all_clusters = ib.cluster(deepcopy(Pcw), deepcopy(Pw))
    display.display_ok("IB method finished")

    save_clusters(all_clusters)

if __name__ == "__main__":
    args = check_args(sys.argv)
    run(args)
