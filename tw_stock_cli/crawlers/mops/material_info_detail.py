"""Fetch MOPS material information detail pages."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t05st01"
REFERER = "https://mopsov.twse.com.tw/mops/web/t05st01"

FIELD_MAP = {
    "序號": "seq_no",
    "發言日期": "announcement_date",
    "發言時間": "announcement_time",
    "發言人": "spokesperson",
    "發言人職稱": "spokesperson_title",
    "發言人電話": "spokesperson_phone",
    "主旨": "subject",
    "符合條款": "clause",
    "事實發生日": "event_date",
    "說明": "description",
}


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
        data=material_info_detail_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()
    return parse_material_info_detail_html(response.text, parameter)


def material_info_detail_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "encodeURIComponent": "1",
        "firstin": "true",
        "step": "2",
        "off": "1",
        "co_id": parameter.get("stock_id"),
        "TYPEK": parameter.get("kind", "all"),
        "seq_no": parameter.get("seq_no"),
        "spoke_date": parameter.get("spoke_date"),
        "spoke_time": parameter.get("spoke_time"),
    }


def parse_material_info_detail_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    record: dict[str, Any] = {
        "stock_id": str(parameter.get("stock_id")),
        "detail_seq_no": str(parameter.get("seq_no")),
        "detail_spoke_date": str(parameter.get("spoke_date")),
        "detail_spoke_time": str(parameter.get("spoke_time")),
        "detail_type": parameter.get("kind"),
    }
    company = company_from_html(soup)
    if company:
        record.update(company)

    detail_table = first_detail_table(soup)
    if detail_table:
        record.update(parse_detail_table(detail_table))

    disclaimer = disclaimer_from_html(soup)
    if disclaimer:
        record["disclaimer"] = disclaimer

    if not any(key in record for key in ("subject", "description", "seq_no")):
        return pd.DataFrame()
    return pd.DataFrame([record])


def first_detail_table(soup: BeautifulSoup) -> Any:
    for table in soup.find_all("table"):
        text = table.get_text(" ", strip=True)
        if "發言日期" in text and "主旨" in text and "說明" in text:
            return table
    return None


def parse_detail_table(table: Any) -> dict[str, str]:
    record: dict[str, str] = {}
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        values = [clean_text(cell.get_text("\n", strip=True)) for cell in cells]
        values = [value for value in values if value]
        for label, value in label_value_pairs(values):
            key = FIELD_MAP.get(normalize_label(label))
            if key and value and key not in record:
                record[key] = value
    return record


def label_value_pairs(values: list[str]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    index = 0
    while index < len(values) - 1:
        label = normalize_label(values[index])
        if label in FIELD_MAP:
            value_parts = []
            index += 1
            while index < len(values) and normalize_label(values[index]) not in FIELD_MAP:
                value_parts.append(values[index])
                index += 1
            pairs.append((label, clean_text(" ".join(value_parts))))
        else:
            index += 1
    return pairs


def company_from_html(soup: BeautifulSoup) -> dict[str, str]:
    text = soup.get_text(" ", strip=True)
    match = re.search(r"本資料由\s*（?([^）\s]+)公司）?\s*(\d+)\s+(\S+)\s*公司提供", text)
    if not match:
        match = re.search(r"本資料由\s*\(([^)]*)\)\s*(\d+)\s+(\S+)\s*公司提供", text)
    if not match:
        return {}
    return {
        "market_name": match.group(1).strip(),
        "stock_id": match.group(2).strip(),
        "stock_name": match.group(3).strip(),
    }


def disclaimer_from_html(soup: BeautifulSoup) -> str | None:
    text = soup.get_text(" ", strip=True)
    match = re.search(r"(以上資料均由各公司.+?負責。)", text)
    return clean_text(match.group(1)) if match else None


def normalize_label(value: str) -> str:
    return re.sub(r"\s+", "", value)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()
