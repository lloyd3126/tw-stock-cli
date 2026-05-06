"""Fetch MOPS insider holding company list tables."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_stapap1_all"
REFERER = "https://mopsov.twse.com.tw/mops/web/stapap1_all"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "query_year",
    "query_month",
    "report_ym",
    "market",
    "detail_available",
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
        data=insider_holding_company_list_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()
    return parse_insider_holding_company_list_html(response.text, parameter)


def insider_holding_company_list_form_data(
    parameter: dict[str, Any],
) -> dict[str, Any]:
    market = parameter.get("kind", "sii")
    return {
        "encodeURIComponent": "1",
        "sTYPEK": market,
        "TYPEK": market,
        "firstin": "true",
        "step": "1",
        "kind": "",
        "id": "",
        "skind": parameter.get("industry_code") or "",
        "YM": report_ym(parameter),
    }


def parse_insider_holding_company_list_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="hasBorder")
    if table is None:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        stock_id = clean_text(cells[0].get_text(" ", strip=True))
        if not stock_id or not re.fullmatch(r"\d{4,6}", stock_id):
            continue
        rows.append(
            {
                "stock_id": stock_id,
                "stock_name": clean_text(cells[1].get_text(" ", strip=True)),
                "query_year": int(parameter.get("year")),
                "query_month": int(parameter.get("month")),
                "report_ym": report_ym(parameter),
                "market": parameter.get("kind", "sii"),
                "detail_available": True,
            }
        )

    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def report_ym(parameter: dict[str, Any]) -> str:
    return f"{int(parameter.get('year'))}{int(parameter.get('month')):02d}"


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None
