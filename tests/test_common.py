from __future__ import annotations

import pandas as pd

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import JSON_ACCEPT
from tw_stock_cli.crawlers.common import compact_date
from tw_stock_cli.crawlers.common import flatten_column_names
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.common import roc_date
from tw_stock_cli.crawlers.common import select_and_rename_columns
from tw_stock_cli.crawlers.common import table_dataframe
from tw_stock_cli.crawlers.common import table_dataframe_by_field


def test_date_helpers_normalize_exchange_date_formats() -> None:
    assert compact_date("2026-04-30") == "20260430"
    assert roc_date("2026-04-30") == "115/04/30"
    assert roc_date("2026/04/30") == "115/04/30"


def test_request_headers_builds_stable_browser_headers() -> None:
    headers = request_headers(
        accept=JSON_ACCEPT,
        referer="https://example.test/source",
        origin="https://example.test",
        content_type="application/x-www-form-urlencoded",
        ajax=True,
        cache_control="no-cache",
        upgrade_insecure=True,
    )

    assert headers["Accept"] == JSON_ACCEPT
    assert headers["Referer"] == "https://example.test/source"
    assert headers["Origin"] == "https://example.test"
    assert headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert headers["X-Requested-With"] == "XMLHttpRequest"
    assert headers["Cache-Control"] == "no-cache"
    assert headers["Pragma"] == "no-cache"
    assert headers["Upgrade-Insecure-Requests"] == "1"
    assert "User-Agent" in headers


def test_request_headers_leaves_transport_headers_to_requests() -> None:
    headers = request_headers(accept=HTML_ACCEPT)

    assert "Accept-Encoding" not in headers
    assert "Connection" not in headers
    assert "Content-Length" not in headers
    assert "Host" not in headers


def test_table_dataframe_reads_modern_tables_shape() -> None:
    payload = {
        "tables": [
            {
                "fields": ["stock_id", "close"],
                "data": [["2330", "780"], ["2317", "155"]],
            }
        ]
    }

    frame = table_dataframe(payload)

    assert list(frame.columns) == ["stock_id", "close"]
    assert frame.to_dict("records") == [
        {"stock_id": "2330", "close": "780"},
        {"stock_id": "2317", "close": "155"},
    ]


def test_select_and_rename_columns_defines_output_contract() -> None:
    frame = pd.DataFrame(
        [
            {"證券代號": "2330", "證券名稱": "台積電", "收盤價": "780"},
        ]
    )

    result = select_and_rename_columns(
        frame,
        source_columns=["證券代號", "收盤價"],
        output_columns=["stock_id", "close"],
    )

    assert list(result.columns) == ["stock_id", "close"]
    assert result.iloc[0].to_dict() == {"stock_id": "2330", "close": "780"}


def test_select_and_rename_columns_rejects_mismatched_column_contracts() -> None:
    frame = pd.DataFrame([{"證券代號": "2330"}])

    try:
        select_and_rename_columns(
            frame,
            source_columns=["證券代號"],
            output_columns=["stock_id", "stock_name"],
        )
    except ValueError as exc:
        assert str(exc) == "source_columns and output_columns must have the same length"
    else:
        raise AssertionError("expected ValueError")


def test_flatten_column_names_normalizes_multiindex_columns() -> None:
    columns = [
        ("交易口數與契約金額", "多方", "口數"),
        ("Unnamed: 1_level_0", "商品 名稱"),
        "身份別",
    ]

    assert flatten_column_names(columns) == [
        "交易口數與契約金額_多方_口數",
        "商品 名稱",
        "身份別",
    ]


def test_table_dataframe_reads_legacy_data_shape() -> None:
    payload = {"fields": ["id", "name"], "data": [["1101", "台泥"]]}

    frame = table_dataframe(payload)

    assert list(frame.columns) == ["id", "name"]
    assert frame.iloc[0].to_dict() == {"id": "1101", "name": "台泥"}


def test_table_dataframe_by_field_selects_matching_table() -> None:
    payload = {
        "tables": [
            {"fields": ["日期", "指數"], "data": [["2026/04/30", "100"]]},
            {"fields": ["證券代號", "證券名稱"], "data": [["2330", "台積電"]]},
        ]
    }

    frame = table_dataframe_by_field(payload, "證券代號")

    assert list(frame.columns) == ["證券代號", "證券名稱"]
    assert frame.iloc[0].to_dict() == {"證券代號": "2330", "證券名稱": "台積電"}


def test_table_dataframe_returns_empty_frame_for_empty_payload() -> None:
    frame = table_dataframe({"tables": [{"fields": ["id"], "data": []}]})

    assert isinstance(frame, pd.DataFrame)
    assert frame.empty
