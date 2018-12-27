"""Trains and evaluates classifiers for words distribution

This script allows the user to train and evaluate Strict Classifier, Split
Weighted Classifier and Weighted Classifier based on the words distribution
obtained by using the wordsdistribution.py script.

It evaluates these models for each value of the threshold between 0 and X with
a step equals to Y. X and Y corresponds to the values
WORDS_DISTRIBUTION_MAX_THRESHOLD and WORDS_DISTRIBUTION_STEP_THRESHOLD defined
in the config file.

The script can be run through the following command :
`python wordsdistribution_classification.py CONFIG`
where `CONFIG` is the name of the configuration file situated in the `config`
folder (without the extension).
"""

import argparse
import sys

import numpy as np

from copy import deepcopy
from sklearn.metrics import confusion_matrix, f1_score

import display
import explorer_helper as exh
import plotter as plt

from classifiers.wordsdistribution import StrictClassifier, SplitWeightedClassifier, WeightedClassifier

CONFIG = None

DIRECTORY = "wordsdistribution"
FILENAME_TEMPLATE = "documents/{0}.json"
DISTRIBUTION_FILENAME_TEMPLATE = DIRECTORY + "/{0}-grams.csv"
FSCORE_FILENAME = DIRECTORY + "/fscore.png"
LOG_FILENAME = DIRECTORY + "/{0}.json"



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

def csv_filenames(n):
    """Prepares names of all CSV files containing n-grams distribution

    Parameters
    ----------
    n : int
        The maximum length of n-grams

    Returns
    -------
    list
        the list of file names
    """
    names = []
    for i in range(1, n+1):
        name = DISTRIBUTION_FILENAME_TEMPLATE.format(i)
        names.append(name)
    return names

def save_to_log(results, model):
    """Saves the evolution of the confusion matrix and the f1-score in JSON file

    Parameters
    ----------
    results : dict
        The results of the classifier for different value of the threshold
    model : str
        The prefix string of the classifier
    """
    data = dict()
    for index, threshold in enumerate(results['threshold']):
        data[threshold] = dict()
        data[threshold]['tn'] = int(results['tn'][index])
        data[threshold]['tp'] = int(results['tp'][index])
        data[threshold]['fn'] = int(results['fn'][index])
        data[threshold]['fp'] = int(results['fp'][index])
        data[threshold]['score'] = float(results['score'][index])

    exh.write_json(data, LOG_FILENAME.format(model))

def train(Classifier, data, csv_files, y_true):
    """Trains a classifier with a range of thresholds based on words distribution

    Parameters
    ----------
    Classifier : Classifier
        The type of classifier to train
    data : list
        The list of publications composing the data set
    csv_files : list
        The list of CSV files containing the words distribution
    y_true : list
        The list of the true classes of each publication in the training set

    Returns
    -------
    dict
        the evolutions of the confusion matrix and the list of all evaluated
        threshold
    """
    max_threshold = CONFIG['WORDS_DISTRIBUTION_MAX_THRESHOLD']
    threshold = max_threshold
    step = CONFIG['WORDS_DISTRIBUTION_STEP_THRESHOLD']

    threshold_l = []
    tn_l = []
    fp_l = []
    fn_l = []
    tp_l = []
    score_l = []

    while threshold > 0:
        s = "Threshold {0} ({1} %)".format(threshold, int(((max_threshold-threshold)/max_threshold)*100))
        print (s, end="\r")

        # Initialize the classifier
        classifier = Classifier(threshold, csv_files, CONFIG['DIDA_DOCS'], CONFIG['NOTDIDA_DOCS'])

        # Predict the class of each publication
        y_pred = classifier.predict(data)

        # Confusion matrix of the predictions
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        # F1-score of the classifier
        score = f1_score(y_true, y_pred)

        threshold_l.append(threshold)
        tn_l.append(tn)
        fp_l.append(fp)
        fn_l.append(fn)
        tp_l.append(tp)
        score_l.append(score)

        threshold -= step
    print("Threshold 1 (100 %)")

    return {
        "threshold": threshold_l,
        "tn": tn_l,
        "fp": fp_l,
        "fn": fn_l,
        "tp": tp_l,
        "score": score_l
    }



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

    csv_files = csv_filenames(n)

    # Real labels of each publication
    y_true = np.append(np.ones(len(dida_data)), np.zeros(len(notdida_data)))

    data = deepcopy(dida_data)
    data.extend(deepcopy(notdida_data))

    scores = []
    classifiers_names = []

    print("Strict Classifier training")
    results = train(StrictClassifier, deepcopy(data), csv_files, y_true)
    plt.plot_confusion_matrix(results, len(dida_data), len(notdida_data), 'strict_', DIRECTORY)
    scores.append(results['score'])
    save_to_log(results, 'strict')
    classifiers_names.append("Strict Classifier")
    display.display_ok("Strict Classifier training done")

    print("Split Weighted Classifier training")
    results = train(SplitWeightedClassifier, deepcopy(data), csv_files, y_true)
    plt.plot_confusion_matrix(results, len(dida_data), len(notdida_data), 'splitweighted_', DIRECTORY)
    scores.append(results['score'])
    save_to_log(results, 'splitweighted')
    classifiers_names.append("Split Weighted Classifier")
    display.display_ok("Split Weighted Classifier training done")

    print("Weighted Classifier training")
    results = train(WeightedClassifier, deepcopy(data), csv_files, y_true)
    plt.plot_confusion_matrix(results, len(dida_data), len(notdida_data), 'weighted_', DIRECTORY)
    scores.append(results['score'])
    save_to_log(results, 'weighted')
    classifiers_names.append("Weighted Classifier")
    display.display_ok("Weighted Classifier training done")

    plt.plot_lines(results['threshold'], scores, classifiers_names, FSCORE_FILENAME, "Threshold", "F1-score")
    display.display_info("Results saved in {0}".format(DIRECTORY))

if __name__ == "__main__":
    args = check_args(sys.argv)
    run(args)
