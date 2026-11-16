"""Explicit, per-process resource limits."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    max_file_bytes: int = 8 * 1024 * 1024
    max_request_bytes: int = 17 * 1024 * 1024
    max_transactions: int = 10_000
    max_history: int = 100_000
    max_combined_rows: int = 110_000
    max_concurrent: int = 1
    threads: int = 2
    max_xlsx_expanded_bytes: int = 32 * 1024 * 1024
    max_zip_entries: int = 128
    max_zip_ratio: int = 200
    frontend_origin: str | None = None

    def __post_init__(self):
        for name, value in vars(self).items():
            if name != "frontend_origin" and (type(value) is not int or value < 1):
                raise ValueError(f"{name} must be a positive integer")
        if self.threads not in (1, 2):
            raise ValueError("threads must be 1 or 2")
        if max(self.max_transactions, self.max_history) > 1_000_000 or self.max_combined_rows > 2_000_000:
            raise ValueError("Limits cannot exceed the Handbook contract")
        if self.frontend_origin:
            from urllib.parse import urlsplit

            origin = urlsplit(self.frontend_origin)
            if (
                origin.scheme not in {"http", "https"}
                or not origin.netloc
                or origin.username
                or origin.password
                or origin.path
                or origin.query
                or origin.fragment
                or "*" in origin.netloc
            ):
                raise ValueError("frontend_origin must be one exact HTTP(S) origin without a trailing slash")

    @classmethod
    def from_env(cls):
        values = {}
        for name in cls.__dataclass_fields__:
            raw = os.environ.get(f"AUDITLENS_{name.upper()}")
            if raw is not None:
                values[name] = (raw or None) if name == "frontend_origin" else int(raw)
        return cls(**values)
