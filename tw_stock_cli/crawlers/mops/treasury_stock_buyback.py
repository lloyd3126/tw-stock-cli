"""Fetch MOPS treasury stock buyback basic information."""

from __future__ import annotations

import io
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


QUERY_URL = "https://mopsov.twse.com.tw/mops/web/ajax_t35sb01_q1"
DETAIL_URL = "https://mopsov.twse.com.tw/mops/web/ajax_t35sb01"
REFERER = "https://mopsov.twse.com.tw/mops/web/t35sb01_q1"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "buyback_no",
    "report_title",
    "report_date",
    "board_resolution_date",
    "buyback_purpose",
    "share_type",
    "issued_shares",
    "cumulative_held_shares",
    "cumulative_held_ratio",
    "planned_start_date",
    "planned_end_date",
    "planned_buyback_shares",
    "planned_buyback_ratio",
    "price_floor",
    "price_ceiling",
    "buyback_method",
    "detail_text",
)

EXTRA_COLUMNS = (
    "company_address",
    "below_average_transfer_shares",
    "below_average_transfer_ratio",
    "buyback_amount_limit",
    "previous_buyback_status",
    "incomplete_previous_buybacks",
    "board_resolution_minutes",
    "employee_transfer_rules",
    "capital_maintenance_statement",
    "price_rationality_opinion",
    "other_matters",
    "detail_available",
)


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    logger.info(parameter)
    query_response = requests.post(
        QUERY_URL,
        headers=mops_headers(REFERER),
        data=treasury_stock_buyback_query_form_data(parameter),
    )
    if has_no_data(query_response.text):
        return pd.DataFrame()

    query_form = auto_form_data(query_response.text)
    summary_html = query_response.text
    if query_form:
        summary_response = requests.post(
            DETAIL_URL,
            headers=mops_headers(REFERER),
            data=query_form,
        )
        if has_no_data(summary_response.text):
            return pd.DataFrame()
        summary_html = summary_response.text

    rows = parse_treasury_stock_buyback_list_html(summary_html, parameter)
    if rows.empty:
        return rows

    records: list[dict[str, Any]] = []
    for row in rows.to_dict("records"):
        if not row.get("detail_available"):
            records.append(row)
            continue
        detail_response = requests.post(
            DETAIL_URL,
            headers=mops_headers(REFERER),
            data=treasury_stock_buyback_detail_form_data(row),
        )
        detail = parse_treasury_stock_buyback_detail_html(
            detail_response.text,
            row,
        )
        records.append({**row, **detail})

    return pd.DataFrame(records, columns=(*OUTPUT_COLUMNS, *EXTRA_COLUMNS))


def treasury_stock_buyback_query_form_data(
    parameter: dict[str, Any],
) -> dict[str, Any]:
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
    }


def treasury_stock_buyback_detail_form_data(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "encodeURIComponent": "1",
        "step": "11",
        "TYPEK": row.get("market", "sii"),
        "buyno": row.get("buyback_no"),
        "co_id": row.get("stock_id"),
        "firstin": "true",
    }


def parse_treasury_stock_buyback_list_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    stock_name = company_name_from_html(html)
    rows: list[dict[str, Any]] = []
    for table in soup.find_all("table", class_="hasBorder"):
        headers = [clean_text(cell.get_text(" ", strip=True)) for cell in table.find_all("th")]
        if "第N次" not in headers:
            continue
        for source_row in table.find_all("tr"):
            cells = source_row.find_all("td")
            if len(cells) < 2:
                continue
            buyback_no = clean_text(cells[0].get_text(" ", strip=True))
            if not buyback_no or not buyback_no.isdigit():
                continue
            hidden = hidden_inputs(source_row)
            market = hidden.get("TYPEK") or parameter.get("kind", "all")
            rows.append(
                {
                    "stock_id": str(hidden.get("co_id") or parameter.get("stock_id")),
                    "stock_name": stock_name,
                    "market": market,
                    "buyback_no": int(buyback_no),
                    "board_resolution_date": clean_text(
                        cells[1].get_text(" ", strip=True)
                    ),
                    "detail_available": bool(hidden.get("buyno")),
                }
            )

    return pd.DataFrame(rows)


def parse_treasury_stock_buyback_detail_html(
    html: str,
    row: dict[str, Any],
) -> dict[str, Any]:
    if has_no_data(html):
        return {}
    try:
        tables = pd.read_html(io.StringIO(html), header=None)
    except (ImportError, ValueError):
        return {}
    if len(tables) < 2:
        return {}

    title_table = tables[0]
    field_table = tables[1]
    fields = key_value_fields(field_table)
    title_values = [clean_text(value) for value in title_table.iloc[:, 0].tolist()]
    title_values = [value for value in title_values if value]
    report_date = None
    for value in title_values:
        match = re.search(r"申報日期[:：]\s*([0-9/]+)", value)
        if match:
            report_date = match.group(1)

    period = fields.get("預定買回之期間")
    price_range = fields.get("買回區間價格(元)")

    return {
        "report_title": title_values[0] if title_values else None,
        "report_date": report_date,
        "stock_id": str(fields.get("公司代號") or row.get("stock_id")),
        "stock_name": fields.get("公司名稱") or row.get("stock_name"),
        "company_address": fields.get("公司地址"),
        "buyback_purpose": fields.get("買回股份目的"),
        "board_resolution_date": fields.get("董事會決議日期")
        or row.get("board_resolution_date"),
        "issued_shares": parse_int(fields.get("公司已發行股數總數(股)")),
        "cumulative_held_shares": parse_int(
            fields.get("申報時已持有本公司股份之累積股數(股)")
        ),
        "cumulative_held_ratio": parse_percent(
            fields.get("前項佔公司已發行股份總數比例(%)")
        ),
        "below_average_transfer_shares": parse_int(
            fields.get("申報時，低於買回股份平均價格轉讓予員工之累積股數(股)")
        ),
        "below_average_transfer_ratio": parse_percent(
            fields.get("前項佔公司已發行股份總數比例(%)")
        ),
        "share_type": fields.get("買回股份種類"),
        "buyback_amount_limit": fields.get("買回股數總金額上限(元)"),
        "planned_start_date": date_after("開始日期", period),
        "planned_end_date": date_after("結束日期", period),
        "planned_buyback_shares": parse_int(fields.get("預定買回之數量(股)")),
        "planned_buyback_ratio": parse_percent(
            fields.get("預定買回股份占公司已發行股份總數之比率(%) A/B")
        ),
        "price_floor": number_after("最低", price_range),
        "price_ceiling": number_after("最高", price_range),
        "buyback_method": fields.get("買回方式"),
        "previous_buyback_status": fields.get("申報前三年內買回公司股份之情形"),
        "incomplete_previous_buybacks": fields.get("已申報買回但未執行完畢之情形"),
        "board_resolution_minutes": fields.get("董事會決議買回股份之會議紀錄"),
        "employee_transfer_rules": fields.get(
            "「上市上櫃公司買回本公司股份辦法」第十條規定之轉讓辦法"
        ),
        "capital_maintenance_statement": fields.get(
            "董事會已考慮公司財務狀況，不影響公司資本維持之聲明"
        ),
        "price_rationality_opinion": fields.get(
            "會計師或證券承銷商對買回股份價格之合理性評估意見"
        ),
        "other_matters": fields.get("其他證期局所規定之事項"),
        "detail_text": " | ".join(
            f"{key}: {value}" for key, value in fields.items() if value
        ),
    }


def auto_form_data(html: str) -> dict[str, Any] | None:
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", {"name": "autoForm"})
    if form is None:
        return None
    data = hidden_inputs(form)
    data.pop("run", None)
    return data


def hidden_inputs(node: Any) -> dict[str, str]:
    data: dict[str, str] = {}
    for input_tag in node.find_all("input"):
        name = input_tag.get("name")
        if not name:
            continue
        data[name] = input_tag.get("value", "")
    return data


def key_value_fields(table: pd.DataFrame) -> dict[str, str]:
    fields: dict[str, str] = {}
    for _, source_row in table.iterrows():
        if len(source_row) < 3:
            continue
        key = clean_text(source_row.iloc[1])
        value = clean_text(source_row.iloc[2])
        if not key:
            continue
        if key in fields and value:
            fields[key] = f"{fields[key]} {value}".strip()
        else:
            fields[key] = value or ""
    return fields


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None


def parse_int(value: Any) -> int | None:
    text = clean_text(value)
    if not text:
        return None
    text = re.sub(r"[^0-9-]", "", text)
    return int(text) if text and text != "-" else None


def parse_percent(value: Any) -> float | None:
    text = clean_text(value)
    if not text:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    return float(match.group(0)) if match else None


def date_after(label: str, text: str | None) -> str | None:
    if not text:
        return None
    match = re.search(rf"{label}[:：]\s*([0-9/]+)", text)
    return match.group(1) if match else None


def number_after(label: str, text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(rf"{label}[:：]\s*(-?\d+(?:\.\d+)?)", text.replace(",", ""))
    return float(match.group(1)) if match else None


def mops_headers(referer: str) -> dict[str, str]:
    return request_headers(
        accept=HTML_ACCEPT,
        referer=referer,
        origin=STATEMENT_ORIGIN,
        content_type="application/x-www-form-urlencoded",
    )
