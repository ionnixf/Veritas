"""Aggregate UCI Online Retail II invoice lines to calendar-day GBP totals."""

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import pandas as pd


SOURCE = "https://archive.ics.uci.edu/dataset/502/online+retail+ii"
ARCHIVE_SHA256 = "572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb"
SHEETS = ("Year 2009-2010", "Year 2010-2011")
HANDOVER = pd.Timestamp("2010-12-01")


def aggregate(archive: Path, output: Path) -> None:
    with archive.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != ARCHIVE_SHA256:
        raise ValueError("Unexpected UCI archive checksum. Verify the source before using it.")
    parts = []
    audit = []
    with ZipFile(archive) as package, package.open("online_retail_II.xlsx") as workbook:
        with pd.ExcelFile(workbook, engine="calamine") as excel:
            for i, sheet in enumerate(SHEETS):
                lines = pd.read_excel(excel, sheet_name=sheet,
                                      usecols=["Invoice", "Quantity", "InvoiceDate", "Price"])
                date = pd.to_datetime(lines["InvoiceDate"], errors="raise").dt.normalize()
                # The annual worksheets overlap. Give each calendar day one owner.
                owned = date.lt(HANDOVER) if i == 0 else date.ge(HANDOVER)
                if date.isna().any() or date[owned].empty:
                    raise ValueError(f"Invalid date coverage in {sheet}")
                lines = lines.loc[owned]
                is_credit = lines["Invoice"].astype(str).str.upper().str.startswith("C")
                qty, price = lines["Quantity"], lines["Price"]
                value = qty * price
                daily = pd.DataFrame({
                    "date": date.loc[owned],
                    "cancel_gbp": (-value).where(is_credit & qty.lt(0) & price.gt(0), 0),
                    "sales_gbp": value.where(~is_credit & qty.gt(0) & price.gt(0), 0),
                    "lines": 1,
                }).groupby("date").sum()
                parts.append(daily)
                audit.append({"sheet": sheet, "input_rows": len(date),
                              "rows_on_owned_dates": len(lines)})
    days = pd.concat(parts, verify_integrity=True).sort_index()
    days = days.reindex(pd.date_range(days.index.min(), days.index.max(), freq="D"), fill_value=0)
    days = days.iloc[1:-1].rename_axis("date")  # Discard possibly partial boundary dates.
    output.mkdir(parents=True, exist_ok=True)
    days.to_csv(output / "daily.csv", float_format="%.2f")
    manifest = {"dataset": SOURCE, "license": "CC BY 4.0", "author": "Daqing Chen",
                "sha256": digest, "sheets": audit, "handover": str(HANDOVER.date()),
                "first_full_day": str(days.index[0].date()), "last_full_day": str(days.index[-1].date()),
                "calendar_days": len(days), "days_with_no_recorded_lines": int(days.lines.eq(0).sum())}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    aggregate(args.archive, args.output)
