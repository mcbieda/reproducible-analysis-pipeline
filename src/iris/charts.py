import numpy as np
import matplotlib.pyplot as plt

from iris.data import COLUMNS
from iris.stats import mean, sd


def save_chart(data, path):
    classes = sorted(data.keys())
    n_classes = len(classes)
    n_cols = len(COLUMNS)

    means = {cls: [mean(data[cls][col]) for col in COLUMNS] for cls in classes}
    sds   = {cls: [sd(data[cls][col])   for col in COLUMNS] for cls in classes}

    x = np.arange(n_cols)
    width = 0.25
    offsets = np.linspace(-(n_classes - 1) / 2, (n_classes - 1) / 2, n_classes) * width

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#0072B2", "#E69F00", "#CC79A7"]

    for i, cls in enumerate(classes):
        ax.bar(
            x + offsets[i], means[cls], width,
            yerr=sds[cls], capsize=4,
            label=cls, color=colors[i], alpha=0.85,
            error_kw={"elinewidth": 1.2, "ecolor": "black"},
        )

    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("_", "\n") for c in COLUMNS])
    ax.set_ylabel("cm")
    ax.set_title("Iris: mean ± SD by measurement and class")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_scatter(data, path):
    styles = {
        "Iris-setosa":     {"color": "#0072B2", "marker": "o"},
        "Iris-versicolor": {"color": "#E69F00", "marker": "s"},
        "Iris-virginica":  {"color": "#CC79A7", "marker": "^"},
    }

    fig, ax = plt.subplots(figsize=(8, 6))

    for cls in sorted(data.keys()):
        ax.scatter(
            data[cls]["petal_length"],
            data[cls]["petal_width"],
            label=cls,
            alpha=0.75,
            edgecolors="white",
            linewidths=0.4,
            s=60,
            **styles[cls],
        )

    ax.set_xlabel("Petal length (cm)")
    ax.set_ylabel("Petal width (cm)")
    ax.set_title("Iris: petal width vs petal length")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
