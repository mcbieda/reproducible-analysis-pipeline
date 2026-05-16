from math import sqrt

from iris.data import COLUMNS


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
