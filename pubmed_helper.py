"""Some functions to interact with PubTator and deal with PubMed publications

This script contains some functions to help the user to deal with PubMed
publications.

This file can be imported as a module and contains the following functions:

    * clean_text - lowerizes and stems publications abstracts
    * download_publications - downloads publications based on a PMIDs list
    * extract_features - inserts PubTator annotations inside the publications abstracts
    * get_pmids - gets a PMIDs list based on a particular query
"""

import json
import urllib.request as req
import xml.etree.ElementTree as ET

from copy import deepcopy
from nltk.stem import PorterStemmer
from string import punctuation

import explorer_helper as exh

STOPWORDS = exh.load_json("config/stopwords.json")['stopwords']
URL_DOWNLOAD = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/BioConcept/{0}/JSON/"
URL_PMIDS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={0}&retmax={1}"

def clean_text(text, stopwords=STOPWORDS):
    """Lowerizez and stems publications abstracts

    Parameters
    ----------
    text : str
        The abstract to lowerize and stem
    stopwords: list
        A list of stopwords

    Returns
    -------
    str
        the abstract lowerized and stemmed
    """
    # Lowerize the text
    text = text.lower()

    # Remove punctuation marks
    our_punctuation = list(punctuation)
    for c in our_punctuation:
        text = text.replace(c,'')

    stemmer = PorterStemmer()
    words = text.split(' ')
    i = 0
    while i < len(words):
        # Stem the words
        words[i] = stemmer.stem(words[i])
        if len(words[i]) < 3 or words[i] in stopwords:
            # Remove words shorter than 3 characters long or appearing in the
            # list of stopwords
            words.remove(words[i])
            i -= 1
        i += 1

    # Convert list of words to a text
    return ' '.join(map(str,words))

def download_publications(pmids_l):
    """Downloads publications based on a PMIDs list

    Parameters
    ----------
    pmids_l : list
        The list of PMIDs of publications to download

    Returns
    -------
    list
        the list of all the downloaded publications at a JSON format
    """
    stepsize = 50
    all_data = []

    for i in range(0, len(pmids_l), stepsize):
        subset = pmids_l[i:i + stepsize]
        pmids = ""
        for id in subset[:-1]:
            pmids += id + ','
        pmids += subset[-1]

        response = req.urlopen(URL_DOWNLOAD.format(pmids)).read().decode('utf-8')
        response = json.loads(response)
        all_data.extend(deepcopy(response))

    return all_data

def extract_features(data, stopwords=STOPWORDS):
    """Inserts PubTator annotations inside the publications abstracts

    Parameters
    ----------
    data : list
        The list of publications to deal with
    stopwords: list
        A list of stopwords

    Returns
    -------
    list
        the list of publications with Pubtator annotations inside the abstracts
    """
    tags = set()
    docs = []
    for document in data:
        doc_data = dict()
        doc_data['pmid'] = document['sourceid']
        text = document['text']

        # Insert PubTator annotations inside abstract
        denotations = document['denotations']
        sorted_denotations = []
        for denotation in denotations:
            begin = denotation['span']['begin']
            end = denotation['span']['end']
            obj = denotation['obj']
            for c in punctuation:
                obj = obj.replace(c, '')
            tags.add(obj)
            doc_data[obj] = doc_data.get(obj,0)+1
            sorted_denotations.append([begin,end,obj])
        sorted_denotations.sort()
        sorted_denotations.reverse()
        for begin, end, obj in sorted_denotations:
            text = text[:begin] + obj + ' ' + text[end:]

        doc_data['text'] = clean_text(text, stopwords)
        docs.append(doc_data)

    return docs

def get_pmids(query="digenic", retmax=1000):
    """Gets a PMIDs list based on a particular query

    Parameters
    ----------
    query : str
        The query to retrieve the PMIDs list
    retmax: int
        The maximum number of publications that must be returned by the query

    Returns
    -------
    list
        the list of the PMIDs returned by the query
    """
    resp = req.urlopen(URL_PMIDS.format(query, retmax)).read().decode('utf-8')
    root = ET.fromstring(resp)
    pmids = root.find('IdList').getchildren()
    for i in range(len(pmids)):
        pmids[i] = pmids[i].text

    return pmids
