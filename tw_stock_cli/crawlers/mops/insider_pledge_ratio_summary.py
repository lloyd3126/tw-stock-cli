"""Fetch MOPS director/supervisor pledge ratio summary tables."""

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
from tw_stock_cli.crawlers.mops.insider_shareholding_change import published_report_url


URL = "https://mopsov.twse.com.tw/mops/web/ajax_IRB180"
REFERER = "https://mopsov.twse.com.tw/mops/web/IRB180"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "query_year",
    "query_month",
    "report_ym",
    "pledge_ratio_bucket",
    "pledge_ratio",
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
        data=insider_pledge_ratio_summary_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()

    report_url = published_report_url(response.text)
    if not report_url:
        return pd.DataFrame()
    report_response = requests.get(
        report_url,
        headers=request_headers(accept=HTML_ACCEPT, referer=REFERER),
    )
    if not report_response.content:
        return pd.DataFrame()

    html = report_response.content.decode("cp950", errors="replace")
    return parse_insider_pledge_ratio_summary_html(html, parameter)


def insider_pledge_ratio_summary_form_data(
    parameter: dict[str, Any],
) -> dict[str, Any]:
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "TYPEK": parameter.get("kind", "sii"),
        "year": parameter.get("year"),
        "month": f"{int(parameter.get('month')):02d}",
    }


def parse_insider_pledge_ratio_summary_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html), header=None)
    except (ImportError, ValueError):
        return pd.DataFrame()

    data_tables = [table for table in tables if len(table.columns) >= 2]
    if not data_tables:
        return pd.DataFrame()
    return normalize_insider_pledge_ratio_summary_table(data_tables[0], parameter)


def normalize_insider_pledge_ratio_summary_table(
    table: pd.DataFrame,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    bucket: str | None = None
    for _, source_row in table.iloc[1:].iterrows():
        first = clean_text(source_row.iloc[0])
        if first:
            bucket = first
        for value in source_row.iloc[1:]:
            parsed = parse_company_ratio(value)
            if parsed is None:
                continue
            stock_id, stock_name, ratio = parsed
            rows.append(
                {
                    "stock_id": stock_id,
                    "stock_name": stock_name,
                    "query_year": int(parameter.get("year")),
                    "query_month": int(parameter.get("month")),
                    "report_ym": (
                        f"{int(parameter.get('year'))}{int(parameter.get('month')):02d}"
                    ),
                    "pledge_ratio_bucket": bucket,
                    "pledge_ratio": ratio,
                }
            )

    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def parse_company_ratio(value: Any) -> tuple[str, str, float] | None:
    text = clean_text(value)
    if text is None:
        return None
    match = re.match(r"^(\d{4,6})\s+(.+)\s+([0-9]+(?:\.[0-9]+)?)$", text)
    if not match:
        return None
    return match.group(1), match.group(2), float(match.group(3))


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    if text.lower() == "nan":
        return None
    return text or None
