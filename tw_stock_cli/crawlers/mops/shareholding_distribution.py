"""Fetch MOPS shareholding distribution and shareholder structure tables."""

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
from tw_stock_cli.crawlers.mops.common import company_name_from_html
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t16sn02"
REFERER = "https://mopsov.twse.com.tw/mops/web/t16sn02"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "query_year",
    "data_date",
    "section",
    "sequence_no",
    "bucket_or_category",
    "holders",
    "shares",
    "holding_ratio",
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
        data=shareholding_distribution_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_shareholding_distribution_html(response.text, parameter)


def shareholding_distribution_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "ture",
        "off": "1",
        "keyword4": "",
        "code1": "",
        "TYPEK2": "",
        "checkbtn": "",
        "queryName": "co_id",
        "t05st29_c_ifrs": "N",
        "t05st30_c_ifrs": "N",
        "inpuType": "co_id",
        "TYPEK": parameter.get("kind", "all"),
        "isnew": "true",
        "co_id": parameter.get("stock_id"),
        "year": parameter.get("year"),
    }


def parse_shareholding_distribution_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html), header=None)
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    data_tables = [table for table in tables if len(table.columns) >= 5]
    if not data_tables:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    table = data_tables[0].iloc[:, :5].copy()
    stock_name = company_name_from_html(html)
    data_date = source_data_date(table)
    rows: list[dict[str, Any]] = []
    section: str | None = None
    for _, row in table.iterrows():
        label = clean_text(row.iloc[1])
        if label == "持股分級":
            section = "holding_distribution"
            continue
        if label == "股東結構類別":
            section = "shareholder_structure"
            continue
        if not section or not label or label == "股東結構":
            continue

        sequence_no = parse_number(row.iloc[0])
        holders = parse_number(row.iloc[2])
        shares = parse_number(row.iloc[3])
        ratio = parse_number(row.iloc[4])
        if sequence_no is None and holders is None and shares is None and ratio is None:
            continue

        rows.append(
            {
                "stock_id": str(parameter.get("stock_id")),
                "stock_name": stock_name,
                "market": parameter.get("kind", "all"),
                "query_year": int(parameter.get("year")),
                "data_date": data_date,
                "section": section,
                "sequence_no": sequence_no,
                "bucket_or_category": label.replace("合 計", "合計"),
                "holders": holders,
                "shares": shares,
                "holding_ratio": ratio,
            }
        )

    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def source_data_date(table: pd.DataFrame) -> str | None:
    for value in table.iloc[0].tolist():
        text = clean_text(value)
        if not text:
            continue
        match = re.search(r"資料日期[:：]\s*([0-9/]+)", text)
        if match:
            return match.group(1)
    return None


def parse_number(value: Any) -> float | int | None:
    text = clean_text(value)
    if text is None or text in {"-", "--", "----", "------"}:
        return None
    number = pd.to_numeric(re.sub(r"[,%]", "", text), errors="coerce")
    if pd.isna(number):
        return None
    if float(number).is_integer():
        return int(number)
    return float(number)


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None
