from pprint import pprint

def init(docs, words):
    return _replace_words(docs, words)

# def convert_all(docs, clusters, words, method='s'):
def convert_all(docs, clusters, method='s'):
    # converted_docs = _replace_words(docs, words)
    if method == 's':
        # _convert(converted_docs, clusters)
        _convert(docs, clusters)
    elif method == 'd':
        # _convert(converted_docs, clusters, allow_doublons=True)
        _convert(docs, clusters, allow_doublons=True)
    # return converted_docs
    return docs

def _replace_words(all_docs, words):
    converted = []
    for docs in all_docs:
        for doc in docs:
            temp_doc = dict()
            temp_doc['pmid'] = doc['pmid']
            temp_doc['text'] = []
            for word in doc['text'].split(' '):
                id_word = _find_id_word(word, words)
                temp_doc['text'].append(id_word)
            converted.append(temp_doc)
    return converted

def _find_id_word(word, words):
    for id, w in enumerate(words):
        if w == word:
            return id

def _convert(docs, clusters, allow_doublons=False):
    for doc in docs:
        doc['converted'] = []
        for word in doc['text']:
            cluster = _find_cluster(word, clusters)
            if allow_doublons or not cluster in doc['converted']:
                doc['converted'].append(cluster)

def _find_cluster(word, clusters):
    for id, cluster in enumerate(clusters):
        if word in cluster:
            return id
