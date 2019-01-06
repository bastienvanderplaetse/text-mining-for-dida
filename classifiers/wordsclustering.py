import numpy as np

from sklearn.metrics import confusion_matrix, f1_score
from pprint import pprint

class NaiveBayesCluster():
    def __init__(self, clusters, Ndw, words):
        self.clusters = clusters
        self.Ndw = Ndw
        self.words = words
        self.LABELS = [1,0]
        self._prepare()

    def evaluate(self, documents):
        predictions = []

        n_cats = len(self.Ndw)
        for doc in documents:
            cat_probas = np.ones(n_cats)
            for cat in range(n_cats):
                for cluster in doc['converted']:
                    cat_probas[cat] *= self.Pcluster_c[cluster, cat]
                cat_probas[cat] *= self.Pc[cat]
            prediction = np.argwhere(cat_probas == cat_probas.max())
            # print(prediction)
            prediction = prediction[0]
            predictions.append(int(prediction))
        return predictions

    def score(self, y_true, y_pred):
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        score = f1_score(y_true, y_pred)
        return {
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "score": score
        }


    def _prepare(self):
        n_cats = len(self.Ndw)
        n_clusters = len(self.clusters)

        self.Nc_cluster = np.zeros((n_cats, n_clusters))
        self._fill_Nc_cluster(n_clusters)
        self.Nc_cluster = self.Nc_cluster + 0.5
        self.total_ncw = [sum(x) for x in self.Nc_cluster]

        self.Pc = self._fill_Pc()

        self.Pcluster_c = np.zeros((n_clusters, n_cats))
        self._fill_Pcluster_c(n_clusters, n_cats)

    def _fill_Pcluster_c(self, n_clusters, n_cats):
        for cluster in range(n_clusters):
            for cat in range(n_cats):
                self.Pcluster_c[cluster, cat] = self.Nc_cluster[cat, cluster] / self.total_ncw[cat]

    def _fill_Pc(self):
        pc = []
        for cat in self.Ndw:
            pc.append(len(self.Ndw[cat]))
        return np.array(pc)/sum(np.array(pc))

    def _fill_Nc_cluster(self, n_clusters):
        id_cat = -1
        for cat in self.Ndw:
            id_cat += 1
            for cluster in range(n_clusters):
                total = 0
                for doc in self.Ndw[cat]:
                    for w in self.clusters[cluster]:
                        word = self.words[w]
                        total += self._from_Ndw(cat, doc, word)
                self.Nc_cluster[id_cat, cluster] = total

    def _from_Ndw(self, cat, doc, word):
        if word in self.Ndw[cat][doc]:
            return self.Ndw[cat][doc][word]
        return 0
