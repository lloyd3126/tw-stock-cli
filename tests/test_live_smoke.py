from __future__ import annotations

import os

import pytest

from tw_stock_cli.cli import transform_output
from tw_stock_cli.cli import validation_result
from tw_stock_cli.registry import get_dataset


pytestmark = pytest.mark.skipif(
    os.environ.get("TW_STOCK_LIVE_TESTS") != "1",
    reason="set TW_STOCK_LIVE_TESTS=1 to run live exchange smoke tests",
)


@pytest.mark.parametrize(
    ("dataset_id", "params"),
    [
        ("twse.stock-price", {"date": "2026-04-30"}),
        ("twse.margin-trade", {"date": "2026-04-30"}),
        ("tpex.stock-price", {"date": "2026-04-30"}),
        ("tpex.margin-trade", {"date": "2026-04-30"}),
        ("tpex.institutional-trade", {"date": "2026-04-30"}),
        ("taifex.futures-daily", {"date": "2026-04-30"}),
        ("taifex.futures-institutional", {"date": "2026-04-30"}),
        ("taifex.fcm-futures-volume-day", {}),
        ("mops.month-revenue", {"year": 115, "month": 3, "market": "sii"}),
        ("mops.income-statement", {"year": 114, "quarter": 4, "market": "sii"}),
    ],
)
def test_live_dataset_smoke(dataset_id: str, params: dict[str, object]) -> None:
    dataset = get_dataset(dataset_id)
    output = dataset.fetch(params)
    output = transform_output(output, columns=None, limit=2)
    result = validation_result(dataset, output)

    assert result["ok"], result
