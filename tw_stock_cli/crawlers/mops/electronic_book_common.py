"""Shared parsing for MOPS electronic book metadata pages."""

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


DOC_BASE_URL = "https://doc.twse.com.tw/server-java/t57sb01"

OUTPUT_COLUMNS = (
    "stock_id",
    "document_year",
    "document_type",
    "detail_type",
    "case_type",
    "meeting_type",
    "nature",
    "detail_description",
    "remark",
    "filename",
    "file_size",
    "upload_datetime",
    "correction_status",
    "download_request_url",
)


def crawler(parameter: dict[str, Any], endpoint: str, document_type: str) -> pd.DataFrame:
    logger.info(parameter)
    response = requests.post(
        f"https://mopsov.twse.com.tw/mops/web/ajax_{endpoint}",
        headers=request_headers(
            accept=HTML_ACCEPT,
            referer=f"https://mopsov.twse.com.tw/mops/web/{endpoint}",
            origin=STATEMENT_ORIGIN,
            content_type="application/x-www-form-urlencoded",
        ),
        data=electronic_book_form_data(parameter, endpoint),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    report_url = published_report_url(response.text)
    if not report_url:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    report_response = requests.get(
        report_url,
        headers=request_headers(accept=HTML_ACCEPT, referer=f"https://mopsov.twse.com.tw/mops/web/{endpoint}"),
    )
    html = report_response.content.decode("big5", errors="replace")
    return parse_electronic_book_html(html, document_type)


def electronic_book_form_data(parameter: dict[str, Any], endpoint: str) -> dict[str, Any]:
    form_data: dict[str, Any] = {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "ture",
        "off": "1",
        "TYPEK": parameter.get("kind", "all"),
        "keyword4": "",
        "code1": "",
        "TYPEK2": "",
        "checkbtn": "",
        "queryName": "co_id",
        "inpuType": "co_id",
        "co_id": parameter.get("stock_id"),
        "year": parameter.get("year"),
    }
    if endpoint == "t57sb01_q10":
        form_data.update(
            {
                "t05st29_c_ifrs": "N",
                "t05st30_c_ifrs": "N",
                "isnew": "true",
            }
        )
    return form_data


def parse_electronic_book_html(html: str, document_type: str) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    data_tables = [table for table in tables if has_filename_column(table)]
    if not data_tables:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result = data_tables[0].copy()
    result.columns = [normalize_column(column) for column in result.columns]
    result = result.rename(
        columns={
            "證券代號": "stock_id",
            "公司(證券)代號": "stock_id",
            "資料年度": "document_year",
            "資料類型": "detail_type",
            "結案類型": "case_type",
            "股東會性質": "meeting_type",
            "性質": "nature",
            "資料細節說明": "detail_description",
            "備註": "remark",
            "電子檔案": "filename",
            "檔案大小": "file_size",
            "上傳日期": "upload_datetime",
            "財務報告更(補)正": "correction_status",
            "永續專章更(補)正": "correction_status",
        }
    )
    for column in OUTPUT_COLUMNS:
        if column not in result.columns:
            result[column] = pd.NA
    result["document_type"] = document_type
    result["document_year"] = result["document_year"].map(clean_year)
    result["file_size"] = pd.to_numeric(
        result["file_size"].map(clean_number_text),
        errors="coerce",
    )
    result["download_request_url"] = result.apply(download_request_url, axis=1)
    for column in result.columns:
        if column in {"document_year", "file_size"}:
            continue
        result[column] = result[column].map(clean_text)
    return result[list(OUTPUT_COLUMNS)]


def has_filename_column(table: pd.DataFrame) -> bool:
    columns = {normalize_column(column) for column in table.columns}
    return "電子檔案" in columns


def published_report_url(html: str) -> str | None:
    match = re.search(r"window\.open\('([^']+)'", html)
    if not match:
        return None
    return match.group(1).replace("&amp;", "&")


def download_request_url(row: pd.Series) -> str | None:
    filename = clean_text(row.get("filename"))
    stock_id = clean_text(row.get("stock_id"))
    if not filename or not stock_id:
        return None
    kind = "A" if "_AI" in filename or "_AQ" in filename else None
    if kind is None:
        kind_match = re.search(r"([A-Z])\d*\.pdf$", filename)
        kind = kind_match.group(1) if kind_match else None
    if not kind:
        return None
    return f"{DOC_BASE_URL}?{urlencode({'step': 9, 'kind': kind, 'co_id': stock_id, 'filename': filename})}"


def normalize_column(column: Any) -> str:
    parts = column if isinstance(column, tuple) else (column,)
    cleaned = [
        re.sub(r"\s+", "", str(part).replace("\xa0", ""))
        for part in parts
        if part is not None and not str(part).startswith("Unnamed")
    ]
    return cleaned[-1] if cleaned else ""


def clean_year(value: Any) -> int | None:
    text = clean_text(value)
    if text is None:
        return None
    match = re.search(r"\d+", text)
    return int(match.group(0)) if match else None


def clean_number_text(value: Any) -> str | None:
    text = clean_text(value)
    if text is None or text in {"-", "--", "----", "------"}:
        return None
    return re.sub(r"[,%]", "", text)


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None
