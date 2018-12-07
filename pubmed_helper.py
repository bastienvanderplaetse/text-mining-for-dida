from string import punctuation
from nltk.stem import PorterStemmer

import explorer_helper as exh

STOPWORDS = exh.load_json('config/stopwords.json')["stopwords"]

def _clean_text(text):
    text = text.lower()

    our_punctuation = list(punctuation)
    #ourPunctuation.remove("-")
    for c in our_punctuation:
        text = text.replace(c,"")
    stemmer = PorterStemmer()
    #remove words shorter than 3 characters long or appearing in the list of stopwords of pubmed
    words = text.split(' ')
    i = 0
    while i < len(words):
        words[i] = stemmer.stem(words[i])
        if len(words[i]) < 3 or words[i] in STOPWORDS:
            words.remove(words[i])
            i -= 1
        i += 1

    return ' '.join(map(str,words)) # converting list of words to a text

def extract_features(data):
    tags = set()
    docs = []
    total_text = []
    for document in data:
        doc_data = dict()
        doc_data["pmid"] = document["sourceid"]
        text = document["text"]
        denotations = document["denotations"]
        sorted_denotations = []
        for denotation in denotations:
            #print(denot)
            begin = denotation["span"]["begin"]
            end = denotation["span"]["end"]
            obj = denotation["obj"]
            for c in punctuation:
                obj = obj.replace(c, "")
            tags.add(obj)
            doc_data[obj] = doc_data.get(obj,0)+1

            sorted_denotations.append([begin,end,obj])

        sorted_denotations.sort()
        sorted_denotations.reverse()
        for begin, end, obj in sorted_denotations:
            text = text[:begin] + obj + " " + text[end:]
        doc_data["text"] = _clean_text(text)
        total_text.append(doc_data["text"])
        docs.append(doc_data)

    return docs, total_text
