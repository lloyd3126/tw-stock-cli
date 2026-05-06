"""Shared helpers for MOPS crawler modules."""

import re
from typing import Any

import pandas as pd
import requests

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.common import html_tables
from tw_stock_cli.crawlers.common import rename_columns


STATEMENT_ORIGIN = "https://mopsov.twse.com.tw"

NO_DATA_MARKERS = (
    "之公司不存在！",
    "查無所需資料",
    "公司不繼續公開發行！",
    "資料庫中查無需求資料",
    "查詢無資料!",
)
STATEMENT_COLUMN_MAP = {
    0: "section",
    "0": "section",
    "公司 代號": "stock_id",
    "公司代號": "stock_id",
    "公司名稱": "stock_name",
}


def statement_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    """Build the form payload used by MOPS quarterly statement endpoints."""
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "isQuery": "Y",
        "TYPEK": parameter.get("kind", "sii"),
        "year": parameter.get("year", 111),
        "season": f"0{parameter.get('quar', 1)}",
    }


def company_statement_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    """Build the form payload used by MOPS single-company statement endpoints."""
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
        "TYPEK": parameter.get("kind", "all"),
        "co_id": parameter.get("stock_id"),
        "year": parameter.get("year"),
        "season": f"0{parameter.get('quar', 1)}",
    }


def has_no_data(response_text: str) -> bool:
    """Return whether a MOPS HTML response represents an empty result."""
    return not response_text or any(
        marker in response_text for marker in NO_DATA_MARKERS
    )


def fetch_statement_tables(
    url: str,
    referer: str,
    parameter: dict[str, Any],
) -> list[pd.DataFrame]:
    """Fetch and parse a MOPS quarterly statement into tables."""
    response = requests.post(
        url,
        headers=request_headers(
            referer=referer,
            origin=STATEMENT_ORIGIN,
            content_type="application/x-www-form-urlencoded",
        ),
        data=statement_form_data(parameter),
    )
    if has_no_data(response.text):
        return []
    return [normalize_statement_table(table) for table in html_tables(response.text)]


def fetch_company_statement_table(
    url: str,
    referer: str,
    parameter: dict[str, Any],
    statement: str,
) -> pd.DataFrame:
    """Fetch and parse a single-company MOPS financial statement table."""
    response = requests.post(
        url,
        headers=request_headers(
            accept=HTML_ACCEPT,
            referer=referer,
            origin=STATEMENT_ORIGIN,
            content_type="application/x-www-form-urlencoded",
        ),
        data=company_statement_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()

    tables = html_tables(response.text)
    statement_tables = [table for table in tables if len(table.columns) >= 2]
    if not statement_tables:
        return pd.DataFrame()

    return normalize_company_statement_table(
        statement_tables[-1],
        response.text,
        parameter,
        statement,
    )


def normalize_statement_table(table: pd.DataFrame) -> pd.DataFrame:
    """Normalize common MOPS statement identifier columns."""
    return rename_columns(table, STATEMENT_COLUMN_MAP)


def normalize_company_statement_table(
    table: pd.DataFrame,
    html: str,
    parameter: dict[str, Any],
    statement: str,
) -> pd.DataFrame:
    """Normalize a single-company MOPS statement into a row-per-account table."""
    result = table.copy()
    result.columns = company_statement_columns(result.columns)
    result = result.dropna(axis=1, how="all")
    result = result.loc[:, ~result.columns.str.startswith("unnamed_")]

    if "item" not in result.columns:
        first_column = result.columns[0]
        result = result.rename(columns={first_column: "item"})

    raw_items = result["item"].astype(str)
    result.insert(0, "statement", statement)
    result.insert(0, "quarter", int(parameter.get("quar")))
    result.insert(0, "report_year", int(parameter.get("year")))
    result.insert(0, "stock_name", company_name_from_html(html))
    result.insert(0, "stock_id", str(parameter.get("stock_id")))
    result.insert(
        6,
        "indent_level",
        raw_items.map(lambda item: len(item) - len(item.lstrip(" \u3000"))),
    )
    result["item"] = raw_items.map(clean_statement_item)

    return result


def company_statement_columns(columns: pd.Index) -> list[str]:
    """Flatten MOPS multi-row statement headers into stable column names."""
    names: list[str] = []
    seen: dict[str, int] = {}
    for index, column in enumerate(columns):
        parts = column if isinstance(column, tuple) else (column,)
        meaningful = [
            str(part).strip()
            for part in parts
            if part is not None
            and not str(part).startswith("Unnamed")
            and str(part).strip()
            and not str(part).startswith("民國")
            and not str(part).startswith("單位")
        ]

        if index == 0 or "會計項目" in meaningful:
            name = "item"
        elif not meaningful:
            name = f"unnamed_{index}"
        else:
            name = "_".join(
                column_label_part(part)
                for part in meaningful
                if part != "會計項目"
            )
            name = name or f"unnamed_{index}"

        count = seen.get(name, 0)
        seen[name] = count + 1
        if count:
            name = f"{name}_{count + 1}"
        names.append(name)

    return names


def column_label_part(part: str) -> str:
    """Convert common MOPS header fragments into CLI-friendly labels."""
    if part == "金額":
        return "amount"
    if part == "%":
        return "percent"
    return part


def clean_statement_item(item: str) -> str:
    """Trim MOPS account indentation and normalize whitespace."""
    return re.sub(r"\s+", " ", item.lstrip(" \u3000")).strip()


def company_name_from_html(html: str) -> str | None:
    """Extract company name from the MOPS single-company statement heading."""
    match = re.search(
        r"本資料由[\s\u3000]*(?:\([^)]*\)[\s\u3000]*)?([^<\s\u3000]+)[\s\u3000]*公司提供",
        html,
    )
    return match.group(1) if match else None
