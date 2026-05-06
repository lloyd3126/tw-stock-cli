"""Fetch MOPS company governance organization structure summary."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t100sb01_1"
REFERER = "https://mopsov.twse.com.tw/mops/web/t100sb01_1"

OUTPUT_COLUMNS = (
    "market",
    "stock_id",
    "stock_name",
    "articles_board_seats",
    "articles_independent_director_seats",
    "articles_supervisor_seats",
    "director_term_start",
    "director_term_end",
    "vacant_director_seats",
    "vacant_independent_director_seats",
    "vacant_supervisor_seats",
    "board_seats",
    "independent_director_seats",
    "resident_director_required_ratio",
    "resident_director_actual_seats",
    "resident_director_actual_ratio",
    "audit_committee_status",
    "remuneration_committee_status",
    "legal_advisor",
    "shareholder_service_contact",
    "remark",
)

SOURCE_DATA_COLUMNS = (
    "stock_id",
    "stock_name",
    "articles_board_seats",
    "articles_independent_director_seats",
    "articles_supervisor_seats",
    "director_term_start",
    "director_term_end",
    "vacant_director_seats",
    "vacant_independent_director_seats",
    "vacant_supervisor_seats",
    "board_seats",
    "independent_director_seats",
    "resident_director_required_ratio",
    "resident_director_actual_seats",
    "resident_director_actual_ratio",
    "audit_committee_status",
    "remuneration_committee_status",
    "legal_advisor",
    "shareholder_service_contact",
    "remark",
)

NUMERIC_COLUMNS = {
    "articles_independent_director_seats",
    "articles_supervisor_seats",
    "vacant_director_seats",
    "vacant_independent_director_seats",
    "vacant_supervisor_seats",
    "board_seats",
    "independent_director_seats",
    "resident_director_actual_seats",
}

RATIO_COLUMNS = {
    "resident_director_required_ratio",
    "resident_director_actual_ratio",
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
        data=company_governance_structure_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_company_governance_structure_html(response.text, parameter)


def company_governance_structure_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    stock_id = parameter.get("stock_id") or ""
    return {
        "step": "1",
        "firstin": "ture",
        "off": "1",
        "keyword4": "",
        "code1": "",
        "TYPEK2": "",
        "checkbtn": "",
        "queryName": "",
        "inpuType": "co_id",
        "TYPEK": parameter.get("kind", "sii"),
        "co_id_1": stock_id,
        "co_id_2": stock_id,
    }


def parse_company_governance_structure_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html), header=[0, 1])
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    for table in tables:
        result = normalize_company_governance_structure_table(table, parameter)
        if not result.empty:
            return result
    return pd.DataFrame(columns=OUTPUT_COLUMNS)


def normalize_company_governance_structure_table(
    table: pd.DataFrame,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    if len(table.columns) < len(SOURCE_DATA_COLUMNS):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result = table.iloc[:, : len(SOURCE_DATA_COLUMNS)].copy()
    result.columns = list(SOURCE_DATA_COLUMNS)
    result = result[result["stock_id"].map(is_stock_id)].copy()
    if result.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result.insert(0, "market", parameter.get("kind", "sii"))
    for column in NUMERIC_COLUMNS | RATIO_COLUMNS:
        result[column] = pd.to_numeric(
            result[column].map(clean_number_text),
            errors="coerce",
        )
    for column in result.columns:
        if column in NUMERIC_COLUMNS or column in RATIO_COLUMNS:
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
