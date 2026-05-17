import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split


def run_logistic_regression(data, report_path, plot_path, scatter_path):
    styles = {
        "Iris-setosa":     {"color": "#0072B2", "marker": "o"},
        "Iris-versicolor": {"color": "#E69F00", "marker": "s"},
        "Iris-virginica":  {"color": "#CC79A7", "marker": "^"},
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
    with open(report_path, "w") as f:
        f.write(report + "\n")

    pad = 0.3
    x_min, x_max = X[:, 0].min() - pad, X[:, 0].max() + pad
    y_min, y_max = X[:, 1].min() - pad, X[:, 1].max() + pad
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 400),
                         np.linspace(y_min, y_max, 400))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = np.array([classes.index(z) for z in Z]).reshape(xx.shape)

    bg_colors = ["#b3d4e8", "#f5e0b3", "#ecd4e3"]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.contourf(xx, yy, Z, levels=[-0.5, 0.5, 1.5, 2.5], colors=bg_colors, alpha=0.4)
    ax.contour(xx, yy, Z, levels=[0.5, 1.5], colors="grey", linewidths=0.8, linestyles="--")
    for cls in classes:
        mask = y_test == cls
        ax.scatter(X_test[mask, 0], X_test[mask, 1], label=cls, s=70, alpha=0.9,
                   edgecolors="white", linewidths=0.5, **styles[cls])
    ax.set_xlabel("Petal length (cm)")
    ax.set_ylabel("Petal width (cm)")
    ax.set_title(f"Logistic regression decision boundary (test set, acc={acc:.2f})")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.contourf(xx, yy, Z, levels=[-0.5, 0.5, 1.5, 2.5], colors=bg_colors, alpha=0.4)
    ax.contour(xx, yy, Z, levels=[0.5, 1.5], colors="grey", linewidths=0.8, linestyles="--")
    for cls in classes:
        ax.scatter(data[cls]["petal_length"], data[cls]["petal_width"],
                   label=cls, s=60, alpha=0.75, edgecolors="white", linewidths=0.4,
                   **styles[cls])
    ax.set_xlabel("Petal length (cm)")
    ax.set_ylabel("Petal width (cm)")
    ax.set_title(f"Logistic regression decision boundary (all data, acc={acc:.2f})")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(scatter_path, dpi=150)
    plt.close(fig)

    return report
