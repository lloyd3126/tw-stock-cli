"""Fetch MOPS single-company insider holding balance detail tables."""

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
from tw_stock_cli.crawlers.mops.common import company_name_from_html
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_stapap1"
REFERER = "https://mopsov.twse.com.tw/mops/web/stapap1"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "query_year",
    "query_month",
    "report_ym",
    "role",
    "person_name",
    "elected_shares",
    "current_shares",
    "pledged_shares",
    "pledged_ratio",
    "related_current_shares",
    "related_pledged_shares",
    "related_pledged_ratio",
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
        data=insider_holding_detail_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()
    return parse_insider_holding_detail_html(response.text, parameter)


def insider_holding_detail_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "keyword4": "",
        "code1": "",
        "TYPEK2": "",
        "checkbtn": "",
        "queryName": "co_id",
        "inpuType": "co_id",
        "TYPEK": parameter.get("kind", "all"),
        "isnew": "false",
        "co_id": parameter.get("stock_id"),
        "year": parameter.get("year"),
        "month": f"{int(parameter.get('month')):02d}",
    }


def parse_insider_holding_detail_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="hasBorder")
    if table is None:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    stock_id = str(parameter.get("stock_id"))
    stock_name = company_name_from_html(html)
    report_ym_value = report_ym_from_html(html) or (
        f"{int(parameter.get('year'))}{int(parameter.get('month')):02d}"
    )

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 9:
            continue
        role = clean_text(cells[0].get_text(" ", strip=True))
        if role in (None, "職稱"):
            continue
        rows.append(
            {
                "stock_id": stock_id,
                "stock_name": stock_name,
                "query_year": int(parameter.get("year")),
                "query_month": int(parameter.get("month")),
                "report_ym": report_ym_value,
                "role": role,
                "person_name": clean_text(cells[1].get_text(" ", strip=True)),
                "elected_shares": parse_int(cells[2].get_text(" ", strip=True)),
                "current_shares": parse_int(cells[3].get_text(" ", strip=True)),
                "pledged_shares": parse_int(cells[4].get_text(" ", strip=True)),
                "pledged_ratio": parse_percent(cells[5].get_text(" ", strip=True)),
                "related_current_shares": parse_int(
                    cells[6].get_text(" ", strip=True)
                ),
                "related_pledged_shares": parse_int(
                    cells[7].get_text(" ", strip=True)
                ),
                "related_pledged_ratio": parse_percent(
                    cells[8].get_text(" ", strip=True)
                ),
            }
        )

    result = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    for column in (
        "query_year",
        "query_month",
        "elected_shares",
        "current_shares",
        "pledged_shares",
        "related_current_shares",
        "related_pledged_shares",
    ):
        if column in result.columns:
            result[column] = pd.to_numeric(result[column], errors="coerce").astype(
                "Int64"
            )
    return result


def report_ym_from_html(html: str) -> str | None:
    match = re.search(r"資料年月:?\s*(\d{5})", html)
    return match.group(1) if match else None


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None


def parse_int(value: Any) -> int | None:
    text = clean_text(value)
    if text is None:
        return None
    text = re.sub(r"[,\s]", "", text)
    if not text or text in {"-", "--"}:
        return None
    return int(text)


def parse_percent(value: Any) -> float | None:
    text = clean_text(value)
    if text is None:
        return None
    text = text.replace("%", "")
    return float(text) if text else None
