# Theoretical Methods

This file documents the statistical and machine learning methods used in this project, with a focus on theory rather than implementation.

---

## Logistic Regression for Multiclass Classification

### What this project uses

The logistic regression here is **multinomial (softmax) logistic regression** — a single, jointly estimated model that assigns a probability to each of the three Iris classes simultaneously. Given a feature vector **x**, the model computes a score $z_k = \mathbf{w}_k \cdot \mathbf{x} + b_k$ for each class $k$, then passes all scores through the softmax function:

$$P(y = k \mid \mathbf{x}) = \frac{e^{z_k}}{\sum_{j} e^{z_j}}$$

This guarantees that probabilities across all classes are non-negative and sum to exactly 1. The model parameters for all classes are estimated together by maximizing the multinomial log-likelihood (equivalently, minimizing cross-entropy loss) over the training set.

---

### How this differs from One-vs-Rest (OvR)

One-vs-Rest (also called One-vs-All) is a different strategy for extending binary logistic regression to multiple classes. Instead of one joint model, OvR trains **K separate binary classifiers** — one per class — where each classifier learns to distinguish "class k" from "all other classes combined."

At prediction time, each binary classifier produces its own probability estimate for its class, and the class with the highest score wins.

Key differences:

| | Multinomial (softmax) | One-vs-Rest |
|---|---|---|
| Number of models | 1 | K (one per class) |
| Probabilities sum to 1 | Yes, by construction | Not guaranteed |
| Classes estimated | Jointly | Independently |
| Training set balance | Natural | Each binary problem sees class imbalance (1 class vs. K-1) |
| Decision boundaries | Consistent across all classes | Each boundary set independently |

### Why the distinction matters for Iris

The Iris dataset has three classes, two of which (versicolor and virginica) are **not linearly separable** from each other. With OvR, the versicolor and virginica binary classifiers are each trained against a pooled "not this class" set, which can produce inconsistent or overlapping decision regions in the feature space. The multinomial model avoids this by learning a single coherent partition of the feature space across all three classes simultaneously.

Softmax logistic regression is generally preferred when classes are mutually exclusive (each sample belongs to exactly one class), which is the case here.
