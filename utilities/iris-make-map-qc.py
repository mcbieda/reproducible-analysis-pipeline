"""
iris-make-map-qc.py — generates a simulated map file and QC file from iris-combined.csv.

Outputs:
  data_derived/iris-mapids.csv  — sampleID -> FINAL_ID (162 - 6 dropped + 8 simulated = 164 rows)
  data_derived/iris-qc.csv      — FINAL_ID + QC_CALL (164 - 4 dropped + 6 new = 166 rows)
"""

import csv
import os
import random

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED_DIR = os.path.join(REPO_ROOT, "data_derived")

COMBINED_CSV = os.path.join(DERIVED_DIR, "iris-combined.csv")
MAPIDS_CSV   = os.path.join(DERIVED_DIR, "iris-mapids.csv")
QC_CSV       = os.path.join(DERIVED_DIR, "iris-qc.csv")

RANDOM_SEED = 42


def make_final_id(used):
    """Return a unique FINAL_ID in the format FINAL-NNN (001-899)."""
    while True:
        n = random.randint(1, 899)
        fid = f"FINAL-{n:03d}"
        if fid not in used:
            used.add(fid)
            return fid


def make_sample_id(used):
    """Return a unique sampleID in the format X-NNNN (A-F, 0001-8999)."""
    while True:
        letter = random.choice("ABCDEF")
        n = random.randint(1, 8999)
        sid = f"{letter}-{n:04d}"
        if sid not in used:
            used.add(sid)
            return sid


def load_sample_ids():
    with open(COMBINED_CSV, newline="") as f:
        reader = csv.DictReader(f)
        return [row["sampleID"] for row in reader]


def write_mapids(sample_ids):
    kept = list(sample_ids)
    drop_indices = set(random.sample(range(len(kept)), 6))
    kept = [sid for i, sid in enumerate(kept) if i not in drop_indices]

    used_finals = set()
    used_samples = set(sample_ids)  # track all original IDs to avoid collisions

    rows = [{"sampleID": sid, "FINAL_ID": make_final_id(used_finals)} for sid in kept]

    # 8 extra rows with simulated sampleID and FINAL_ID
    for _ in range(8):
        rows.append({
            "sampleID": make_sample_id(used_samples),
            "FINAL_ID": make_final_id(used_finals),
        })

    with open(MAPIDS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sampleID", "FINAL_ID"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {MAPIDS_CSV}  ({len(rows)} rows)")
    return [row["FINAL_ID"] for row in rows], used_finals


def write_qc(map_finals, used_finals):
    kept = list(map_finals)
    drop_indices = set(random.sample(range(len(kept)), 4))
    kept = [fid for i, fid in enumerate(kept) if i not in drop_indices]

    # 6 new FINAL_IDs not in iris-mapids.csv
    new_finals = [make_final_id(used_finals) for _ in range(6)]

    all_finals = kept + new_finals
    random.shuffle(all_finals)

    with open(QC_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["FINAL_ID", "QC_CALL"])
        writer.writeheader()
        for fid in all_finals:
            qc = "FAIL" if random.random() < 0.10 else "PASS"
            writer.writerow({"FINAL_ID": fid, "QC_CALL": qc})

    print(f"Wrote {QC_CSV}  ({len(all_finals)} rows)")


def main():
    random.seed(RANDOM_SEED)
    sample_ids = load_sample_ids()
    map_finals, used_finals = write_mapids(sample_ids)
    write_qc(map_finals, used_finals)


if __name__ == "__main__":
    main()
