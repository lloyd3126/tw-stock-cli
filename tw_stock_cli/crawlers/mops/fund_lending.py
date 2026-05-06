"""Fetch MOPS fund lending disclosure details."""

from __future__ import annotations

from typing import Any

import pandas as pd

from tw_stock_cli.crawlers.mops.lending_endorsement_common import LENDING_COLUMNS
from tw_stock_cli.crawlers.mops.lending_endorsement_common import crawler as section_crawler
from tw_stock_cli.crawlers.mops.lending_endorsement_common import (
    lending_endorsement_form_data,
)
from tw_stock_cli.crawlers.mops.lending_endorsement_common import parse_fund_lending_html


OUTPUT_COLUMNS = LENDING_COLUMNS


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    return section_crawler(parameter, "lending")
