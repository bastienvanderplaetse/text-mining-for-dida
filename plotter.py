import matplotlib.pyplot as plt
import numpy as np

def autolabel(rects, ax):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%.3f'%h,
                ha="center", va="bottom")

def plot(filename, title, score_c1, score_c2, n_c1, n_c2, label_c1, label_c2, y_label):
    x = [label_c1, label_c2]
    ind=[0,0.5]
    width = 0.25
    fig = plt.figure()
    ax = fig.add_subplot(111)
    yvals = [score_c1, score_c2]
    rects1 = ax.bar(ind, yvals, width, color='b')
    plt.title(title)
    ax.set_ylabel(y_label)
    ax.set_xticks(ind)
    ax.set_xticklabels( (label_c1, label_c2) )

    autolabel(rects1, ax)

    plt.savefig(filename)
    plt.close(fig)
    plt.clf()

def plot_confusion_matrix(results, n_c1, n_c2, prefix, key, s_key, directory, step=2):
    lines = [results['tp'], results['fp'], results['tn'], results['fn']]
    labels = ["True Positive", "False Positive", "True Negative", "False Negative"]
    plot_lines(results[key], lines, labels, directory+"/"+prefix+"confusion_matrix.png", s_key, "Number of samples", step=step)

    lines = [
        np.array(results['tp'])/n_c1,
        np.array(results['fp'])/n_c2,
        np.array(results['tn'])/n_c2,
        np.array(results['fn'])/n_c1
    ]

    plot_lines(results[key], lines, labels, directory+"/"+prefix+"normalized_confusion_matrix.png", s_key, "Number of samples", step=step)

def plot_dots(lists, colors, threshold, threshold_color, xlabel, ylabel, figname, filename):
    for index, l in enumerate(lists):
        if len(l) > 0:
            plt.scatter(*zip(*l), s=10, c=colors[index])

    plt.axhline(y=threshold, color=threshold_color, linestyle='-')

    plt.title(figname)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.savefig(filename)

    plt.clf()

def plot_lines(threshold_l, lines, labels, filename, label_x, label_y, has_legend=True, step=2):
    fig, ax = plt.subplots()

    for index, line in enumerate(lines):
        ax.plot(threshold_l, line, label=labels[index])


    ax.set_ylabel(label_y)
    ax.set_xlabel(label_x)

    plt.xticks(np.arange(min(threshold_l)-1, max(threshold_l)+1, step))

    if has_legend:
        lgd = ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches="tight")
    else:
        plt.savefig(filename)
    plt.close(fig)
    plt.clf()
