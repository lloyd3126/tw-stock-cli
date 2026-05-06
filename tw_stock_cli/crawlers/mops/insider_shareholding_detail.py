"""Fetch MOPS single-company insider shareholding detail tables."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import company_name_from_html
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_query6_1"
REFERER = "https://mopsov.twse.com.tw/mops/web/query6_1"

PREVIOUS_COLUMNS = (
    "elected_shares",
    "previous_month_held_shares",
    "previous_month_trust_shares",
    "previous_month_pledged_shares",
    "previous_month_private_shares",
)
INCREASE_COLUMNS = (
    "increase_centralized_shares",
    "increase_other_shares",
    "increase_private_shares",
    "increase_trust_shares",
    "increase_pledged_shares",
)
DECREASE_COLUMNS = (
    "decrease_centralized_shares",
    "decrease_other_shares",
    "decrease_private_shares",
    "decrease_trust_shares",
    "decrease_released_pledge_shares",
)
CURRENT_COLUMNS = (
    "current_held_shares",
    "current_custody_shares",
    "current_trust_shares",
    "current_pledged_shares",
    "current_private_shares",
)
OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "query_year",
    "query_month",
    "report_ym",
    "role",
    "person_name",
    "share_type",
    *PREVIOUS_COLUMNS,
    *INCREASE_COLUMNS,
    *DECREASE_COLUMNS,
    *CURRENT_COLUMNS,
    "role_notes",
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
        data=insider_shareholding_detail_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()
    return parse_insider_shareholding_detail_html(response.text, parameter)


def insider_shareholding_detail_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
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
        "isnew": "false",
        "co_id": parameter.get("stock_id"),
        "year": parameter.get("year"),
        "month": f"{int(parameter.get('month')):02d}",
    }


def parse_insider_shareholding_detail_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="hasBorder")
    if table is None:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    stock_id = str(parameter.get("stock_id"))
    stock_name = company_name_from_html(html)
    report_ym = report_ym_from_table(table) or (
        f"{int(parameter.get('year'))}{int(parameter.get('month')):02d}"
    )

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 7:
            continue
        role = clean_text(cell_text(cells[0]))
        if role in (None, "身份別"):
            continue

        record: dict[str, Any] = {
            "stock_id": stock_id,
            "stock_name": stock_name,
            "query_year": int(parameter.get("year")),
            "query_month": int(parameter.get("month")),
            "report_ym": report_ym,
            "role": role,
            "person_name": clean_text(cell_text(cells[1])),
            "share_type": clean_text(cell_text(cells[2])),
        }
        record.update(number_block(PREVIOUS_COLUMNS, cell_lines(cells[3])))
        record.update(number_block(INCREASE_COLUMNS, cell_lines(cells[4])))
        record.update(number_block(DECREASE_COLUMNS, cell_lines(cells[5])))

        current_lines = cell_lines(cells[6])
        record.update(number_block(CURRENT_COLUMNS, current_lines))
        record["role_notes"] = role_notes(current_lines)
        rows.append(record)

    if not rows:
        return pd.DataFrame()

    result = pd.DataFrame(rows)
    for column in [
        "query_year",
        "query_month",
        *PREVIOUS_COLUMNS,
        *INCREASE_COLUMNS,
        *DECREASE_COLUMNS,
        *CURRENT_COLUMNS,
    ]:
        result[column] = pd.to_numeric(result[column], errors="coerce").astype("Int64")
    return result[list(OUTPUT_COLUMNS)]


def report_ym_from_table(table: Any) -> str | None:
    first_header = table.find("th")
    if not first_header:
        return None
    match = re.search(r"資料年月：?\s*(\d{5})", cell_text(first_header))
    return match.group(1) if match else None


def number_block(columns: tuple[str, ...], lines: list[str]) -> dict[str, int | None]:
    values: dict[str, int | None] = {}
    for index, column in enumerate(columns):
        values[column] = parse_int(lines[index]) if index < len(lines) else None
    return values


def role_notes(lines: list[str]) -> str | None:
    notes: list[str] = []
    collecting = False
    for line in lines[5:]:
        if line.startswith("身份別備註"):
            collecting = True
            tail = line.split("：", 1)[-1].strip()
            if tail:
                notes.append(tail)
            continue
        if collecting and line:
            notes.append(line)
    return clean_text(" ".join(notes))


def cell_lines(cell: Any) -> list[str]:
    lines = cell.get_text("\n", strip=True).splitlines()
    return [
        clean
        for clean in (clean_text(part) for part in lines)
        if clean
    ]


def cell_text(cell: Any) -> str:
    return cell.get_text(" ", strip=True)


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None


def parse_int(value: Any) -> int | None:
    text = clean_text(value)
    if text is None:
        return None
    text = re.sub(r"[,\s]", "", text)
    if not text or text in {"-", "--"}:
        return None
    return int(text)
