"""Fetch MOPS independent director profile summary."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t93sc01_1"
REFERER = "https://mopsov.twse.com.tw/mops/web/t93sc01_1"

OUTPUT_COLUMNS = (
    "market",
    "sequence_no",
    "stock_id",
    "stock_name",
    "role",
    "person_name",
    "appointment_date",
    "current_positions",
    "experience",
    "concurrent_company_name",
    "concurrent_role",
    "remark",
)

SOURCE_DATA_COLUMNS = (
    "sequence_no",
    "stock_id",
    "stock_name",
    "role",
    "person_name",
    "appointment_date",
    "current_positions",
    "experience",
    "concurrent_company_name",
    "concurrent_role",
    "remark",
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
        data=independent_director_profile_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_independent_director_profile_html(response.text, parameter)


def independent_director_profile_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": "1",
        "firstin": "ture",
        "off": "1",
        "TYPEK": parameter.get("kind", "sii"),
    }


def parse_independent_director_profile_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    data_tables = [
        table for table in tables if len(table.columns) >= len(SOURCE_DATA_COLUMNS)
    ]
    if not data_tables:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result = data_tables[0].iloc[:, : len(SOURCE_DATA_COLUMNS)].copy()
    result.columns = SOURCE_DATA_COLUMNS
    result = result[result["stock_id"].map(is_stock_id)].copy()
    result.insert(0, "market", parameter.get("kind", "sii"))
    result["sequence_no"] = pd.to_numeric(
        result["sequence_no"].map(clean_number_text),
        errors="coerce",
    )
    for column in result.columns:
        if column == "sequence_no":
            continue
        result[column] = result[column].map(clean_text)
    return result[list(OUTPUT_COLUMNS)].reset_index(drop=True)


def is_stock_id(value: Any) -> bool:
    text = clean_text(value)
    return bool(text and re.fullmatch(r"\d{4,6}", text))


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
