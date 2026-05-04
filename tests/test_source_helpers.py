from __future__ import annotations

from tw_stock_cli.crawlers.mops.common import has_no_data
from tw_stock_cli.crawlers.mops.common import statement_form_data
from tw_stock_cli.crawlers.mops.month_revenue import source_url
from tw_stock_cli.crawlers.taifex.common import market_download_headers
from tw_stock_cli.crawlers.taifex.common import market_form_data
from tw_stock_cli.crawlers.tpex.common import headers as tpex_headers
from tw_stock_cli.crawlers.twse.common import headers as twse_headers
from tw_stock_cli.crawlers.twse.common import is_no_data


def test_mops_statement_form_data_uses_source_parameter_names() -> None:
    form_data = statement_form_data({"kind": "otc", "year": 114, "quar": 4})

    assert form_data == {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "isQuery": "Y",
        "TYPEK": "otc",
        "year": 114,
        "season": "04",
    }


def test_mops_no_data_markers_match_source_error_pages() -> None:
    assert has_no_data("查無所需資料")
    assert has_no_data("資料庫中查無需求資料")
    assert not has_no_data("<table><tr><td>2330</td></tr></table>")


def test_mops_month_revenue_source_url_preserves_roc_year() -> None:
    assert (
        source_url("sii", 115, 3, 1)
        == "https://mopsov.twse.com.tw/nas/t21/sii/t21sc03_115_3_1.html"
    )


def test_taifex_market_form_data_uses_slash_dates() -> None:
    assert market_form_data("2026-04-30") == {
        "down_type": "1",
        "commodity_id": "all",
        "queryStartDate": "2026/04/30",
        "queryEndDate": "2026/04/30",
    }


def test_taifex_market_download_headers_include_form_context() -> None:
    headers = market_download_headers("https://www.taifex.com.tw/cht/3/futDailyMarketReport")

    assert headers["Origin"] == "https://www.taifex.com.tw"
    assert headers["Referer"] == "https://www.taifex.com.tw/cht/3/futDailyMarketReport"
    assert headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert "Content-Length" not in headers


def test_twse_and_tpex_json_headers_use_ajax_context() -> None:
    twse = twse_headers("https://www.twse.com.tw/example")
    tpex = tpex_headers("https://www.tpex.org.tw/example")

    assert twse["X-Requested-With"] == "XMLHttpRequest"
    assert tpex["X-Requested-With"] == "XMLHttpRequest"
    assert twse["Referer"] == "https://www.twse.com.tw/example"
    assert tpex["Referer"] == "https://www.tpex.org.tw/example"


def test_twse_no_data_statuses_are_detected() -> None:
    assert is_no_data({"stat": "很抱歉，沒有符合條件的資料!"})
    assert not is_no_data({"stat": "OK"})
