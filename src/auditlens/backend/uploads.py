"""Bounded, memory-only tabular ingestion. Uploaded paths are never opened."""

import csv
import io
import re
import zipfile
from pathlib import PurePosixPath

import polars as pl
from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
from openpyxl import load_workbook
from starlette.datastructures import UploadFile
from starlette.formparsers import MultiPartException, MultiPartParser

from auditlens.handbook import RAW_COLUMNS, validate_transactions

from .errors import APIError


def headers_valid(headers):
    if len(headers) != len(RAW_COLUMNS) or set(headers) != set(RAW_COLUMNS):
        raise APIError(
            422,
            "invalid_schema",
            "Exactly record_id, timestamp, customer_id, terminal_id, amount required; labels forbidden.",
        )


def row_limit():
    raise APIError(413, "row_limit", "Table exceeds the configured row limit.")


def preflight_xlsx(data, settings, max_rows):
    """Bound ZIP expansion before openpyxl; disallow formulas, links and active content."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        if len(entries) > settings.max_zip_entries:
            raise APIError(413, "unsafe_xlsx", "XLSX contains too many archive entries.")
        if len({e.filename for e in entries}) != len(entries):
            raise APIError(400, "invalid_file", "Duplicate XLSX archive entries.")
        if sum(e.file_size for e in entries) > settings.max_xlsx_expanded_bytes:
            raise APIError(413, "unsafe_xlsx", "XLSX expanded size exceeds the configured limit.")
        for entry in entries:
            path = PurePosixPath(entry.filename)
            if (
                path.is_absolute()
                or ".." in path.parts
                or "\\" in entry.filename
                or entry.flag_bits & 1
                or entry.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}
            ):
                raise APIError(400, "unsafe_xlsx", "Unsupported XLSX archive structure.")
            if entry.file_size > settings.max_zip_ratio * max(1, entry.compress_size):
                raise APIError(413, "unsafe_xlsx", "XLSX compression ratio exceeds the configured limit.")
            if entry.filename.lower().endswith(".bin") or any(
                part.lower() in {"externallinks", "embeddings", "macrosheets"} for part in path.parts
            ):
                raise APIError(400, "unsafe_xlsx", "XLSX active content and external links are unsupported.")
            if not entry.filename.endswith((".xml", ".rels")):
                continue
            # Reading is bounded by prechecked central-directory sizes; zipfile also checks CRC.
            xml = archive.read(entry)
            for _, element in ElementTree.iterparse(io.BytesIO(xml), events=("end",)):
                local = element.tag.rsplit("}", 1)[-1]
                if local == "f" or element.attrib.get("TargetMode", "").lower() == "external":
                    raise APIError(400, "unsafe_xlsx", "Formulas and external relationships are unsupported.")
                # Guard worksheet dimensions, including sparse or deliberately misleading sheets.
                if local in {"c", "dimension"} and entry.filename.startswith("xl/worksheets/"):
                    reference = element.attrib.get("r" if local == "c" else "ref", "")
                    for column, row in re.findall(r"([A-Z]+)([0-9]+)", reference):
                        if len(column) > 2 or (len(column) == 2 and column > "IV") or int(row) > max_rows + 1:
                            row_limit()
                element.clear()


def read_upload(data: bytes, filename: str, max_rows: int, settings):
    if len(data) > settings.max_file_bytes:
        raise APIError(413, "file_too_large", "File exceeds the configured byte limit.")
    suffix = PurePosixPath(filename).suffix.lower()
    if suffix not in {".csv", ".xlsx"}:
        raise APIError(400, "unsupported_file", "Only UTF-8 CSV and XLSX files are supported.")
    rows = []
    try:
        if suffix == ".csv":
            iterator = csv.reader(io.StringIO(data.decode("utf-8-sig"), newline=""), strict=True)
            headers = next(iterator, [])
            headers_valid(headers)
            for row in iterator:
                if not row:  # Match existing CSV reader behavior for blank lines.
                    continue
                if len(row) != len(headers):
                    raise APIError(422, "invalid_schema", "Every CSV row must contain exactly five fields.")
                if len(rows) >= max_rows:
                    row_limit()
                rows.append(row)
        else:
            preflight_xlsx(data, settings, max_rows)
            book = load_workbook(io.BytesIO(data), read_only=True, data_only=False, keep_links=False)
            try:
                sheet = book.active
                if sheet is None or (sheet.max_column is not None and sheet.max_column > 5):
                    raise APIError(422, "invalid_schema", "Active XLSX sheet must have exactly five columns.")
                if sheet.max_row and sheet.max_row > max_rows + 1:
                    row_limit()
                # Dimensions can lie; scan actual cells after the ZIP/XML preflight.
                sheet.reset_dimensions()
                iterator = sheet.iter_rows(values_only=True)
                headers = list(next(iterator, ()))
                headers_valid(headers)
                for row in iterator:
                    if len(rows) >= max_rows:
                        row_limit()
                    if len(row) != len(headers):
                        raise APIError(
                            422, "invalid_schema", "Every XLSX row must contain exactly five fields."
                        )
                    if any(
                        not isinstance(row[headers.index(c)], str)
                        for c in ("record_id", "customer_id", "terminal_id")
                    ):
                        raise APIError(422, "invalid_schema", "XLSX identifiers must be text cells.")
                    if isinstance(row[headers.index("amount")], bool):
                        raise APIError(422, "invalid_schema", "amount must be numeric, not boolean.")
                    rows.append(row)
            finally:
                book.close()
        if not rows:
            raise APIError(422, "empty_table", "Table must contain at least one transaction.")
        frame = pl.DataFrame(rows, schema=headers, orient="row", infer_schema_length=None, strict=True)
        return validate_transactions(frame)
    except APIError:
        raise
    except (UnicodeError, csv.Error, zipfile.BadZipFile, DefusedXmlException, ElementTree.ParseError) as exc:
        raise APIError(400, "invalid_file", "Malformed or unsafe CSV/XLSX file.") from exc
    except ValueError as exc:
        # Do not return parsing-library messages: these may contain financial values.
        raise APIError(
            422,
            "invalid_schema",
            "Values violate the Handbook schema; check text IDs, UTC timestamps and finite nonnegative amounts.",
        ) from exc
    except Exception as exc:
        # All remaining parser errors are input errors; inference exceptions are handled separately.
        raise APIError(400, "invalid_file", "Cannot read this CSV/XLSX file.") from exc


async def multipart_inputs(request, settings):
    if request.headers.get("content-type", "").split(";", 1)[0].lower() != "multipart/form-data":
        raise APIError(
            400, "invalid_multipart", "Use multipart/form-data with transactions, optional history and top_k."
        )
    parser = MultiPartParser(request.headers, request.stream(), max_files=2, max_fields=1, max_part_size=128)
    # The outer ASGI gate bounds the entire body, so uploads never roll to disk.
    parser.spool_max_size = settings.max_request_bytes + 1
    form = None
    try:
        form = await parser.parse()
        items = form.multi_items()
        names = [name for name, _ in items]
        if len(set(names)) != len(names) or set(names) - {"transactions", "history", "top_k"}:
            raise APIError(422, "invalid_fields", "Use each of transactions, history and top_k at most once.")
        if "transactions" not in form or "top_k" not in form:
            raise APIError(422, "missing_field", "transactions and top_k are required.")
        raw_k = form["top_k"]
        if not isinstance(raw_k, str) or not re.fullmatch(r"[0-9]{1,12}", raw_k) or int(raw_k) < 1:
            raise APIError(422, "invalid_top_k", "top_k must be a positive integer (at most 12 digits).")
        result = {}
        for name in ("transactions", "history"):
            if name not in form:
                continue
            upload = form[name]
            if not isinstance(upload, UploadFile):
                raise APIError(422, "invalid_fields", "transactions and history must be file parts.")
            data = await upload.read(settings.max_file_bytes + 1)
            if len(data) > settings.max_file_bytes:
                raise APIError(413, "file_too_large", "File exceeds the configured byte limit.")
            result[name] = (data, upload.filename or "")
        return result, int(raw_k)
    except APIError:
        raise
    except (MultiPartException, ValueError) as exc:
        raise APIError(400, "invalid_multipart", "Malformed multipart body or too many parts.") from exc
    finally:
        if form is not None:
            await form.close()
        # Also close an unfinished final part after a truncated multipart body.
        # Starlette's parser owns these handles; pinned dependency + cleanup regression test.
        for file in parser._files_to_close_on_error:
            file.close()
