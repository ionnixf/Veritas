"""CSV/XLSX readers and text identifier validation."""

import csv
from pathlib import Path

import polars as pl


def read_table(path, max_rows=1_000_000):
    path = Path(path)
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as stream:
            headers = next(csv.reader(stream), [])
        if not headers or any(not c.strip() for c in headers) or len(set(headers)) != len(headers):
            raise ValueError("CSV requires unique nonempty column names")
        strings = {c: pl.String for c in headers if c.endswith("_id") or c in {"sector", "country", "nameOrig", "nameDest"}}
        frame = pl.read_csv(
            path,
            infer_schema_length=None,
            n_rows=max_rows + 1,
            null_values=[""],
            schema_overrides=strings,
        )
    elif path.suffix.lower() == ".xlsx":
        from openpyxl import load_workbook

        book = load_workbook(path, read_only=True, data_only=False, keep_links=False)
        try:
            sheet = book.active
            if sheet is None:
                raise ValueError("XLSX requires an active worksheet")
            # Some exporters save stale dimensions; they must not truncate data.
            sheet.reset_dimensions()
            iterator = sheet.iter_rows()
            headers = [cell.value for cell in next(iterator, ())]
            if (
                not headers
                or any(not isinstance(c, str) or not c.strip() for c in headers)
                or len(set(headers)) != len(headers)
            ):
                raise ValueError("XLSX requires unique, nonempty string column names")
            text_columns = [i for i, name in enumerate(headers) if name.endswith("_id")]
            rows = []
            for cells in iterator:
                if any(cell.data_type == "f" for cell in cells):
                    raise ValueError("XLSX formulas are unsupported")
                row = [cell.value for cell in cells]
                if len(row) != len(headers):
                    raise ValueError("XLSX rows must match the header width")
                if any(not isinstance(row[i], str) for i in text_columns):
                    raise ValueError("XLSX identifiers must be text cells")
                if "amount" in headers and isinstance(row[headers.index("amount")], bool):
                    raise ValueError("amount must be numeric, not boolean")
                rows.append(row)
                if len(rows) > max_rows:
                    break
            frame = pl.DataFrame(rows, schema=headers, orient="row", infer_schema_length=None)
        finally:
            book.close()
    else:
        raise ValueError("Only CSV and XLSX supported")
    if frame.height > max_rows or frame.height == 0:
        raise ValueError("Table is empty or exceeds the configured row limit")
    return frame


def validate_record_ids(frame):
    """Reject lossy programmatic IDs; file readers preserve text IDs."""
    if "record_id" in frame.columns:
        ids = frame["record_id"]
        if ids.dtype != pl.String or ids.null_count() or ids.n_unique() != frame.height:
            raise ValueError("record_id must contain unique non-null strings")
        if ids.str.strip_chars().eq("").any():
            raise ValueError("record_id must not be empty")
