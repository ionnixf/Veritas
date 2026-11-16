"""The direct file inference path must preserve identifiers without coercion."""

import io
import zipfile
from datetime import datetime

import pytest
from openpyxl import Workbook

from auditlens.handbook import RAW_COLUMNS, validate_transactions
from auditlens.io import read_table


def write_xlsx(path, rows):
    book = Workbook()
    book.active.append(RAW_COLUMNS)
    for row in rows:
        book.active.append(row)
    book.save(path)
    book.close()


@pytest.mark.parametrize("suffix", [".csv", ".xlsx"])
def test_file_readers_preserve_na_and_leading_zero_identifiers(tmp_path, suffix):
    rows = [
        ["NA", "2026-02-01T12:00:00", "NA", "0001", 10],
        ["0002", "2026-02-01T13:00:00", "0003", "NA", 20],
    ]
    path = tmp_path / f"transactions{suffix}"
    if suffix == ".csv":
        import csv

        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(RAW_COLUMNS)
            writer.writerows(rows)
    else:
        write_xlsx(path, rows)
    actual = validate_transactions(read_table(path))
    for name in ("record_id", "customer_id", "terminal_id"):
        index = RAW_COLUMNS.index(name)
        assert actual[name].to_list() == [row[index] for row in rows]


@pytest.mark.parametrize("column,value", [(0, 2), (2, 2), (3, 2), (4, True)])
def test_xlsx_rejects_lossy_mixed_cell_types_before_polars_coercion(tmp_path, column, value):
    first = ["r1", "2026-02-01T12:00:00", "c", "t", 10]
    second = ["r2", "2026-02-01T13:00:00", "c", "t", 20]
    second[column] = value
    path = tmp_path / "mixed.xlsx"
    write_xlsx(path, [first, second])
    with pytest.raises(ValueError):
        read_table(path)


def test_xlsx_rejects_formula_cells_instead_of_using_cached_values(tmp_path):
    path = tmp_path / "formula.xlsx"
    write_xlsx(path, [['="r1"', "2026-02-01T12:00:00", "c", "t", 10]])
    with pytest.raises(ValueError, match="formulas"):
        read_table(path)


def test_xlsx_native_datetime_remains_usable(tmp_path):
    path = tmp_path / "datetime.xlsx"
    timestamp = datetime(2026, 2, 1, 12)
    write_xlsx(path, [["r1", timestamp, "c", "t", 10]])
    assert validate_transactions(read_table(path))["timestamp"][0] == timestamp


@pytest.mark.parametrize("max_rows", [1, 2])
def test_xlsx_stale_dimensions_cannot_truncate_records_or_bypass_row_limits(tmp_path, max_rows):
    path = tmp_path / "dimensions.xlsx"
    write_xlsx(
        path,
        [
            ["r1", "2026-02-01T12:00:00", "c", "t", 10],
            ["r2", "2026-02-01T13:00:00", "c", "t", 20],
        ],
    )
    output = io.BytesIO()
    with zipfile.ZipFile(path) as source, zipfile.ZipFile(output, "w") as archive:
        for entry in source.infolist():
            content = source.read(entry)
            if entry.filename == "xl/worksheets/sheet1.xml":
                content = content.replace(b'ref="A1:E3"', b'ref="A1:E2"')
            archive.writestr(entry, content)
    path.write_bytes(output.getvalue())
    if max_rows == 1:
        with pytest.raises(ValueError, match="row limit"):
            read_table(path, max_rows=max_rows)
    else:
        assert read_table(path, max_rows=max_rows)["record_id"].to_list() == ["r1", "r2"]
