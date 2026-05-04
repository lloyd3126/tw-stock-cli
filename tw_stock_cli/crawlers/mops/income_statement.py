"""Fetch MOPS quarterly income statement summary tables."""

from typing import Any

import pandas as pd
from loguru import logger

from tw_stock_cli.crawlers.mops.common import fetch_statement_tables


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t163sb04"
REFERER = "https://mopsov.twse.com.tw/mops/web/t163sb04"


def crawler(parameter: dict[str, Any]) -> list[pd.DataFrame]:
    logger.info(parameter)
    return fetch_statement_tables(URL, REFERER, parameter)


if __name__ == "__main__":
    # kind selects listed, OTC, emerging, or public-company statement tables.
    parameter = {"kind": "sii", "year": 111, "quar": 1}
    df = crawler(parameter)
    print(df)
