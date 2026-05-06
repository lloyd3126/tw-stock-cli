"""Fetch MOPS annual report and shareholder meeting electronic book metadata."""

from __future__ import annotations

from typing import Any

import pandas as pd

from tw_stock_cli.crawlers.mops.electronic_book_common import OUTPUT_COLUMNS
from tw_stock_cli.crawlers.mops.electronic_book_common import crawler as book_crawler
from tw_stock_cli.crawlers.mops.electronic_book_common import electronic_book_form_data
from tw_stock_cli.crawlers.mops.electronic_book_common import parse_electronic_book_html


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    return book_crawler(parameter, "t57sb01_q5", "annual_shareholder_meeting")
