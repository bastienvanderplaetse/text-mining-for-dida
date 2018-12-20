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

def count_occurrences(n, documents):
    """Counts the number of documents covered by each n-grams in a documents set

    Parameters
    ----------
    n : int
        The length of the n-grams
    documents: list
        The documents set

    Returns
    -------
    list
        list of tuples (g, x), where g is the n-gram and x is a dict object in
        which the 'docs' key gives the documents covered by the n-gram and the
        'occurrences' key gives the number of occurrences of the n-gram in the
        documents set; the tuples are ordered by the number of covered documents
    """
    occurences = dict()

    for doc in documents:
        for gram in doc["grams"][str(n)]:
            s_gram = ', '.join(gram)
            if not s_gram in occurences:
                occurences[s_gram] = dict()
                occurences[s_gram]["docs"] = []
                occurences[s_gram]["occurrences"] = 0

            occurences[s_gram]["occurrences"] += 1

            if not doc["pmid"] in occurences[s_gram]["docs"]:
                occurences[s_gram]["docs"].append(doc["pmid"])

    occurences = sorted(occurences.items(), key=lambda kv: (len(kv[1]['docs']),kv[1]['occurrences']))
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

def normalize_occurrences(occurences, n_docs):
    """Normalizes the number of documents covered by each n-grams in a documents
    set

    Parameters
    ----------
    occurences : list
        The list of tuples returned by count_occurences
    n_docs: int
        The total number of documents

    Returns
    -------
    list
        list of tuples (e1, e2, e3, e4, False), where e1 is the n-gram, e2 is
        the normalized number of documents covered by the n-gram, e3 is the
        number of occurrences of the n-grams in the documents set and e4 is
        the list of covered documents
    """
    normalized = []
    tot_occurrences = 0
    for gram in occurences:
        tot_occurrences += gram[1]['occurrences']
        data = (gram[0], len(gram[1]['docs'])/n_docs, gram[1]['occurrences'], gram[1]['docs'], False)
        normalized.append(data)

    return normalized
