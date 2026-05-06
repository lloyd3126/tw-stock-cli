"""Shared parsing for MOPS fund lending and endorsement guarantee tables."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t65sb04"
REFERER = "https://mopsov.twse.com.tw/mops/web/t65sb04"

LENDING_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "report_year",
    "report_month",
    "sequence_no",
    "lender_name",
    "borrower_name",
    "is_related_party",
    "account_title",
    "max_balance_ytd",
    "subsidiary_business_increase_decrease",
    "subsidiary_short_term_financing_increase_decrease",
    "ending_balance",
    "actual_drawdown_amount",
    "interest_rate_range",
    "lending_nature",
    "business_transaction_amount",
    "short_term_financing_reason",
    "allowance_for_bad_debt",
    "collateral_name",
    "collateral_value",
    "individual_lending_limit",
    "total_lending_limit",
)

ENDORSEMENT_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "report_year",
    "report_month",
    "sequence_no",
    "guarantor_name",
    "guaranteed_party_name",
    "relationship",
    "individual_guarantee_limit",
    "max_balance_ytd",
    "subsidiary_increase_decrease",
    "ending_guarantee_balance",
    "actual_drawdown_amount",
    "collateralized_guarantee_amount",
    "net_worth_ratio",
    "total_guarantee_limit",
    "is_parent_to_subsidiary",
    "is_subsidiary_to_parent",
    "is_china_area_guarantee",
)

LENDING_COLUMN_MAP = {
    "編號(註2)": "sequence_no",
    "貸出資金之公司": "lender_name",
    "貸與對象": "borrower_name",
    "是否為關係人": "is_related_party",
    "往來科目(註3)": "account_title",
    "累計至本月止最高餘額(註4)": "max_balance_ytd",
    "個別子公司本月增(減)金額(註5)_因業務往來金額": (
        "subsidiary_business_increase_decrease"
    ),
    "個別子公司本月增(減)金額(註5)_短期融通資金": (
        "subsidiary_short_term_financing_increase_decrease"
    ),
    "期末餘額(註6)": "ending_balance",
    "實際動支金額(註7)": "actual_drawdown_amount",
    "利率區間": "interest_rate_range",
    "資金貸與性質(註8)": "lending_nature",
    "業務往來金額(註9)": "business_transaction_amount",
    "有短期融通資金必要之原因(註10)": "short_term_financing_reason",
    "提列備抵呆帳金額": "allowance_for_bad_debt",
    "擔保品_名稱": "collateral_name",
    "擔保品_價值": "collateral_value",
    "對個別對象資金貸與限額(註11)": "individual_lending_limit",
    "資金貸與總限額(註11)": "total_lending_limit",
}

ENDORSEMENT_COLUMN_MAP = {
    "編號(註2)": "sequence_no",
    "背書保證者公司名稱": "guarantor_name",
    "被背書保證對象_公司名稱": "guaranteed_party_name",
    "被背書保證對象_關係(註3)": "relationship",
    "對單一企業背書保證之限額(註4)": "individual_guarantee_limit",
    "累計至本月止最高餘額(註5)": "max_balance_ytd",
    "個別子公司本月增(減)金額(註6)": "subsidiary_increase_decrease",
    "期末背書保證餘額(註7)": "ending_guarantee_balance",
    "實際動支金額(註8)": "actual_drawdown_amount",
    "以財產擔保之背書保證金額(註9)": "collateralized_guarantee_amount",
    "累計背書保證金額佔最近期財務報表淨值之比率": "net_worth_ratio",
    "背書保證最高限額(註4)": "total_guarantee_limit",
    "屬母公司對子公司背書保證(註10)": "is_parent_to_subsidiary",
    "屬子公司對母公司背書保證(註10)": "is_subsidiary_to_parent",
    "屬對大陸地區背書保證(註10)": "is_china_area_guarantee",
}


def crawler(parameter: dict[str, Any], section: str) -> pd.DataFrame:
    logger.info(parameter)
    response = requests.post(
        URL,
        headers=request_headers(
            accept=HTML_ACCEPT,
            referer=REFERER,
            origin=STATEMENT_ORIGIN,
            content_type="application/x-www-form-urlencoded",
        ),
        data=lending_endorsement_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()
    if section == "lending":
        return parse_fund_lending_html(response.text, parameter)
    if section == "endorsement":
        return parse_endorsement_guarantee_html(response.text, parameter)
    raise ValueError(f"Unsupported section: {section}")


def lending_endorsement_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
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


def parse_fund_lending_html(html: str, parameter: dict[str, Any]) -> pd.DataFrame:
    table = section_table(html, "資金貸與資訊揭露明細表")
    if table is None:
        return pd.DataFrame(columns=LENDING_COLUMNS)
    result = normalize_table(table, LENDING_COLUMN_MAP)
    result = filter_detail_rows(result, "lender_name")
    return add_context(result, html, parameter, LENDING_COLUMNS)


def parse_endorsement_guarantee_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    table = section_table(html, "背書保證資訊揭露明細表")
    if table is None:
        return pd.DataFrame(columns=ENDORSEMENT_COLUMNS)
    result = normalize_table(table, ENDORSEMENT_COLUMN_MAP)
    result = filter_detail_rows(result, "guarantor_name")
    return add_context(result, html, parameter, ENDORSEMENT_COLUMNS)


def section_table(html: str, title: str) -> pd.DataFrame | None:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return None
    for index, table in enumerate(tables):
        text = " ".join(str(value) for value in table.to_numpy().ravel())
        if title in text:
            for candidate in tables[index + 1 :]:
                if len(candidate.columns) >= 10:
                    return candidate
    return None


def normalize_table(table: pd.DataFrame, column_map: dict[str, str]) -> pd.DataFrame:
    result = table.copy()
    result.columns = [column_map.get(flatten_column(column), "") for column in result.columns]
    result = result.loc[:, [bool(column) for column in result.columns]]
    return result


def flatten_column(column: Any) -> str:
    parts = column if isinstance(column, tuple) else (column,)
    cleaned = []
    for part in parts:
        text = normalize_key(part)
        if not text or text.startswith("Unnamed"):
            continue
        if text not in cleaned:
            cleaned.append(text)
    return "_".join(cleaned)


def normalize_key(value: Any) -> str:
    text = re.sub(r"\s+", "", str(value).replace("\xa0", " ")).strip()
    return text


def filter_detail_rows(frame: pd.DataFrame, name_column: str) -> pd.DataFrame:
    if frame.empty or name_column not in frame.columns:
        return frame
    invalid = {"小計", "各子公司合計", "備註", "合計"}
    result = frame[~frame[name_column].astype(str).isin(invalid)].copy()
    result = result[result[name_column].notna()]
    return result.reset_index(drop=True)


def add_context(
    frame: pd.DataFrame,
    html: str,
    parameter: dict[str, Any],
    columns: tuple[str, ...],
) -> pd.DataFrame:
    result = frame.copy()
    result.insert(0, "report_month", int(parameter.get("month")))
    result.insert(0, "report_year", int(parameter.get("year")))
    result.insert(0, "market", parameter.get("kind", "all"))
    result.insert(0, "stock_name", source_company_name(html))
    result.insert(0, "stock_id", str(parameter.get("stock_id")))
    for column in columns:
        if column not in result.columns:
            result[column] = pd.NA
    for column in result.columns:
        if column in {"stock_id", "stock_name", "market", "interest_rate_range"}:
            continue
        result[column] = coerce_numeric(result[column])
    return result[list(columns)]


def source_company_name(html: str) -> str | None:
    text = re.sub(r"\s+", " ", html)
    match = re.search(r"\((?:上市|上櫃)公司\)\s*([^<\s　]+)", text)
    return match.group(1) if match else None


def coerce_numeric(series: pd.Series) -> pd.Series:
    converted = pd.to_numeric(series, errors="coerce")
    return converted.where(converted.notna(), series)
