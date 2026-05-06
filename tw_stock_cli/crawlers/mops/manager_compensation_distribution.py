"""Fetch MOPS manager employee compensation distribution tables."""

from __future__ import annotations

import io
import re
from typing import Any

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t114sb07"
REFERER = "https://mopsov.twse.com.tw/mops/web/t114sb07"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "compensation_year",
    "distribution_year",
    "stock_compensation_shares",
    "stock_compensation_market_price",
    "stock_compensation_amount",
    "cash_compensation_amount",
    "total_compensation_amount",
    "profit_ratio",
    "remark",
)

DATA_COLUMNS = (
    "stock_id",
    "stock_name",
    "stock_compensation_shares",
    "stock_compensation_market_price",
    "stock_compensation_amount",
    "cash_compensation_amount",
    "total_compensation_amount",
    "profit_ratio",
    "remark",
)


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    logger.info(parameter)
    response = requests.post(
        URL,
        headers=request_headers(
            accept=HTML_ACCEPT,
            referer=REFERER,
            origin=STATEMENT_ORIGIN,
            content_type="application/x-www-form-urlencoded",
        ),
        data=manager_compensation_distribution_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_manager_compensation_distribution_html(response.text, parameter)


def manager_compensation_distribution_form_data(
    parameter: dict[str, Any],
) -> dict[str, Any]:
    stock_id = parameter.get("stock_id")
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "ture",
        "off": "1",
        "keyword4": "",
        "code1": "",
        "TYPEK2": "",
        "checkbtn": "",
        "queryName": "",
        "inpuType": "co_id",
        "TYPEK": parameter.get("kind", "all"),
        "co_id_1": stock_id,
        "co_id_2": stock_id,
        "year": parameter.get("year"),
    }


def parse_manager_compensation_distribution_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    data_tables = [table for table in tables if len(table.columns) >= len(DATA_COLUMNS)]
    if not data_tables:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    compensation_year, distribution_year = report_years(html, parameter)
    result = data_tables[-1].iloc[:, : len(DATA_COLUMNS)].copy()
    result.columns = DATA_COLUMNS
    result = result[result["stock_id"].map(is_stock_id)].copy()
    result.insert(2, "market", parameter.get("kind", "all"))
    result.insert(3, "compensation_year", compensation_year)
    result.insert(4, "distribution_year", distribution_year)

    for column in result.columns:
        if column in {"stock_id", "stock_name", "market", "remark"}:
            result[column] = result[column].map(clean_text)
            continue
        result[column] = pd.to_numeric(
            result[column].map(clean_number_text),
            errors="coerce",
        )
    result["stock_id"] = result["stock_id"].astype(str)
    return result[list(OUTPUT_COLUMNS)].reset_index(drop=True)


def report_years(html: str, parameter: dict[str, Any]) -> tuple[int | None, int]:
    compensation_year = None
    distribution_year = int(parameter.get("year"))
    text = re.sub(r"<input[^>]*>", "", html)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text)
    match = re.search(
        r"員工酬勞所屬年度[:：]\s*(\d+).*?分派員工酬勞年度[:：]\s*(\d+)",
        text,
        re.S,
    )
    if match:
        compensation_year = int(match.group(1))
        distribution_year = int(match.group(2))
    return compensation_year, distribution_year


def is_stock_id(value: Any) -> bool:
    text = clean_text(value)
    return bool(text and re.fullmatch(r"\d{4,6}", text))


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None


def clean_number_text(value: Any) -> str | None:
    text = clean_text(value)
    if text is None:
        return None
    if text in {"-", "--", "----", "------"}:
        return None
    return re.sub(r"[,%]", "", text)
