import sys
import argparse

from copy import deepcopy
from nltk import ngrams

import explorer_helper as exh
import pubmed_helper as pbmdh

CONFIG = None
DIRECTORY = "topwords"
TOPWORDS_FILENAME = DIRECTORY + "/topwords_iter{0}.json"
STOPWORDS_FILENAME = DIRECTORY + "/stopwords_iter{0}.json"
STRICT_TOPWORDS_FILENAME = DIRECTORY + '/strict_top_{0}_words.json'
TOPGRAMS_FILENAME = DIRECTORY + "/{0}grams_topwords_iter{1}.json"
STOPGRAMS_FILENAME = DIRECTORY + "/{0}grams_stopwords_iter{1}.json"
STRICT_TOPGRAMS_FILENAME = DIRECTORY + '/strict_top_{0}_{1}grams.json'
FILENAME_TEMPLATE = "documents/{0}-back.json"

def check_args(argv):
    parser = argparse.ArgumentParser(description="Searches the top words in a\
        publications file")
    parser.add_argument('CONFIG', type=str, help="the name of the configuration file (without extension)")
    args = parser.parse_args()

    return args

def find_top_words(dida_data, notdida_data, initial_stopwords):
    cross_top_words(deepcopy(dida_data), deepcopy(notdida_data), deepcopy(initial_stopwords))
    strict_top_words(deepcopy(dida_data), deepcopy(notdida_data), deepcopy(initial_stopwords))

def cross_top_words(dida_data, notdida_data, initial_stopwords):
    iteration = 0
    CTW = [1] # common top words
    topwords_dict = dict()
    stopwords_dict = dict()

    while CTW:
        CTW.clear()
        dida_docs, _ = pbmdh.extract_features(deepcopy(dida_data), initial_stopwords)
        notdida_docs, _ = pbmdh.extract_features(deepcopy(notdida_data), initial_stopwords)
        top_dida = top_words(dida_docs)
        top_notdida = top_words(notdida_docs)
        find_common_words(top_dida, top_notdida, CTW)
        topwords_dict["iteration"] = iteration
        topwords_dict["CTW"] = CTW
        topwords_dict["dida"] = top_dida
        topwords_dict["notdida"] = top_notdida
        exh.write_json(topwords_dict, TOPWORDS_FILENAME.format(iteration))

        if CTW:
            initial_stopwords.extend(CTW)
            stopwords_dict["stopwords"] = initial_stopwords
            iteration += 1
            exh.write_json(stopwords_dict, STOPWORDS_FILENAME.format(iteration))

def strict_top_words(dida_data, notdida_data, initial_stopwords):
    strict_top = dict()
    max_top = CONFIG["NTOPWORDS"]

    dida_docs, dida_text = pbmdh.extract_features(deepcopy(dida_data), initial_stopwords)
    notdida_docs, notdida_text = pbmdh.extract_features(deepcopy(notdida_data), initial_stopwords)

    top_dida = top_words(dida_docs, split=False)
    top_notdida = top_words(notdida_docs, split=False)

    top_dida_l = []
    top_notdida_l = []

    find_unique(top_dida, top_notdida, top_dida_l)
    find_unique(top_notdida, top_dida, top_notdida_l)

    if (len(top_dida_l) > max_top):
        top_dida_l = top_dida_l[len(top_dida_l)-max_top:]
    if (len(top_notdida_l) > max_top):
        top_notdida_l = top_notdida_l[len(top_notdida_l)-max_top:]

    strict_top["didatop"] = top_dida_l
    strict_top["notdidatop"] = top_notdida_l

    exh.write_json(strict_top, STRICT_TOPWORDS_FILENAME.format(max_top))

def top_words(docs, split=True):
    top = dict()
    max_top = CONFIG["NTOPWORDS"]
    for doc in docs:
        text = doc['text'].split(" ")
        for word in text:
            top[word] = top.get(word, 0) + 1
    top = sorted(top.items(), key=lambda kv: kv[1])

    if len(top) > max_top and split:
        top = top[len(top)-max_top:]

    return top

def find_common_words(set1, set2, common):
    for w1 in set1:
        for w2 in set2:
            if w1[0] == w2[0]:
                common.append(w1[0])
                break

def find_unique(set1, set2, uniques):
    for w1 in set1:
        found = False
        for w2 in set2:
            if w1[0] == w2[0]:
                found = True
                break
        if not found:
            uniques.append(w1)

def find_top_ngrams(n, dida_data, notdida_data, initial_stopwords):
    dida_docs, _ = pbmdh.extract_features(deepcopy(dida_data), initial_stopwords)
    notdida_docs, _ = pbmdh.extract_features(deepcopy(notdida_data), initial_stopwords)

    dida_grams = dict()
    count_ngrams(n, dida_docs, dida_grams)
    dida_grams = sorted(dida_grams.items(), key=lambda kv: kv[1])

    notdida_grams = dict()
    count_ngrams(n, notdida_docs, notdida_grams)
    notdida_grams = sorted(notdida_grams.items(), key=lambda kv: kv[1])

    cross_ngrams(n, deepcopy(dida_grams), deepcopy(notdida_grams))
    strict_ngrams(n, deepcopy(dida_grams), deepcopy(notdida_grams))

def cross_ngrams(n, set1, set2):
    iteration = 0
    CTG = [1] # common top grams
    blacklist = []
    topgrams_dict = dict()
    blacklist_dict = dict()
    max_top = CONFIG["NTOPWORDS"]

    while CTG:
        CTG.clear()

        grams1 = deepcopy(set1)
        grams2 = deepcopy(set2)
        if len(grams1) > max_top :
            grams1 = grams1[len(grams1)-max_top:]
        if len(grams2) > max_top :
            grams2 = grams2[len(grams2)-max_top:]
        for gram1 in grams1:
            for gram2 in grams2:
                if gram1[0] == gram2[0] and not gram1[0] in blacklist :
                    CTG.append(gram1[0])
                    break
        topgrams_dict["iteration"] = iteration
        topgrams_dict["CTG"] = CTG
        topgrams_dict["dida"] = grams1
        topgrams_dict["notdida"] = grams2
        exh.write_json(topgrams_dict, TOPGRAMS_FILENAME.format(n, iteration))

        if CTG :
            blacklist.extend(CTG)
            for word in CTG :
                for gram in set1:
                    if gram[0] == word:
                        set1.remove(gram)
                        break
                for gram in set2:
                    if gram[0] == word:
                        set2.remove(gram)
                        break
            blacklist_dict["stopgrams"] = blacklist
            iteration += 1
            exh.write_json(blacklist_dict, STOPGRAMS_FILENAME.format(n, iteration))

def strict_ngrams(n, dida_grams, notdida_grams):
    didatop = []
    notdidatop = []
    strict_top = dict()
    max_top = CONFIG["NTOPWORDS"]

    find_unique(dida_grams, notdida_grams, didatop)
    find_unique(notdida_grams, dida_grams, notdidatop)

    if (len(didatop) > max_top):
        didatop = didatop[len(didatop)-max_top:]
    if (len(notdidatop) > max_top):
        notdidatop = notdidatop[len(notdidatop)-max_top:]

    strict_top["didatop"] = didatop
    strict_top["notdidatop"] = notdidatop

    exh.write_json(strict_top, STRICT_TOPGRAMS_FILENAME.format(max_top, n))

def count_ngrams(n, docs, grams_dict):
    for doc in docs:
        grams = ngrams(doc["text"].split(), n)
        for gram in grams:
            grams_dict[gram] = grams_dict.get(gram, 0) + 1

def extract_ngrams(n, dida_data, notdida_data, initial_stopwords):
    if n == 1:
        find_top_words(deepcopy(dida_data), deepcopy(notdida_data), deepcopy(initial_stopwords))
    else:
        find_top_ngrams(n, deepcopy(dida_data), deepcopy(notdida_data), deepcopy(initial_stopwords))

def run(args):
    global CONFIG
    CONFIG = exh.load_json('config/{0}.json'.format(args.CONFIG))
    exh.create_directory('topwords')

    initial_stopwords = deepcopy(pbmdh.STOPWORDS)
    dida_data = exh.load_json(FILENAME_TEMPLATE.format(CONFIG["DIDA_DOCS"]))
    notdida_data = exh.load_json(FILENAME_TEMPLATE.format(CONFIG["NOTDIDA_DOCS"]))

    n = CONFIG["NGRAMS"]
    for i in range(1, n+1):
        extract_ngrams(i, deepcopy(dida_data), deepcopy(notdida_data), deepcopy(initial_stopwords))


if __name__=="__main__":
    args = check_args(sys.argv)
    run(args)
