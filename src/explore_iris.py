import csv
from collections import defaultdict
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split

DATA_PATH = "data/iris.data"
OUTPUT_PATH = "outputs/iris_stats.txt"
CHART_PATH = "outputs/iris_means.png"
SCATTER_PATH = "outputs/iris_scatter.png"
LR_PLOT_PATH = "outputs/iris_logreg.png"
LR_REPORT_PATH = "outputs/iris_logreg.txt"
COLUMNS = ["sepal_length", "sepal_width", "petal_length", "petal_width"]


def load_data(path):
    data = defaultdict(lambda: defaultdict(list))
    with open(path) as f:
        for row in csv.reader(f):
            if len(row) != 5:
                continue
            *values, cls = row
            for col, val in zip(COLUMNS, values):
                data[cls][col].append(float(val))
    return data


def mean(xs):
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def sd(xs):
    m = mean(xs)
    return sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def format_stats(data):
    stat_fns = [("mean", mean), ("median", median), ("sd", sd)]
    col_w = 16
    lines = []

    for cls, cols in sorted(data.items()):
        lines.append(f"\n{'=' * 60}")
        lines.append(f"  {cls}")
        lines.append(f"{'=' * 60}")
        header = f"{'variable':<20}" + "".join(f"{label:>{col_w}}" for label, _ in stat_fns)
        lines.append(header)
        lines.append("-" * 60)
        for col in COLUMNS:
            xs = cols[col]
            row = f"{col:<20}" + "".join(f"{fn(xs):>{col_w}.4f}" for _, fn in stat_fns)
            lines.append(row)

    return "\n".join(lines)


def save_chart(data):
    classes = sorted(data.keys())
    n_classes = len(classes)
    n_cols = len(COLUMNS)

    means = {cls: [mean(data[cls][col]) for col in COLUMNS] for cls in classes}
    sds   = {cls: [sd(data[cls][col])   for col in COLUMNS] for cls in classes}

    x = np.arange(n_cols)
    width = 0.25
    offsets = np.linspace(-(n_classes - 1) / 2, (n_classes - 1) / 2, n_classes) * width

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#4c72b0", "#dd8452", "#55a868"]

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
    fig.savefig(CHART_PATH, dpi=150)
    plt.close(fig)


def save_scatter(data):
    styles = {
        "Iris-setosa":     {"color": "#4c72b0", "marker": "o"},
        "Iris-versicolor": {"color": "#dd8452", "marker": "s"},
        "Iris-virginica":  {"color": "#55a868", "marker": "^"},
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
    fig.savefig(SCATTER_PATH, dpi=150)
    plt.close(fig)


def run_logistic_regression(data):
    styles = {
        "Iris-setosa":     {"color": "#4c72b0", "marker": "o"},
        "Iris-versicolor": {"color": "#dd8452", "marker": "s"},
        "Iris-virginica":  {"color": "#55a868", "marker": "^"},
    }
    classes = sorted(data.keys())

    X = np.array([
        [pl, pw]
        for cls in classes
        for pl, pw in zip(data[cls]["petal_length"], data[cls]["petal_width"])
    ])
    y = np.array([cls for cls in classes for _ in data[cls]["petal_length"]])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred, labels=classes)

    lines = [
        "Logistic Regression — petal length + petal width",
        "=" * 50,
        f"Train size: {len(X_train)}   Test size: {len(X_test)}",
        f"Accuracy:   {acc:.4f}",
        "",
        "Confusion matrix (rows=actual, cols=predicted):",
        f"{'':20}" + "".join(f"{c.split('-')[1]:>14}" for c in classes),
    ]
    for cls, row in zip(classes, cm):
        lines.append(f"{cls.split('-')[1]:<20}" + "".join(f"{v:>14}" for v in row))

    report = "\n".join(lines)
    print("\n" + report)
    with open(LR_REPORT_PATH, "w") as f:
        f.write(report + "\n")

    # decision boundary plot
    pad = 0.3
    x_min, x_max = X[:, 0].min() - pad, X[:, 0].max() + pad
    y_min, y_max = X[:, 1].min() - pad, X[:, 1].max() + pad
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 400),
                         np.linspace(y_min, y_max, 400))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = np.array([classes.index(z) for z in Z]).reshape(xx.shape)

    bg_colors = ["#c6d4e8", "#f2d5c0", "#c2dfca"]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.contourf(xx, yy, Z, levels=[-0.5, 0.5, 1.5, 2.5],
                colors=bg_colors, alpha=0.4)
    ax.contour(xx, yy, Z, levels=[0.5, 1.5], colors="grey",
               linewidths=0.8, linestyles="--")

    for cls in classes:
        mask = y_test == cls
        ax.scatter(
            X_test[mask, 0], X_test[mask, 1],
            label=cls, s=70, alpha=0.9,
            edgecolors="white", linewidths=0.5,
            **styles[cls],
        )

    ax.set_xlabel("Petal length (cm)")
    ax.set_ylabel("Petal width (cm)")
    ax.set_title(f"Logistic regression decision boundary (test set, acc={acc:.2f})")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(LR_PLOT_PATH, dpi=150)
    plt.close(fig)

    # full dataset with boundaries
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.contourf(xx, yy, Z, levels=[-0.5, 0.5, 1.5, 2.5],
                colors=bg_colors, alpha=0.4)
    ax.contour(xx, yy, Z, levels=[0.5, 1.5], colors="grey",
               linewidths=0.8, linestyles="--")

    for cls in classes:
        ax.scatter(
            data[cls]["petal_length"],
            data[cls]["petal_width"],
            label=cls, s=60, alpha=0.75,
            edgecolors="white", linewidths=0.4,
            **styles[cls],
        )

    ax.set_xlabel("Petal length (cm)")
    ax.set_ylabel("Petal width (cm)")
    ax.set_title(f"Logistic regression decision boundary (all data, acc={acc:.2f})")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig("outputs/iris_scatterplot_withboundaries.png", dpi=150)
    plt.close(fig)

    return report


if __name__ == "__main__":
    data = load_data(DATA_PATH)
    output = format_stats(data)
    print(output)
    with open(OUTPUT_PATH, "w") as f:
        f.write(output + "\n")
    print(f"\nResults written to {OUTPUT_PATH}")
    save_chart(data)
    print(f"Chart written to {CHART_PATH}")
    save_scatter(data)
    print(f"Scatter written to {SCATTER_PATH}")
    run_logistic_regression(data)
    print(f"Logistic regression plot written to {LR_PLOT_PATH}")
    print(f"Logistic regression report written to {LR_REPORT_PATH}")
