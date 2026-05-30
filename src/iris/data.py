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


def load_data_csv(path):
    """Load a CSV with headers (iris-combined-mapids-qc format), keeping only QC_CALL==PASS rows."""
    data = defaultdict(lambda: defaultdict(list))
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("QC_CALL", "PASS") != "PASS":
                continue
            cls = row["class"]
            for col in COLUMNS:
                data[cls][col].append(float(row[col]))
    return data
