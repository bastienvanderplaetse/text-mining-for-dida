import numpy as np
import pandas as pd

import explorer_helper as exh
import plotter as plt

class WordsDistributionClassifier:
    def __init__(self, threshold, filenames, c1, c2, foldername):
        self.threshold = threshold/100
        self.ngrams_files = filenames
        self.c1 = c1
        self.c2 = c2
        self.foldername = "wordsdistribution/" + foldername
        exh.create_directory(self.foldername)

        self.c1_grams = []
        self.c1_weight_grams = dict()
        self.c2_grams = []
        self.c2_weight_grams = dict()
        self.global_weights = dict()
        self.global_weights[self.c1] = dict()
        self.global_weights[self.c2] = dict()

        self._prepare_ngrams()

    def _prepare_ngrams(self):
        for filename in self.ngrams_files:
            df = pd.read_csv(filename, sep=',',engine='python')
            for index, row in df.iterrows():
                if abs(row['Diff']) >= self.threshold:
                    if row['Diff'] > 0: # n-gram of DIDA
                        self.c1_grams.append(row['N-gram'])
                        self.c1_weight_grams[row['N-gram']] = row['% DIDA']
                    else:
                        self.c2_grams.append(row['N-gram'])
                        self.c2_weight_grams[row['N-gram']] = row['% NotDIDA']
                    self.global_weights[self.c1][row['N-gram']] = row['% DIDA']
                    self.global_weights[self.c2][row['N-gram']] = row['% NotDIDA']

    def predict(self, documents, with_plot=False):
        classes = []
        for doc in documents:
            c1 = self._count_occurences(doc['grams'], self.c1_grams, self.c1_weight_grams, self.global_weights[self.c1])
            c2 = self._count_occurences(doc['grams'], self.c2_grams, self.c2_weight_grams, self.global_weights[self.c2])

            if with_plot:
                filename = self.foldername + '/' + doc['pmid'] + '.png'
                plt.plot(filename, doc['pmid'], c1, c2, len(self.c1_grams), len(self.c2_grams), "DIDA", "NotDIDA", "Number of n-grams")

            if c1 >= c2:
                classes.append(1)
            else:
                classes.append(0)

        return np.array(classes)

class StrictClassifier(WordsDistributionClassifier):
    def __init__(self, threshold, filenames, c1, c2):
        super(StrictClassifier, self).__init__(threshold, filenames, c1, c2, "strict")

    def _count_occurences(self, grams, grams_c, weights, global_weights):
        counter = 0
        for g in grams_c:
            has_found = False
            for n in grams:
                for gram in grams[n]:
                    l_words = list(gram)
                    words = '(' + ', '.join(l_words) + ')'
                    if words == g:
                        counter += 1
                        has_found = True
                        break
                if has_found:
                    break

        return counter

class SplitWeightedClassifier(WordsDistributionClassifier):
    def __init__(self, threshold, filenames, c1, c2):
        super(SplitWeightedClassifier, self).__init__(threshold, filenames, c1, c2, "splitweighted")

    def _count_occurences(self, grams, grams_c, weights, global_weights):
        counter = 0
        for g in grams_c:
            has_found = False
            for n in grams:
                for gram in grams[n]:
                    l_words = list(gram)
                    words = '(' + ', '.join(l_words) + ')'
                    if words == g:
                        counter += weights[g]
                        has_found = True
                        break
                if has_found:
                    break

        return counter

class WeightedClassifier(WordsDistributionClassifier):
    def __init__(self, threshold, filenames, c1, c2):
        super(WeightedClassifier, self).__init__(threshold, filenames, c1, c2, "weighted")

    def _count_occurences(self, grams, grams_c, weights, global_weights):
        counter = 0
        for g in grams_c:
            has_found = False
            for n in grams:
                for gram in grams[n]:
                    l_words = list(gram)
                    words = '(' + ', '.join(l_words) + ')'
                    if words == g:
                        counter += global_weights[g]
                        has_found = True
                        break
                if has_found:
                    break

        return counter
