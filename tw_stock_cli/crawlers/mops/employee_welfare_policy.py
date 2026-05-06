"""Fetch MOPS employee welfare policy and rights protection disclosures."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t100sb12"
REFERER = "https://mopsov.twse.com.tw/mops/web/t100sb12"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "report_year",
    "disclosure_year",
    "section",
    "item",
    "value",
    "note",
)

SALARY_ADJUSTMENT_ITEMS = (
    "expected_salary_adjustment_ratio",
    "expected_salary_adjustment_note",
    "actual_salary_adjustment_ratio",
    "actual_salary_adjustment_note",
    "non_manager_salary_adjustment_ratio",
    "non_manager_salary_adjustment_note",
    "manager_salary_adjustment_ratio",
    "manager_salary_adjustment_note",
)

STARTING_SALARY_ITEMS = (
    "master_and_above_starting_salary",
    "college_starting_salary",
    "high_school_and_below_starting_salary",
    "starting_salary_note",
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
        data=employee_welfare_policy_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_employee_welfare_policy_html(response.text, parameter)


def employee_welfare_policy_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": "0",
        "firstin": "1",
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


def parse_employee_welfare_policy_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    context = employee_welfare_context(html, parameter)
    rows: list[dict[str, Any]] = []
    for table in tables:
        if is_policy_table(table):
            rows.extend(policy_rows(table, context))
        elif is_salary_adjustment_table(table):
            rows.extend(flat_table_rows(table, context, "salary_adjustment", SALARY_ADJUSTMENT_ITEMS))
        elif is_starting_salary_table(table):
            rows.extend(flat_table_rows(table, context, "starting_salary", STARTING_SALARY_ITEMS))

    if not rows:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    result = pd.DataFrame(rows)
    for column in OUTPUT_COLUMNS:
        if column not in result.columns:
            result[column] = pd.NA
    return result[list(OUTPUT_COLUMNS)].reset_index(drop=True)


def employee_welfare_context(html: str, parameter: dict[str, Any]) -> dict[str, Any]:
    report_year = int(parameter.get("year"))
    match = re.search(
        r"公司代號：\s*</b>\s*(?P<stock_id>\d+)\s*<b>公司名稱：\s*</b>\s*(?P<stock_name>[^<]+)\s*<b>申報年度：\s*</b>\s*(?P<year>\d+)",
        html,
    )
    disclosure_match = re.search(r"揭露\s*(\d+)\s*年度", html)
    return {
        "stock_id": match.group("stock_id") if match else parameter.get("stock_id"),
        "stock_name": clean_text(match.group("stock_name")) if match else None,
        "report_year": int(match.group("year")) if match else report_year,
        "disclosure_year": int(disclosure_match.group(1)) if disclosure_match else None,
    }


def is_policy_table(table: pd.DataFrame) -> bool:
    if len(table.columns) < 2 or table.empty:
        return False
    labels = {clean_label(value) for value in table.columns}
    if {"項目", "內容"}.issubset(labels):
        return True
    first_column = {clean_label(value) for value in table.iloc[:, 0].tolist()}
    return bool(
        {
            "員工福利政策",
            "員工權益維護措施",
            "勞資糾紛情形",
            "履行社會責任",
        }
        & first_column
    )


def is_salary_adjustment_table(table: pd.DataFrame) -> bool:
    text = table_text(table)
    return "預計調薪" in text and "非經理人" in text


def is_starting_salary_table(table: pd.DataFrame) -> bool:
    text = table_text(table)
    return "碩士及以上" in text and "大專校院" in text


def policy_rows(table: pd.DataFrame, context: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for _, row in table.iterrows():
        item = clean_label(row.iloc[0])
        value = clean_text(row.iloc[1]) if len(row) > 1 else None
        if item and value and item not in {"項目", "內容"}:
            rows.append(record(context, "policy", item, value))
    return rows


def flat_table_rows(
    table: pd.DataFrame,
    context: dict[str, Any],
    section: str,
    items: tuple[str, ...],
) -> list[dict[str, Any]]:
    values = table_value_row(table, len(items))
    if not values:
        return []
    return [
        record(context, section, item, clean_text(value))
        for item, value in zip(items, values)
        if clean_text(value)
    ]


def table_value_row(table: pd.DataFrame, width: int) -> list[Any]:
    if table.empty:
        return []
    for _, row in reversed(list(table.iterrows())):
        values = row.tolist()[:width]
        if is_header_value_row(values):
            continue
        if any(clean_text(value) for value in values):
            return values
    return []


def is_header_value_row(values: list[Any]) -> bool:
    labels = [clean_label(value) for value in values]
    labels = [label for label in labels if label]
    if not labels:
        return True
    title_terms = ("平均員工薪資調整情形", "新進員工之平均起薪金額")
    if any(term in label for term in title_terms for label in labels):
        return True
    header_terms = (
        "預計調薪",
        "實際調薪",
        "非經理人員工調薪",
        "經理人員工調薪",
        "碩士及以上",
        "大專校院",
        "高中及以下",
        "備註",
    )
    return all(any(term in label for term in header_terms) for label in labels)


def record(
    context: dict[str, Any],
    section: str,
    item: str,
    value: str | None,
    note: str | None = None,
) -> dict[str, Any]:
    return {
        **context,
        "section": section,
        "item": item,
        "value": value,
        "note": note,
    }


def table_text(table: pd.DataFrame) -> str:
    return "".join(clean_text(value) or "" for value in table.to_numpy().flatten())


def clean_label(value: Any) -> str | None:
    text = clean_text(value)
    return re.sub(r"\s+", "", text) if text else None


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None
