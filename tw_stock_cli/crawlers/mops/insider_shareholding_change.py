"""Fetch MOPS insider shareholding change summary tables."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_IRB110"
REFERER = "https://mopsov.twse.com.tw/mops/web/IRB110"

PUBLISHED_URL_PATTERN = re.compile(r"https://siis\.twse\.com\.tw/publish/[^'\"<>]+")

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "query_year",
    "query_month",
    "report_ym",
    "issued_shares",
    "directors_supervisors_increase_shares",
    "directors_supervisors_decrease_shares",
    "directors_supervisors_held_shares",
    "directors_supervisors_holding_ratio",
    "managers_held_shares",
    "major_shareholders_held_shares",
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
        data=insider_shareholding_change_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()

    published_url = published_report_url(response.text)
    if not published_url:
        return pd.DataFrame()

    report_response = requests.get(
        published_url,
        headers=request_headers(accept=HTML_ACCEPT, referer=REFERER),
    )
    if not report_response.content:
        return pd.DataFrame()

    html = report_response.content.decode("cp950", errors="replace")
    return parse_insider_shareholding_change_html(html, parameter)


def insider_shareholding_change_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "TYPEK": parameter.get("kind", "sii"),
        "year": parameter.get("year"),
        "month": f"{int(parameter.get('month')):02d}",
    }


def published_report_url(html: str) -> str | None:
    match = PUBLISHED_URL_PATTERN.search(html)
    return match.group(0) if match else None


def parse_insider_shareholding_change_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html), header=None)
    except (ImportError, ValueError):
        return pd.DataFrame()

    data_tables = [table for table in tables if len(table.columns) >= 8]
    if not data_tables:
        return pd.DataFrame()
    return normalize_insider_shareholding_change_table(data_tables[0], parameter)


def normalize_insider_shareholding_change_table(
    table: pd.DataFrame,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    result = table.iloc[:, :8].copy()
    result.columns = [
        "company",
        "issued_shares",
        "directors_supervisors_increase_shares",
        "directors_supervisors_decrease_shares",
        "directors_supervisors_held_shares",
        "directors_supervisors_holding_ratio",
        "managers_held_shares",
        "major_shareholders_held_shares",
    ]

    company_parts = result["company"].astype(str).str.extract(r"^(\d{4,6})(.+)$")
    result.insert(0, "stock_id", company_parts[0])
    result.insert(1, "stock_name", company_parts[1].map(clean_text))
    result = result[result["stock_id"].notna()].copy()
    result = result.drop(columns=["company"])

    result.insert(2, "query_year", int(parameter.get("year")))
    result.insert(3, "query_month", int(parameter.get("month")))
    result.insert(
        4,
        "report_ym",
        f"{int(parameter.get('year'))}{int(parameter.get('month')):02d}",
    )

    for column in result.columns:
        if column in {"stock_id", "stock_name", "report_ym"}:
            continue
        result[column] = pd.to_numeric(
            result[column].astype(str).map(clean_number_text),
            errors="coerce",
        )

    result["query_year"] = result["query_year"].astype("Int64")
    result["query_month"] = result["query_month"].astype("Int64")
    return result[list(OUTPUT_COLUMNS)]


def clean_text(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None


def clean_number_text(value: Any) -> str:
    return re.sub(r"[,\s]", "", str(value).replace("\xa0", ""))
