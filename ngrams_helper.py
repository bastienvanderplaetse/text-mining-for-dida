"""Some functions to work with n-grams

This script contains some functions to help the user to deal with n-grams in
PubMed publications.

This file can be imported as a module and contains the following functions:

    * count_occurences -
    * extract_ngrams - extracts the n-grams of a set of publications
    * normalize_occurences -
"""

from nltk import ngrams

# def prepare_documents_ngrams(docs, n):
#     for doc in docs:
#         doc["grams"] = dict()
#         for i in range(1, n+1):
#             doc["grams"][i] = []

def count_occurences(n, documents):
    occurences = dict()

    for doc in documents:
        for gram in doc["grams"][n]:
            if not gram in occurences:
                occurences[gram] = dict()
                occurences[gram]["docs"] = []
                occurences[gram]["occurences"] = 0

            occurences[gram]["occurences"] += 1

            if not doc["pmid"] in occurences[gram]["docs"]:
                occurences[gram]["docs"].append(doc["pmid"])

    occurences = sorted(occurences.items(), key=lambda kv: (len(kv[1]['docs']),kv[1]['occurences']))
    occurences.reverse()

    return occurences

def extract_ngrams(documents, n):
    """Extracts the n-grams of a set of publications

    Parameters
    ----------
    documents : list
        The list of documents for which n-grams extraction is required
    n : int
        The maximum size of n-grams that need to be extracted
    """
    for doc in documents:
        grams_l = []
        doc['grams'] = dict()
        for i in range(1, n+1):
            doc['grams'][i] = []
            grams = ngrams(doc['text'].split(), i)
            for gram in grams:
                doc['grams'][i].append(gram)

def normalize_occurences(occurences, n_docs):
    normalized = []
    tot_occ = 0
    for gram in occurences:
        tot_occ += gram[1]['occurences']
        data = (gram[0], len(gram[1]['docs'])/n_docs, gram[1]['occurences'], gram[1]['docs'], False)
        normalized.append(data)

    return normalized
