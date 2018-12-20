import matplotlib.pyplot as plt

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
