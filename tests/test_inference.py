"""Independent history-window checks and timestamp serialization boundaries."""

import random
from datetime import date, datetime, timedelta

import numpy as np
import polars as pl
import pytest

from auditlens.handbook import past_features, validate_transactions


def transaction(timestamp):
    return pl.DataFrame(
        {
            "record_id": ["r"],
            "timestamp": [timestamp],
            "customer_id": ["c"],
            "terminal_id": ["t"],
            "amount": [1],
        }
    )


@pytest.mark.parametrize("amount", [date(2026, 2, 1), datetime(2026, 2, 1), timedelta(days=1)])
def test_temporal_values_cannot_silently_become_amounts(amount):
    frame = transaction("2026-02-01T12:00:00").with_columns(pl.Series("amount", [amount]))
    with pytest.raises(ValueError, match="amount must be numeric"):
        validate_transactions(frame)


@pytest.mark.parametrize(
    "timestamp", ["0000-01-01T00:00:00", "2026-2-1T1:2:3", datetime(2026, 2, 1, microsecond=1)]
)
def test_timestamps_must_fit_the_exact_public_serialization_contract(timestamp):
    with pytest.raises(ValueError, match="timestamp"):
        validate_transactions(transaction(timestamp))


@pytest.mark.parametrize("timestamp", ["0001-01-01T00:00:00", "0999-01-01T00:00:00", "9999-12-31T23:59:59"])
def test_supported_timestamp_extremes_serialize_and_generate_finite_features(timestamp):
    frame = transaction(timestamp)
    parsed = validate_transactions(frame).to_dicts()[0]["timestamp"]
    assert parsed.isoformat(timespec="seconds") == timestamp
    assert np.isfinite(past_features(frame).to_numpy()).all()


def test_past_windows_match_independent_scalar_reference_in_original_order():
    rng = random.Random(928)
    start = datetime(2026, 1, 1, 12)
    rows = [
        {
            "record_id": str(i),
            "timestamp": start + timedelta(hours=rng.randrange(40 * 24)),
            "customer_id": f"c{rng.randrange(4)}",
            "terminal_id": f"t{rng.randrange(3)}",
            "amount": float(rng.randrange(500)),
        }
        for i in range(60)
    ]
    # Exact lower boundaries are included; all simultaneous records are excluded.
    rows += [
        {
            "record_id": f"boundary-{i}",
            "timestamp": start + timedelta(days=day),
            "customer_id": "boundary",
            "terminal_id": "boundary",
            "amount": float(i + 10),
        }
        for i, day in enumerate([0, 1, 1, 7, 30, 31])
    ]
    rng.shuffle(rows)
    features = past_features(pl.DataFrame(rows))
    assert features["amount"].to_list() == [row["amount"] for row in rows]
    for actual, row in zip(features.iter_rows(named=True), rows):
        for entity, windows in [("customer", (1, 7, 30)), ("terminal", (1, 7))]:
            key = f"{entity}_id"
            for days in windows:
                values = [
                    past["amount"]
                    for past in rows
                    if past[key] == row[key]
                    and row["timestamp"] - timedelta(days=days) <= past["timestamp"] < row["timestamp"]
                ]
                expected = {
                    "count": len(values),
                    "sum": sum(values),
                    "mean": np.mean(values) if values else 0,
                    "std": np.std(values) if values else 0,
                }
                for statistic, value in expected.items():
                    np.testing.assert_allclose(
                        actual[f"{entity}_{statistic}_{days}d"], value, rtol=1e-5, atol=1e-4
                    )
        assert actual["pair_count_30d"] == sum(
            past["customer_id"] == row["customer_id"]
            and past["terminal_id"] == row["terminal_id"]
            and row["timestamp"] - timedelta(days=30) <= past["timestamp"] < row["timestamp"]
            for past in rows
        )
