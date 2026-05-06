"""Fetch MOPS private placement security summary tables."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t116sb01"
REFERER = "https://mopsov.twse.com.tw/mops/web/t116sb01"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "security_type",
    "stock_kind",
    "decision_date",
    "decision_detail_available",
    "year_period",
    "private_year",
    "private_seq_no",
    "pricing_detail_available",
    "payment_detail_available",
    "fund_utilization_periods",
)

EXTRA_COLUMNS = (
    "decision_report_type",
    "pricing_report_type",
    "payment_report_type",
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
        data=private_placement_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()
    return parse_private_placement_html(response.text, parameter)


def private_placement_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
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
        "TYPEK": parameter.get("kind", "sii"),
        "co_id": parameter.get("stock_id") or "",
    }


def parse_private_placement_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="hasBorder")
    if table is None:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    rows: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for source_row in table.find_all("tr"):
        cells = source_row.find_all("td")
        if len(cells) < 8:
            continue

        stock_id = clean_text(cells[0].get_text(" ", strip=True))
        stock_name = clean_text(cells[1].get_text(" ", strip=True))
        security_type = clean_text(cells[2].get_text(" ", strip=True))
        if stock_id:
            current = {
                "stock_id": stock_id,
                "stock_name": stock_name,
                "security_type": security_type,
            }
        if not current.get("stock_id"):
            continue

        decision_params = onclick_params(cells[3])
        pricing_params = onclick_params(cells[5])
        payment_params = onclick_params(cells[6])
        periods = fund_utilization_periods(cells[7])
        year_period = clean_text(cells[4].get_text(" ", strip=True))

        private_year = pricing_params.get("year") or payment_params.get("year")
        private_seq_no = pricing_params.get("seq_no") or payment_params.get("seq_no")
        if year_period and "/" in year_period:
            private_year = private_year or year_period.split("/", 1)[0]
            private_seq_no = private_seq_no or year_period.split("/", 1)[1]

        rows.append(
            {
                "stock_id": current.get("stock_id"),
                "stock_name": current.get("stock_name"),
                "market": parameter.get("kind", "sii"),
                "security_type": current.get("security_type"),
                "stock_kind": (
                    decision_params.get("stock_kind")
                    or pricing_params.get("stock_kind")
                    or payment_params.get("stock_kind")
                ),
                "decision_date": roc_compact_date(
                    decision_params.get("decide_date")
                    or pricing_params.get("decide_date")
                    or payment_params.get("decide_date")
                ),
                "decision_detail_available": bool(decision_params),
                "year_period": year_period,
                "private_year": parse_int(private_year),
                "private_seq_no": parse_int(private_seq_no),
                "pricing_detail_available": bool(pricing_params),
                "payment_detail_available": bool(payment_params),
                "fund_utilization_periods": "；".join(periods) if periods else None,
                "decision_report_type": decision_params.get("report_type"),
                "pricing_report_type": pricing_params.get("report_type"),
                "payment_report_type": payment_params.get("report_type"),
            }
        )

    return pd.DataFrame(rows, columns=(*OUTPUT_COLUMNS, *EXTRA_COLUMNS))


def onclick_params(node: Any) -> dict[str, str]:
    params: dict[str, str] = {}
    onclick_values = [
        element.get("onclick", "")
        for element in node.find_all(["input", "button"])
        if element.get("onclick")
    ]
    if not onclick_values:
        return params
    for name, value in re.findall(r"\.([A-Za-z0-9_]+)\.value='([^']*)'", onclick_values[0]):
        params[name] = value
    return params


def fund_utilization_periods(node: Any) -> list[str]:
    periods: list[str] = []
    for element in node.find_all(["button", "input"]):
        onclick = element.get("onclick", "")
        match = re.search(r"\.ys\.value='([^']+)'", onclick)
        if match:
            periods.append(match.group(1))
            continue
        text = clean_text(element.get_text(" ", strip=True))
        if text and re.fullmatch(r"\d{5}", text):
            periods.append(text)
    if periods:
        return periods
    text = clean_text(node.get_text(" ", strip=True))
    if not text:
        return []
    return re.findall(r"\d{5}", text)


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text if text and text != "\xa0" else None


def roc_compact_date(value: str | None) -> str | None:
    if not value:
        return None
    value = re.sub(r"\D", "", value)
    if len(value) == 7:
        return f"{value[:3]}/{value[3:5]}/{value[5:]}"
    return value or None


def parse_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    text = re.sub(r"[^0-9-]", "", str(value))
    return int(text) if text and text != "-" else None
