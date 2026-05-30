"""
iris-merge-and-qc.py — merges iris-combined.csv with map/QC files via inner joins.

Outputs:
  data_derived/iris-combined-mapids.csv               — iris-combined inner-joined with iris-mapids on sampleID
  data_derived/iris-combined-mapids-summary.json      — join diagnostics
  data_derived/iris-combined-mapids-qc.csv            — above inner-joined with iris-qc on FINAL_ID
  data_derived/iris-combined-mapids-qc-summary.json   — join diagnostics
"""

import csv
import json
import os
import random

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED_DIR = os.path.join(REPO_ROOT, "data_derived")
OUTPUTS_DIR = os.path.join(REPO_ROOT, "outputs")

COMBINED_CSV       = os.path.join(DERIVED_DIR, "iris-combined.csv")
MAPIDS_CSV         = os.path.join(DERIVED_DIR, "iris-mapids.csv")
QC_CSV             = os.path.join(DERIVED_DIR, "iris-qc.csv")

COMBINED_MAPIDS_CSV     = os.path.join(DERIVED_DIR, "iris-combined-mapids.csv")
COMBINED_MAPIDS_SUMMARY = os.path.join(OUTPUTS_DIR, "iris-combined-mapids-summary.json")
COMBINED_QC_CSV         = os.path.join(DERIVED_DIR, "iris-combined-mapids-qc.csv")
COMBINED_QC_SUMMARY     = os.path.join(OUTPUTS_DIR, "iris-combined-mapids-qc-summary.json")

RANDOM_SEED = 42


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def merge_combined_mapids():
    combined_rows = read_csv(COMBINED_CSV)
    mapids_rows   = read_csv(MAPIDS_CSV)

    # Build lookup: sampleID -> FINAL_ID from mapids
    map_lookup = {row["sampleID"]: row["FINAL_ID"] for row in mapids_rows}
    combined_ids = {row["sampleID"] for row in combined_rows}
    mapids_ids   = set(map_lookup.keys())

    only_in_combined = sorted(combined_ids - mapids_ids)
    only_in_mapids   = sorted(mapids_ids - combined_ids)
    n_common         = len(combined_ids & mapids_ids)

    # Inner join: keep rows in combined that have a matching sampleID in mapids
    fieldnames = list(combined_rows[0].keys()) + ["FINAL_ID"]
    joined = []
    for row in combined_rows:
        if row["sampleID"] in map_lookup:
            joined.append({**row, "FINAL_ID": map_lookup[row["sampleID"]]})

    with open(COMBINED_MAPIDS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(joined)

    summary = {
        "n_in_combined_only": len(only_in_combined),
        "ids_in_combined_only": only_in_combined,
        "n_in_mapids_only": len(only_in_mapids),
        "ids_in_mapids_only": only_in_mapids,
        "n_in_common": n_common,
    }
    with open(COMBINED_MAPIDS_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Wrote {COMBINED_MAPIDS_CSV}  ({len(joined)} rows)")
    print(f"Wrote {COMBINED_MAPIDS_SUMMARY}")
    return joined


def merge_with_qc(combined_mapids_rows):
    qc_rows = read_csv(QC_CSV)

    # Build lookup: FINAL_ID -> QC_CALL
    qc_lookup = {row["FINAL_ID"]: row["QC_CALL"] for row in qc_rows}
    mapids_finals = {row["FINAL_ID"] for row in combined_mapids_rows}
    qc_finals     = set(qc_lookup.keys())

    only_in_mapids = sorted(mapids_finals - qc_finals)
    only_in_qc     = sorted(qc_finals - mapids_finals)
    n_common       = len(mapids_finals & qc_finals)

    fieldnames = list(combined_mapids_rows[0].keys()) + ["QC_CALL"]
    joined = []
    for row in combined_mapids_rows:
        if row["FINAL_ID"] in qc_lookup:
            joined.append({**row, "QC_CALL": qc_lookup[row["FINAL_ID"]]})

    with open(COMBINED_QC_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(joined)

    summary = {
        "n_in_combined_mapids_only": len(only_in_mapids),
        "ids_in_combined_mapids_only": only_in_mapids,
        "n_in_qc_only": len(only_in_qc),
        "ids_in_qc_only": only_in_qc,
        "n_in_common": n_common,
    }
    with open(COMBINED_QC_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Wrote {COMBINED_QC_CSV}  ({len(joined)} rows)")
    print(f"Wrote {COMBINED_QC_SUMMARY}")


def main():
    random.seed(RANDOM_SEED)
    combined_mapids_rows = merge_combined_mapids()
    merge_with_qc(combined_mapids_rows)


if __name__ == "__main__":
    main()
