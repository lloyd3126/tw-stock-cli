"""Fetch MOPS board attendance and director training details."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t93sc03_1"
REFERER = "https://mopsov.twse.com.tw/mops/web/t93sc03_1"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "section",
    "role",
    "person_name",
    "represented_company_name",
    "attendance_count",
    "proxy_attendance_count",
    "required_attendance_count",
    "attendance_ratio",
    "appointment_date",
    "first_appointment_date",
    "training_start_date",
    "training_end_date",
    "training_organizer",
    "course_name",
    "training_hours",
    "annual_training_hours",
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
        data=board_attendance_training_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_board_attendance_training_html(response.text, parameter)


def board_attendance_training_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": "2",
        "firstin": "ture",
        "TYPEK": parameter.get("kind", "sii"),
        "co_id": parameter.get("stock_id"),
    }


def parse_board_attendance_training_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    stock_id, stock_name = company_from_tables(tables, parameter)
    frames = [
        parse_attendance_table(table, stock_id, stock_name, parameter) for table in tables
    ]
    frames.extend(
        parse_training_table(table, stock_id, stock_name, parameter) for table in tables
    )
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return pd.concat(frames, ignore_index=True)[list(OUTPUT_COLUMNS)]


def parse_attendance_table(
    table: pd.DataFrame,
    stock_id: str | None,
    stock_name: str | None,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    result = table.copy()
    result.columns = [normalize_column(column) for column in result.columns]
    if "實際出(列)席次數(B)" not in result.columns:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result = result.rename(
        columns={
            "職稱": "role",
            "姓名(或代表人姓名)": "person_name",
            "所代表法人姓名": "represented_company_name",
            "實際出(列)席次數(B)": "attendance_count",
            "委託出席次數": "proxy_attendance_count",
            "應出(列)席次數(A)": "required_attendance_count",
            "實際出(列)席%(B/A)": "attendance_ratio",
            "備註": "remark",
        }
    )
    result = result[result["person_name"].map(clean_text).notna()].copy()
    return finalize_frame(result, "board_attendance", stock_id, stock_name, parameter)


def parse_training_table(
    table: pd.DataFrame,
    stock_id: str | None,
    stock_name: str | None,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    result = table.copy()
    result.columns = [normalize_column(column) for column in result.columns]
    if "課程名稱" not in result.columns:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result = result.rename(
        columns={
            "職稱": "role",
            "姓名": "person_name",
            "就任日期": "appointment_date",
            "初任日期": "first_appointment_date",
            "進修日期_起": "training_start_date",
            "進修日期_迄": "training_end_date",
            "主辦單位": "training_organizer",
            "課程名稱": "course_name",
            "進修時數": "training_hours",
            "當年度進修總時數": "annual_training_hours",
            "備註": "remark",
        }
    )
    result = result[result["person_name"].map(clean_text).notna()].copy()
    return finalize_frame(result, "director_training", stock_id, stock_name, parameter)


def finalize_frame(
    frame: pd.DataFrame,
    section: str,
    stock_id: str | None,
    stock_name: str | None,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    result = frame.copy()
    result["stock_id"] = stock_id or parameter.get("stock_id")
    result["stock_name"] = stock_name
    result["market"] = parameter.get("kind", "sii")
    result["section"] = section
    for column in OUTPUT_COLUMNS:
        if column not in result.columns:
            result[column] = pd.NA
    for column in {
        "attendance_count",
        "proxy_attendance_count",
        "required_attendance_count",
        "attendance_ratio",
        "training_hours",
        "annual_training_hours",
    }:
        result[column] = pd.to_numeric(
            result[column].map(clean_number_text),
            errors="coerce",
        )
    for column in result.columns:
        if column in {
            "attendance_count",
            "proxy_attendance_count",
            "required_attendance_count",
            "attendance_ratio",
            "training_hours",
            "annual_training_hours",
        }:
            continue
        result[column] = result[column].map(clean_text)
    return result[list(OUTPUT_COLUMNS)]


def company_from_tables(
    tables: list[pd.DataFrame],
    parameter: dict[str, Any],
) -> tuple[str | None, str | None]:
    text = " ".join(table.astype(str).to_string(index=False) for table in tables[:2])
    match = re.search(r"公司代號[:：]\s*(\d{4,6})\s+公司名稱[:：]\s*([^\s]+)", text)
    if match:
        return match.group(1), clean_text(match.group(2))
    return clean_text(parameter.get("stock_id")), None


def normalize_column(column: Any) -> str:
    parts = column if isinstance(column, tuple) else (column,)
    cleaned = [
        re.sub(r"\s+", "", str(part).replace("\xa0", ""))
        for part in parts
        if part is not None and not str(part).startswith("Unnamed")
    ]
    deduped: list[str] = []
    for part in cleaned:
        if not deduped or deduped[-1] != part:
            deduped.append(part)
    return "_".join(deduped)


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
