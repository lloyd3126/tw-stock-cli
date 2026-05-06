"""Fetch detailed MOPS single-company income statement tables."""

from typing import Any

import pandas as pd
from loguru import logger

from tw_stock_cli.crawlers.mops.common import fetch_company_statement_table


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t164sb04"
REFERER = "https://mopsov.twse.com.tw/mops/web/t164sb04"
STATEMENT = "income_statement"


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    logger.info(parameter)
    return fetch_company_statement_table(URL, REFERER, parameter, STATEMENT)
