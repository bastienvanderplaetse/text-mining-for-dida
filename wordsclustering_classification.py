import argparse
import sys

import numpy as np

from copy import deepcopy

import converter
import display
import explorer_helper as exh
import plotter as plt

from classifiers.wordsclustering import NaiveBayesCluster

CONFIG = None
DIRECTORY = "wordsclustering"
FILENAME_TEMPLATE = "documents/{0}.json"
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

def add_result(n_clusters, predictions, result):
    result['n_clusters'].append(n_clusters)
    result['tn'].append(predictions['tn'])
    result['fp'].append(predictions['fp'])
    result['fn'].append(predictions['fn'])
    result['tp'].append(predictions['tp'])
    result['score'].append(predictions['score'])

def save_to_log(results, model, key):
    """Saves the evolution of the confusion matrix and the f1-score in JSON file

    Parameters
    ----------
    results : dict
        The results of the classifier for different value of the threshold
    model : str
        The prefix string of the classifier
    """
    data = dict()
    for index, n_clusters in enumerate(results['n_clusters']):
        data[n_clusters] = dict()
        data[n_clusters]['tn'] = int(results['tn'][index])
        data[n_clusters]['tp'] = int(results['tp'][index])
        data[n_clusters]['fn'] = int(results['fn'][index])
        data[n_clusters]['fp'] = int(results['fp'][index])
        data[n_clusters]['score'] = float(results['score'][index])

    exh.write_json(data, LOG_FILENAME.format(model))

def classification(docs, Ndw, W, directory, true_predictions):
    strict_result = {
        "n_clusters": [],
        "tn": [],
        "fp": [],
        "fn": [],
        "tp": [],
        "score": []
    }
    doublon_result = {
        "n_clusters": [],
        "tn": [],
        "fp": [],
        "fn": [],
        "tp": [],
        "score": []
    }

    print("Documents replacement")
    converted_docs = converter.init(deepcopy(docs), deepcopy(W))
    display.display_ok("Documents replacement done")

    clusters_directory = directory + "/clusters"
    max_clusters = len(W)

    print("Evaluating classifier")
    a = [1,2,3,4,5,6,7,8,9,10]
    a.extend(range(100,8500,100))
    a.extend([8417])
    for n_clusters in a:#range(1, max_clusters+1,100):
        print("Processing for {0} clusters (Total : {1})".format(n_clusters, max_clusters))

        # Load clusters
        clusters = exh.load_json(clusters_directory + "/{0}.json".format(n_clusters))

        # Prepare classifier
        classifier = NaiveBayesCluster(deepcopy(clusters), deepcopy(Ndw), deepcopy(W))
        print("Classifier ready")

        print("Converting documents")
        strict_converted_docs = converter.convert_all(deepcopy(converted_docs), deepcopy(clusters))
        doublon_converted_docs = converter.convert_all(deepcopy(converted_docs), deepcopy(clusters), method='d')
        print("Converting documents done")

        print("Evaluate Strict Predictions")
        strict_predictions = classifier.evaluate(strict_converted_docs)
        print("Evaluate Doublon Predictions")
        doublon_predictions = classifier.evaluate(doublon_converted_docs)
        print("Predictions done")
        print("Perform scores")
        strict_score = classifier.score(true_predictions, strict_predictions)
        doublon_score = classifier.score(true_predictions, doublon_predictions)
        print("Scores performed : ({0}, {1})".format(strict_score, doublon_score))
        add_result(n_clusters, strict_score, strict_result)
        add_result(n_clusters, doublon_score, doublon_result)

    display.display_ok("Evaluating classifier done")
    return strict_result, doublon_result


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

    # docs = [deepcopy(notdida_data), deepcopy(dida_data)]
    docs = [deepcopy(dida_data), deepcopy(notdida_data)]
    display.display_ok("Loading publications done")

    data_directory = DIRECTORY + '/' + CONFIG['ALL_CLUSTERS_DIRECTORY']
    Ndw = exh.load_json(data_directory + "/ndw.json")
    W = exh.load_json(data_directory + "/W.json")

    # Real labels of each publication
    # y_true = np.append(np.zeros(len(notdida_data)), np.ones(len(dida_data)))
    y_true = np.append(np.ones(len(dida_data)), np.zeros(len(notdida_data)))
    strict_result, doublon_result = classification(docs, Ndw, W, data_directory, y_true)

    plt.plot_confusion_matrix(strict_result, len(dida_data), len(notdida_data), "strict_", "n_clusters", "Number of clusters", DIRECTORY, step=1000)
    exh.save_to_log(strict_result, "strict", "n_clusters", LOG_FILENAME.format("strict"))
    plt.plot_confusion_matrix(doublon_result, len(dida_data), len(notdida_data), "doublon_", "n_clusters", "Number of clusters", DIRECTORY, step=1000)
    exh.save_to_log(doublon_result, "doublon", "n_clusters", LOG_FILENAME.format("doublon"))

    scores = [strict_result['score'], doublon_result['score']]
    classifiers_names = ["Strict converter", "Doublon converter"]

    plt.plot_lines(strict_result['n_clusters'], scores, classifiers_names, FSCORE_FILENAME, "Number of clusters", "F1-score", step=1000)


if __name__ == "__main__":
    args = check_args(sys.argv)
    run(args)
