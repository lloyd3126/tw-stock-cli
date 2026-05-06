"""Fetch MOPS annual report top-ten shareholder relationship metadata."""

from __future__ import annotations

import io
import re
from typing import Any
from urllib.parse import urlencode

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t144sb10_w"
REFERER = "https://mopsov.twse.com.tw/mops/web/t144sb10_w"
DOC_BASE_URL = "https://doc.twse.com.tw/server-java/t144sb10"

OUTPUT_COLUMNS = (
    "market",
    "report_year",
    "stock_id",
    "stock_name",
    "shareholder_meeting_date",
    "detail_available",
    "filename",
    "download_request_url",
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
        data=major_shareholder_relationship_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    report_url = published_report_url(response.text)
    if not report_url:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    report_response = requests.get(
        report_url,
        headers=request_headers(accept=HTML_ACCEPT, referer=REFERER),
    )
    html = report_response.content.decode("big5", errors="replace")
    return parse_major_shareholder_relationship_html(html, parameter)


def major_shareholder_relationship_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    stock_id = parameter.get("stock_id") or ""
    return {
        "step": "1",
        "firstin": "ture",
        "off": "1",
        "TYPEK": parameter.get("kind", "sii"),
        "year": parameter.get("year"),
        "co_id1": stock_id,
        "co_id2": stock_id,
    }


def parse_major_shareholder_relationship_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    data_tables = [table for table in tables if {"公司代號", "公司名稱"}.issubset(set(table.columns))]
    if not data_tables:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result = data_tables[0].rename(
        columns={
            "公司代號": "stock_id",
            "公司名稱": "stock_name",
            "召開股東會日期": "shareholder_meeting_date",
        }
    )
    result["market"] = parameter.get("kind", "sii")
    result["report_year"] = int(parameter.get("year"))
    filename_by_stock_id = extract_filenames_by_stock_id(html)
    result["stock_id"] = result["stock_id"].map(clean_text)
    stock_id = clean_text(parameter.get("stock_id"))
    if stock_id:
        result = result[result["stock_id"] == stock_id].copy()
    result["filename"] = result["stock_id"].map(filename_by_stock_id)
    result["detail_available"] = result["filename"].notna()
    result["download_request_url"] = result["filename"].map(download_request_url)
    for column in OUTPUT_COLUMNS:
        if column not in result.columns:
            result[column] = pd.NA
    for column in {"market", "stock_id", "stock_name", "shareholder_meeting_date", "filename"}:
        result[column] = result[column].map(clean_text)
    return result[list(OUTPUT_COLUMNS)]


def published_report_url(html: str) -> str | None:
    match = re.search(r"window\.open\('([^']+)'", html)
    if not match:
        return None
    return match.group(1).replace("&amp;", "&")


def extract_filenames_by_stock_id(html: str) -> dict[str, str]:
    filenames: dict[str, str] = {}
    for row_html in re.findall(r"<tr[^>]*>.*?</tr>", html, flags=re.IGNORECASE | re.DOTALL):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row_html, flags=re.IGNORECASE | re.DOTALL)
        if not cells:
            continue
        stock_id = clean_text(re.sub(r"<[^>]+>", "", cells[0]))
        filename_match = re.search(r'getFile\("([^"]+)"\)', row_html)
        if stock_id and filename_match:
            filenames[stock_id] = filename_match.group(1)
    return filenames


def download_request_url(filename: str | None) -> str | None:
    if not filename:
        return None
    return f"{DOC_BASE_URL}?{urlencode({'step': 9, 'filename': filename})}"


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None
