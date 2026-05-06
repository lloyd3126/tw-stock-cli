"""Fetch MOPS investor conference tables."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlencode

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import html_tables
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t100sb02_1"
REFERER = "https://mopsov.twse.com.tw/mops/web/t100sb02_1"
DOWNLOAD_BASE_URL = "https://mopsov.twse.com.tw/server-java/FileDownLoad"

NORMALIZED_COLUMN_MAP = {
    "公司代號": "stock_id",
    "公司名稱": "stock_name",
    "召開法人說明會日期": "conference_date",
    "召開法人說明會時間": "conference_time",
    "召開法人說明會地點": "location",
    "法人說明會擇要訊息": "summary",
    "法人說明會簡報內容_中文檔案": "presentation_zh_file",
    "法人說明會簡報內容_英文檔案": "presentation_en_file",
    "公司網站是否提供法人說明會相關資訊": "company_ir_url",
    "影音連結資訊": "media_links",
    "其他應敘明事項": "notes",
    "歷年法人說明會": "historical_conferences",
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
        data=investor_conference_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()

    tables = [table for table in html_tables(response.text) if len(table.columns) >= 6]
    if not tables:
        return pd.DataFrame()
    return normalize_investor_conference_table(tables[-1], parameter)


def investor_conference_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "TYPEK": parameter.get("kind", "sii"),
        "year": parameter.get("year"),
        "month": month_value(parameter.get("month")),
        "co_id": parameter.get("stock_id") or "",
    }


def normalize_investor_conference_table(
    table: pd.DataFrame,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    result = table.copy()
    result.columns = investor_conference_columns(result.columns)
    result = result.rename(columns=investor_conference_column_name)
    if "stock_id" in result.columns:
        result["stock_id"] = result["stock_id"].astype(str)
    result.insert(0, "query_year", int(parameter.get("year")))
    result["presentation_zh_download_url"] = result.get(
        "presentation_zh_file",
        pd.Series(dtype=object),
    ).map(presentation_file_download_url)
    result["presentation_en_download_url"] = result.get(
        "presentation_en_file",
        pd.Series(dtype=object),
    ).map(presentation_file_download_url)
    return result


def investor_conference_columns(columns: pd.Index) -> list[str]:
    names = []
    for column in columns:
        parts = column if isinstance(column, tuple) else (column,)
        cleaned = [
            clean_header_part(str(part))
            for part in parts
            if part is not None and not str(part).startswith("Unnamed")
        ]
        deduped: list[str] = []
        for part in cleaned:
            if part and (not deduped or deduped[-1] != part):
                deduped.append(part)
        names.append("_".join(deduped))
    return names


def investor_conference_column_name(column: str) -> str:
    key = re.sub(r"\s+", "", column)
    return NORMALIZED_COLUMN_MAP.get(key, column)


def month_value(month: Any) -> str:
    return "all" if month in (None, "", "all") else str(int(month))


def clean_header_part(part: str) -> str:
    return re.sub(r"\s+", " ", part.replace("\xa0", " ")).strip()


def presentation_file_download_url(filename: Any) -> str | None:
    text = clean_text(filename)
    if not text or text in {"-", "--", "無", "nan"}:
        return None
    return f"{DOWNLOAD_BASE_URL}?{urlencode({'step': 9, 'filePath': '/home/html/nas/STR/', 'fileName': text, 'functionName': 't100sb02_1'})}"


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None
