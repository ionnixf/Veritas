"""Replay a historical forecast with an optional reveal of the seven-day outcome."""

import argparse
import csv
from datetime import date, timedelta
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("as_of", help="first forecast day, YYYY-MM-DD")
    parser.add_argument("--reveal", action="store_true")
    parser.add_argument("--file", type=Path, default=Path("artifacts/validation_replay.csv"))
    args = parser.parse_args()
    with args.file.open(newline="") as stream:
        rows = {row["as_of"]: row for row in csv.DictReader(stream)}
    if not rows:
        parser.error(f"{args.file} contains no dates")
    if args.as_of not in rows:
        parser.error(f"Date outside replay. Choose a day from {min(rows)} to {max(rows)}.")
    row = rows[args.as_of]
    end = date.fromisoformat(args.as_of) + timedelta(days=6)
    print(f"Seven-day reserve for recorded cancellations | {args.as_of} through {end}")
    for label, column in [("Previous seven days", "last_week"), ("Fixed training Q80", "training_q80"),
                          ("Eight-week Q80 rule", "historical_q80"),
                          ("Linear Q80 estimate", "linear_q80"),
                          ("Model Q80 reserve", "model_q80")]:
        print(f"{label:24} £{float(row[column]):,.2f}")
    if args.reveal:
        actual, reserve = float(row["actual_gbp"]), float(row["model_q80"])
        print(f"Recorded cancellations   £{actual:,.2f}")
        print(f"Reserve shortfall        £{max(actual - reserve, 0):,.2f}")
        print(f"Unused model reserve     £{max(reserve - actual, 0):,.2f}")


if __name__ == "__main__":
    main()
