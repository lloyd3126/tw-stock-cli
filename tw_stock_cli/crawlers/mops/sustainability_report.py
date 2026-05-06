"""Fetch MOPS sustainability report metadata and download links."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import JSON_ACCEPT
from tw_stock_cli.crawlers.common import request_headers


API_BASE_URL = "https://esggenplus.twse.com.tw/api/api/MopsSustainReport"
DATA_URL = f"{API_BASE_URL}/data"
OLD_DATA_URL = f"{API_BASE_URL}/data/old"
FILE_STREAM_URL = f"{API_BASE_URL}/data/FileStream"
REFERER_BASE_URL = "https://esggenplus.twse.com.tw/inquiry/report"
MOPS_REFERER = "https://mopsov.twse.com.tw/mops/web/t100sb11"
MOPS_DOWNLOAD_BASE_URL = "https://mopsov.twse.com.tw/server-java/FileDownLoad"

MARKET_TYPES = {
    "sii": 0,
    "otc": 1,
    "pub": 2,
    "rotc": 3,
}

OUTPUT_COLUMNS = (
    "market",
    "market_type",
    "report_year",
    "stock_id",
    "stock_name",
    "short_name",
    "english_name",
    "english_short_name",
    "industry",
    "reason",
    "reporting_interval",
    "compliance_notes",
    "assurance_provider",
    "assurance_standard",
    "accountant_assurance_provider",
    "accountant_assurance_standard",
    "accountant_assurance_type",
    "tw_report_url",
    "tw_report_download_url",
    "tw_report_upload_date",
    "tw_revised_report_download_url",
    "tw_revised_report_upload_date",
    "en_report_url",
    "en_report_download_url",
    "en_report_upload_date",
    "en_revised_report_download_url",
    "en_revised_report_upload_date",
    "contact_info",
    "note",
)


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    logger.info(parameter)
    payload = sustainability_report_payload(parameter)
    response = requests.post(
        DATA_URL,
        headers=sustainability_report_headers(payload),
        json=payload,
    )
    response.raise_for_status()
    body = response.json()
    rows = body.get("data") or []

    if not rows:
        old_response = requests.post(
            OLD_DATA_URL,
            headers=sustainability_report_headers(payload),
            json=payload,
        )
        old_response.raise_for_status()
        old_body = old_response.json()
        return normalize_sustainability_report_rows(
            old_body.get("data") or [],
            parameter,
            source="old",
        )

    return normalize_sustainability_report_rows(rows, parameter, source="new")


def sustainability_report_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    year = int(parameter.get("year"))
    roc_year = year - 1911 if year >= 1912 else year
    stock_id = parameter.get("stock_id") or ""
    return {
        "firstin": "true",
        "step": "1",
        "TYPEK": parameter.get("kind", "sii"),
        "kind": "",
        "id": "",
        "skind": parameter.get("industry_code", ""),
        "co_id": stock_id,
        "year": roc_year,
    }


def sustainability_report_payload(parameter: dict[str, Any]) -> dict[str, Any]:
    market = parameter.get("kind", "sii")
    stock_id = parameter.get("stock_id")
    return {
        "year": to_ad_year(int(parameter.get("year"))),
        "marketType": MARKET_TYPES.get(market, 0),
        "industryNameList": [],
        "companyCodeList": [str(stock_id)] if stock_id else [],
    }


def sustainability_report_headers(payload: dict[str, Any]) -> dict[str, str]:
    query = urlencode(
        {
            "market": payload["marketType"],
            "year": payload["year"],
        }
    )
    return request_headers(
        accept=JSON_ACCEPT,
        referer=f"{REFERER_BASE_URL}?{query}",
        origin="https://esggenplus.twse.com.tw",
        content_type="application/json",
    )


def normalize_sustainability_report_rows(
    rows: list[dict[str, Any]],
    parameter: dict[str, Any],
    *,
    source: str,
) -> pd.DataFrame:
    if source == "old":
        records = [normalize_old_row(row, parameter) for row in rows]
    else:
        records = [normalize_new_row(row, parameter) for row in rows]
    if not records:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    result = pd.DataFrame(records)
    for column in OUTPUT_COLUMNS:
        if column not in result.columns:
            result[column] = pd.NA
    for column in result.columns:
        if column in {"market_type", "report_year"}:
            continue
        result[column] = result[column].map(clean_text)
    return result[list(OUTPUT_COLUMNS)].reset_index(drop=True)


def normalize_new_row(row: dict[str, Any], parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": parameter.get("kind", "sii"),
        "market_type": MARKET_TYPES.get(parameter.get("kind", "sii"), 0),
        "report_year": to_ad_year(int(parameter.get("year"))),
        "stock_id": row.get("code"),
        "stock_name": row.get("name"),
        "short_name": row.get("shortName"),
        "english_name": row.get("enName"),
        "english_short_name": row.get("enShortName"),
        "industry": row.get("sector"),
        "reason": row.get("reason"),
        "reporting_interval": row.get("reportingInterval"),
        "compliance_notes": row.get("complianceNotes"),
        "assurance_provider": row.get("valiProvider"),
        "assurance_standard": row.get("thirdStd"),
        "accountant_assurance_provider": row.get("partnerOrganization"),
        "accountant_assurance_standard": row.get("stdCompliance"),
        "accountant_assurance_type": row.get("accOptionType"),
        "tw_report_url": row.get("twDocLink"),
        "tw_report_download_url": download_url(row.get("twFirstReportDownloadUrl"))
        or file_stream_url(row.get("twFirstReportDownloadId")),
        "tw_report_upload_date": row.get("twCommencementDate"),
        "tw_revised_report_download_url": download_url(row.get("twEditReportDownloadUrl"))
        or file_stream_url(row.get("twEditReportDownloadId")),
        "tw_revised_report_upload_date": row.get("twRevisionDate"),
        "en_report_url": row.get("enDocLink"),
        "en_report_download_url": download_url(row.get("enFirstReportDownloadUrl"))
        or file_stream_url(row.get("enFirstReportDownloadId")),
        "en_report_upload_date": row.get("enCommencementDate"),
        "en_revised_report_download_url": download_url(row.get("enEditReportDownloadUrl"))
        or file_stream_url(row.get("enEditReportDownloadId")),
        "en_revised_report_upload_date": row.get("enRevisionDate"),
        "contact_info": row.get("contactInfo"),
        "note": row.get("note"),
    }


def normalize_old_row(row: dict[str, Any], parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": parameter.get("kind", "sii"),
        "market_type": MARKET_TYPES.get(parameter.get("kind", "sii"), 0),
        "report_year": to_ad_year(int(parameter.get("year"))),
        "stock_id": row.get("companY_ID") or row.get("companyId") or row.get("code"),
        "stock_name": row.get("companY_ABBR_NAME") or row.get("name"),
        "short_name": row.get("companY_ABBR_NAME") or row.get("shortName"),
        "english_name": row.get("englisH_ABBR_NAME") or row.get("enName"),
        "english_short_name": row.get("englisH_ABBR_NAME") or row.get("enShortName"),
        "reason": row.get("sub") or row.get("reason"),
        "reporting_interval": old_reporting_interval(row),
        "compliance_notes": row.get("cS_A1") or row.get("complianceNotes"),
        "assurance_provider": row.get("surE_A") or row.get("valiProvider"),
        "assurance_standard": row.get("acC_S") or row.get("thirdStd"),
        "accountant_assurance_provider": row.get("acC_A")
        or row.get("partnerOrganization"),
        "accountant_assurance_standard": row.get("stdCompliance"),
        "accountant_assurance_type": row.get("accOptionType"),
        "tw_report_url": row.get("weB_INFO") or row.get("twDocLink"),
        "tw_report_download_url": old_file_download_url(
            row.get("filE_NAME") or row.get("twFirstReportDownloadId")
        ),
        "tw_report_upload_date": row.get("useR_DATE1") or row.get("twCommencementDate"),
        "tw_revised_report_download_url": old_file_download_url(
            row.get("filE_NAME2") or row.get("twEditReportDownloadId")
        ),
        "tw_revised_report_upload_date": row.get("useR_DATE2") or row.get("twRevisionDate"),
        "en_report_url": row.get("enG_WEB") or row.get("enDocLink"),
        "en_report_download_url": old_file_download_url(
            row.get("filE_ENAME") or row.get("enFirstReportDownloadId")
        ),
        "en_report_upload_date": row.get("useR_EDATE1") or row.get("enCommencementDate"),
        "en_revised_report_download_url": old_file_download_url(
            row.get("filE_ENAME2") or row.get("enEditReportDownloadId")
        ),
        "en_revised_report_upload_date": row.get("useR_EDATE2") or row.get("enRevisionDate"),
        "contact_info": row.get("contacT_INFO") or row.get("contactInfo"),
        "note": row.get("memo") or row.get("note"),
    }


def to_ad_year(year: int) -> int:
    return year + 1911 if year < 1912 else year


def file_stream_url(file_id: Any) -> str | None:
    text = clean_text(file_id)
    if not text or text == "00000000-0000-0000-0000-000000000000":
        return None
    return f"{FILE_STREAM_URL}?{urlencode({'id': text})}"


def old_file_download_url(filename: Any) -> str | None:
    text = clean_text(filename)
    if not text or text == "00000000-0000-0000-0000-000000000000":
        return None
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return f"{MOPS_DOWNLOAD_BASE_URL}?{urlencode({'step': 9, 'filePath': '/home/html/nas/protect/t100/', 'fileName': text})}"


def download_url(value: Any) -> str | None:
    text = clean_text(value)
    return text if text and text != "00000000-0000-0000-0000-000000000000" else None


def old_reporting_interval(row: dict[str, Any]) -> str | None:
    start = clean_text(row.get("duratioN_B"))
    end = clean_text(row.get("duratioN_E"))
    if start and end:
        return f"{start}~{end}"
    return row.get("reportingInterval")


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).replace("\xa0", " ").strip()
    return text or None
