import math

import numpy as np

from copy import deepcopy

import display

global clusters, Pcluster, Pc_cluster, agg_info, Pcw, Pw, backup

def initialize_clusters():
    global clusters, Pcluster, Pc_cluster
    clusters = []
    Pcluster = []
    n_words = len(Pw)
    n_categories = len(Pcw)
    Pc_cluster = np.zeros((n_categories, n_words))

    for i in range(n_words):
        clusters.append([i])
        Pcluster.append(Pw[i])

        for j in range(n_categories):
            Pc_cluster[j,i] = Pcw[j,i] / Pcluster[i]

def js_divergence(cluster_i, cluster_j, n_categories):
    p_cluster_star = Pcluster[cluster_i] + Pcluster[cluster_j]
    pi_i = Pcluster[cluster_i] / p_cluster_star
    pi_j = Pcluster[cluster_j] / p_cluster_star

    dkl_i = 0
    dkl_j = 0
    for c in range(n_categories):
        p = pi_i * Pc_cluster[c, cluster_i] + pi_j * Pc_cluster[c, cluster_j]
        dkl_i += (Pc_cluster[c, cluster_i] * math.log10(Pc_cluster[c, cluster_i] / p))
        dkl_j += (Pc_cluster[c, cluster_j] * math.log10(Pc_cluster[c, cluster_j] / p))

    js_d = pi_i * dkl_i + pi_j * dkl_j

    return js_d

def agglomerative_information():
    global agg_info

    n_words = len(Pw)
    n_categories = len(Pcw)
    agg_info = np.zeros((n_words, n_words)) + np.Inf
    for i in range(n_words):
        s = "Agglomerative information for word {0} on {1}".format(i+1, n_words)
        print (s, end="\r")
        # print("Agglomerative information for word {0} / {1}".format(i+1, n_words))
        for j in range(i+1, n_words):
            js_d = js_divergence(i,j, n_categories)
            agg_info[i,j] = (Pcluster[i] + Pcluster[j]) * js_d
    print(s)

def initialization():
    print("Starting clusters initialization")
    initialize_clusters()
    display.display_ok("Clusters initialization done")
    print("Processing agglomerative information")
    agglomerative_information()
    display.display_ok("Processing agglomerative information done")

def backup_clusters(n_clusters):
    cleaned_clusters = [deepcopy(c) for c in clusters if len(c) != 0]
    backup[n_clusters] = cleaned_clusters

def loop(M):
    backup_clusters(M)
    n_categories = len(Pcw)
    print("Starting IB method loop")
    for m in range(M-1, 0, -1):
        s = "Running iteration {0} on {1}".format(M-m, M-1)
        print (s, end="\r")
        # print("Iteration {0} / {1}".format(M-m, M-1))
        # Find minimum cost
        cluster_i, cluster_j = np.argwhere(agg_info == agg_info.min())[0]

        # Merge clusters
        p_w = Pcluster[cluster_i] + Pcluster[cluster_j]
        pi_i = Pcluster[cluster_i] / p_w
        pi_j = Pcluster[cluster_j] / p_w
        pc_w = []
        for c in range(n_categories):
            temp = pi_i * Pc_cluster[c, cluster_i] + pi_j * Pc_cluster[c, cluster_j]
            pc_w.append(temp)

        clusters[cluster_i].extend(clusters[cluster_j])
        Pcluster[cluster_i] = p_w
        for c in range(n_categories):
            Pc_cluster[c, cluster_i] = pc_w[c]

        # Remove cluster j
        clusters[cluster_j].clear()

        for j in range(cluster_j+1, M):
            agg_info[cluster_j][j] = np.Inf
        for i in range(cluster_j):
            agg_info[i][cluster_j] = np.Inf

        # Update cost
        for j in range(cluster_i+1, M):
            if agg_info[cluster_i,j] != np.Inf:
                # update agg_info[cluster_i][j]
                js_d = js_divergence(cluster_i,j, n_categories)
                agg_info[cluster_i,j] = (Pcluster[cluster_i] + Pcluster[j]) * js_d
        for i in range(cluster_i):
            if agg_info[i][cluster_i] != np.Inf:
                # update agg_info[i][cluster_i]
                js_d = js_divergence(i, cluster_i, n_categories)
                agg_info[i, cluster_i] = (Pcluster[i] + Pcluster[cluster_i]) * js_d

        backup_clusters(m)
    print(s)
    display.display_ok("IB method loop done")

def cluster(p_cw, p_w):
    global Pcw, Pw, backup
    Pcw = p_cw
    Pw = p_w
    words = [w for w in Pw.items()]
    words.sort()
    Pw = [v for k,v in words]
    initialization()
    backup = dict()
    loop(len(Pw))
    return backup
