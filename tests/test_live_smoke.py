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
        (
            "mops.company-cash-flow",
            {"stock_id": "2395", "year": 114, "quarter": 4, "market": "sii"},
        ),
        (
            "mops.company-equity-changes",
            {"stock_id": "2395", "year": 114, "quarter": 4, "market": "sii"},
        ),
        ("mops.company-basic-info", {"stock_id": "2395", "market": "sii"}),
        ("mops.dividend-distribution", {"stock_id": "2395", "year": 114}),
        (
            "mops.ex-dividend-announcement",
            {"stock_id": "2395", "year": 114, "market": "sii"},
        ),
        (
            "mops.insider-shareholding-change",
            {"year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.insider-shareholding-detail",
            {"stock_id": "2395", "year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.insider-holding-company-list",
            {"year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.insider-holding-detail",
            {"stock_id": "2395", "year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.insider-transfer-declaration-detail",
            {"stock_id": "1210", "year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.insider-transfer-declaration-summary",
            {"year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.insider-transfer-untransferred-detail",
            {"stock_id": "2254", "year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.insider-transfer-untransferred-summary",
            {"year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.insider-pledge-summary",
            {"year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.insider-pledge-ratio-summary",
            {"year": 114, "month": 3, "market": "sii"},
        ),
        ("mops.treasury-stock-buyback", {"stock_id": "1101", "market": "sii"}),
        ("mops.private-placement", {"stock_id": "1316", "market": "sii"}),
        (
            "mops.asset-acquisition-disposal-financial",
            {"stock_id": "8011", "year": 113, "month": 9, "market": "sii"},
        ),
        (
            "mops.fund-lending",
            {"stock_id": "1101", "year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.endorsement-guarantee",
            {"stock_id": "1101", "year": 114, "month": 3, "market": "sii"},
        ),
        (
            "mops.related-party-transaction",
            {"stock_id": "8011", "year": 113, "month": 9, "market": "sii"},
        ),
        ("mops.investor-conference", {"stock_id": "2395", "year": 114, "market": "sii"}),
        ("mops.material-info", {"stock_id": "2395", "year": 114}),
        (
            "mops.material-info-detail",
            {
                "stock_id": "2395",
                "market": "sii",
                "seq_no": "4",
                "spoke_date": "20250227",
                "spoke_time": "143238",
            },
        ),
        ("mops.shareholder-meeting", {"stock_id": "2395", "year": 114, "market": "sii"}),
    ],
)
def test_live_dataset_smoke(dataset_id: str, params: dict[str, object]) -> None:
    dataset = get_dataset(dataset_id)
    output = dataset.fetch(params)
    output = transform_output(output, columns=None, limit=2)
    result = validation_result(dataset, output)

    assert result["ok"], result
