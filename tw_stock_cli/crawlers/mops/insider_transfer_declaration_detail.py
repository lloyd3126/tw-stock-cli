"""Fetch MOPS single-company insider prior transfer declaration tables."""

from __future__ import annotations

from typing import Any

import pandas as pd

from tw_stock_cli.crawlers.mops.insider_transfer_common import fetch_transfer_table


REFERER = "https://mopsov.twse.com.tw/mops/web/t56sb21_q1"


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    return fetch_transfer_table(
        parameter,
        sstep=1,
        report_type="declaration_detail",
        referer=REFERER,
    )
