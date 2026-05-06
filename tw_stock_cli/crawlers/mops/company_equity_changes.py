"""Fetch detailed MOPS single-company statements of changes in equity."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import html_tables
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import clean_statement_item
from tw_stock_cli.crawlers.mops.common import company_name_from_html
from tw_stock_cli.crawlers.mops.common import company_statement_form_data
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t164sb06"
REFERER = "https://mopsov.twse.com.tw/mops/web/t164sb06"
STATEMENT = "equity_changes"


def crawler(parameter: dict[str, Any]) -> list[pd.DataFrame]:
    logger.info(parameter)
    response = requests.post(
        URL,
        headers=request_headers(
            accept=HTML_ACCEPT,
            referer=REFERER,
            origin=STATEMENT_ORIGIN,
            content_type="application/x-www-form-urlencoded",
        ),
        data=company_statement_form_data(parameter),
    )
    if has_no_data(response.text):
        return []

    company_name = company_name_from_html(response.text)
    tables = [table for table in html_tables(response.text) if len(table.columns) >= 5]
    return [
        normalize_equity_changes_table(table, response.text, parameter, company_name)
        for table in tables
    ]


def normalize_equity_changes_table(
    table: pd.DataFrame,
    html: str,
    parameter: dict[str, Any],
    company_name: str | None = None,
) -> pd.DataFrame:
    """Normalize one MOPS equity-changes table into row-per-account form."""
    statement_year = statement_year_from_columns(table.columns)
    headers = [clean_statement_item(str(value)) for value in table.iloc[0].tolist()]
    headers = [header if header and header != "nan" else f"unnamed_{index}" for index, header in enumerate(headers)]
    headers[0] = "item"

    result = table.iloc[1:].copy()
    result.columns = unique_columns(headers)
    result = result.dropna(axis=1, how="all")
    result = result.loc[:, ~result.columns.str.startswith("unnamed_")]

    raw_items = result["item"].astype(str)
    result.insert(0, "statement", STATEMENT)
    result.insert(0, "statement_year", statement_year)
    result.insert(0, "quarter", int(parameter.get("quar")))
    result.insert(0, "report_year", int(parameter.get("year")))
    result.insert(0, "stock_name", company_name or company_name_from_html(html))
    result.insert(0, "stock_id", str(parameter.get("stock_id")))
    result.insert(
        7,
        "indent_level",
        raw_items.map(lambda item: len(item) - len(item.lstrip(" \u3000"))),
    )
    result["item"] = raw_items.map(clean_statement_item)

    return result


def statement_year_from_columns(columns: pd.Index) -> int | None:
    first_column = columns[0]
    first_part = first_column[0] if isinstance(first_column, tuple) else first_column
    match = re.search(r"民國\s*(\d+)\s*年度", str(first_part))
    return int(match.group(1)) if match else None


def unique_columns(columns: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    result = []
    for column in columns:
        count = seen.get(column, 0)
        seen[column] = count + 1
        result.append(column if count == 0 else f"{column}_{count + 1}")
    return result
