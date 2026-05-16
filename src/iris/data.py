import csv
from collections import defaultdict

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
