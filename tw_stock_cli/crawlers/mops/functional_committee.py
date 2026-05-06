"""Fetch MOPS functional committee establishment and member summary."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t100sb03_1"
AUDIT_URL = "https://mopsov.twse.com.tw/mops/web/ajax_t135sb02"
REFERER = "https://mopsov.twse.com.tw/mops/web/t100sb03_1"
AUDIT_REFERER = "https://mopsov.twse.com.tw/mops/web/t135sb02"

COMMITTEE_LABELS = {
    "1": "非強制設置審計委員會",
    "2": "提名委員會",
    "3": "公司治理委員會",
    "4": "薪資報酬委員會",
    "5": "風險管理委員會",
    "6": "強制設置審計委員會",
    "7": "資訊安全委員會",
    "8": "永續發展委員會",
    "9": "誠信經營委員會",
    "10": "策略委員會",
    "11": "公司治理暨提名委員會",
    "12": "永續發展暨資訊安全委員會",
    "13": "永續經營暨風險管理委員會",
}

OUTPUT_COLUMNS = (
    "market",
    "committee_code",
    "committee_name",
    "stock_id",
    "stock_name",
    "established_date",
    "convener",
    "members",
    "expertise_members",
    "independent_director_count",
    "director_count",
    "operation_info",
)


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    logger.info(parameter)
    committee = str(parameter.get("committee") or "4")
    url = AUDIT_URL if committee == "6" else URL
    referer = AUDIT_REFERER if committee == "6" else REFERER
    response = requests.post(
        url,
        headers=request_headers(
            accept=HTML_ACCEPT,
            referer=referer,
            origin=STATEMENT_ORIGIN,
            content_type="application/x-www-form-urlencoded",
        ),
        data=functional_committee_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_functional_committee_html(response.text, parameter)


def functional_committee_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    committee = str(parameter.get("committee") or "4")
    return {
        "firstin": "true",
        "step": "1" if committee == "6" else "0",
        "TYPEK": parameter.get("kind", "sii"),
        "mod_no": committee,
    }


def parse_functional_committee_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    committee = str(parameter.get("committee") or "4")
    for table in tables:
        result = normalize_committee_table(table, committee, parameter)
        if not result.empty:
            return result
    return pd.DataFrame(columns=OUTPUT_COLUMNS)


def normalize_committee_table(
    table: pd.DataFrame,
    committee: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    width = 9 if committee == "6" else 7
    if len(table.columns) < width:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result = table.iloc[:, :width].copy()
    result.columns = (
        [
            "stock_id",
            "stock_name",
            "established_date",
            "convener",
            "members",
            "expertise_members",
            "independent_director_count",
            "director_count",
            "operation_info",
        ]
        if committee == "6"
        else [
            "stock_id",
            "stock_name",
            "established_date",
            "convener",
            "members",
            "expertise_members",
            "operation_info",
        ]
    )
    result = result[result["stock_id"].map(is_stock_id)].copy()
    if result.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result.insert(0, "committee_name", COMMITTEE_LABELS.get(committee, committee))
    result.insert(0, "committee_code", committee)
    result.insert(0, "market", parameter.get("kind", "sii"))
    for column in OUTPUT_COLUMNS:
        if column not in result.columns:
            result[column] = pd.NA
    for column in {"independent_director_count", "director_count"}:
        result[column] = pd.to_numeric(
            result[column].map(clean_number_text),
            errors="coerce",
        )
    for column in result.columns:
        if column in {"independent_director_count", "director_count"}:
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
