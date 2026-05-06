"""Dataset catalog and dispatch logic for the tw-stock CLI."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Literal

import pandas as pd


DatasetKind = Literal[
    "date",
    "none",
    "mops-month",
    "mops-quarter",
    "mops-company-quarter",
    "mops-company-year",
    "mops-basic-info",
    "mops-asset-acquisition-disposal",
    "mops-asset-acquisition-disposal-financial",
    "mops-annual-report-electronic-book",
    "mops-board-attendance-training",
    "mops-company-governance-structure",
    "mops-director-supervisor-remuneration",
    "mops-employee-benefit-expense",
    "mops-employee-welfare-policy",
    "mops-endorsement-guarantee",
    "mops-esg-company-disclosure",
    "mops-financial-report-electronic-book",
    "mops-fund-lending",
    "mops-full-time-employee-salary",
    "mops-functional-committee",
    "mops-independent-director-profile",
    "mops-insider-holding-company-list",
    "mops-insider-holding-detail",
    "mops-insider-shareholding-detail",
    "mops-ex-dividend",
    "mops-insider-pledge-ratio-summary",
    "mops-insider-pledge-summary",
    "mops-insider-shareholding-change",
    "mops-insider-transfer-detail",
    "mops-insider-transfer-summary",
    "mops-investor-conference",
    "mops-material-info",
    "mops-material-info-detail",
    "mops-major-shareholder-relationship",
    "mops-private-placement",
    "mops-manager-compensation-distribution",
    "mops-related-party-transaction-difference",
    "mops-related-party-transaction",
    "mops-related-company-reports",
    "mops-shareholding-distribution",
    "mops-shareholder-meeting",
    "mops-sustainability-report",
    "mops-treasury-stock-buyback",
]


@dataclass(frozen=True)
class Dataset:
    id: str
    title: str
    group: str
    description: str
    module: str
    kind: DatasetKind
    returns: tuple[str, ...]
    source_urls: tuple[str, ...]
    notes: str = ""

    def fetch(self, params: dict[str, Any]) -> pd.DataFrame | list[pd.DataFrame]:
        module = import_module(self.module)
        if self.kind == "date":
            date = require(params, "date")
            # Legacy price crawlers still accept their date inside a parameter dict.
            if self.id in {"twse.stock-price", "tpex.stock-price"}:
                return module.crawler({"crawler_date": date})
            return module.crawler(date)

        if self.kind == "none":
            return module.crawler()

        if self.kind == "mops-month":
            # MOPS endpoints use ROC years even when the CLI accepts AD years.
            year = normalize_roc_year(int(require(params, "year")))
            month = int(require(params, "month"))
            market = params.get("market", "sii")
            foreign = int(params.get("foreign", 0))
            return module.crawler(
                {
                    "kind": market,
                    "year": year,
                    "month": month,
                    "_type": market,
                    "foreign": foreign,
                }
            )

        if self.kind == "mops-quarter":
            # MOPS quarterly statement endpoints use ROC years.
            year = normalize_roc_year(int(require(params, "year")))
            quarter = int(require(params, "quarter"))
            market = params.get("market", "sii")
            return module.crawler({"kind": market, "year": year, "quar": quarter})

        if self.kind == "mops-company-quarter":
            year = normalize_roc_year(int(require(params, "year")))
            quarter = int(require(params, "quarter"))
            market = params.get("market", "all")
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": market,
                    "year": year,
                    "quar": quarter,
                }
            )

        if self.kind == "mops-company-year":
            year = normalize_roc_year(int(require(params, "year")))
            market = params.get("market", "all")
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": market,
                    "year": year,
                }
            )

        if self.kind == "mops-basic-info":
            return module.crawler(
                {
                    "stock_id": params.get("stock_id"),
                    "kind": params.get("market", "sii"),
                    "industry_code": params.get("industry_code"),
                }
            )

        if self.kind == "mops-treasury-stock-buyback":
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "all"),
                }
            )

        if self.kind == "mops-private-placement":
            return module.crawler(
                {
                    "stock_id": params.get("stock_id"),
                    "kind": params.get("market", "sii"),
                }
            )

        if self.kind in {
            "mops-asset-acquisition-disposal",
            "mops-asset-acquisition-disposal-financial",
            "mops-endorsement-guarantee",
            "mops-fund-lending",
            "mops-related-party-transaction",
        }:
            year = normalize_roc_year(int(require(params, "year")))
            month = int(require(params, "month"))
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "all"),
                    "year": year,
                    "month": month,
                }
            )

        if self.kind == "mops-related-party-transaction-difference":
            year = normalize_roc_year(int(require(params, "year")))
            quarter = int(require(params, "quarter"))
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "sii"),
                    "year": year,
                    "quar": quarter,
                }
            )

        if self.kind == "mops-director-supervisor-remuneration":
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "kind": params.get("market", "sii"),
                    "year": year,
                }
            )

        if self.kind in {
            "mops-financial-report-electronic-book",
            "mops-annual-report-electronic-book",
            "mops-related-company-reports",
        }:
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "all"),
                    "year": year,
                }
            )

        if self.kind == "mops-company-governance-structure":
            return module.crawler(
                {
                    "stock_id": params.get("stock_id"),
                    "kind": params.get("market", "sii"),
                }
            )

        if self.kind == "mops-sustainability-report":
            return module.crawler(
                {
                    "stock_id": params.get("stock_id"),
                    "kind": params.get("market", "sii"),
                    "year": int(require(params, "year")),
                }
            )

        if self.kind == "mops-major-shareholder-relationship":
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "stock_id": params.get("stock_id"),
                    "kind": params.get("market", "sii"),
                    "year": year,
                }
            )

        if self.kind in {
            "mops-employee-benefit-expense",
            "mops-full-time-employee-salary",
        }:
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "kind": params.get("market", "sii"),
                    "year": year,
                    "industry_code": params.get("industry_code"),
                }
            )

        if self.kind == "mops-employee-welfare-policy":
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "all"),
                    "year": year,
                }
            )

        if self.kind == "mops-esg-company-disclosure":
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "sii"),
                    "year": year,
                }
            )

        if self.kind == "mops-independent-director-profile":
            return module.crawler({"kind": params.get("market", "sii")})

        if self.kind == "mops-board-attendance-training":
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "sii"),
                }
            )

        if self.kind == "mops-functional-committee":
            return module.crawler(
                {
                    "kind": params.get("market", "sii"),
                    "committee": params.get("committee", "4"),
                }
            )

        if self.kind in {
            "mops-manager-compensation-distribution",
            "mops-shareholding-distribution",
        }:
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "all"),
                    "year": year,
                }
            )

        if self.kind == "mops-ex-dividend":
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "stock_id": params.get("stock_id"),
                    "kind": params.get("market", "sii"),
                    "year": year,
                    "month": params.get("month"),
                    "start_day": params.get("start_day"),
                    "end_day": params.get("end_day"),
                }
            )

        if self.kind == "mops-insider-shareholding-change":
            year = normalize_roc_year(int(require(params, "year")))
            month = int(require(params, "month"))
            return module.crawler(
                {
                    "kind": params.get("market", "sii"),
                    "year": year,
                    "month": month,
                }
            )

        if self.kind == "mops-insider-shareholding-detail":
            year = normalize_roc_year(int(require(params, "year")))
            month = int(require(params, "month"))
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "all"),
                    "year": year,
                    "month": month,
                }
            )

        if self.kind == "mops-insider-holding-company-list":
            year = normalize_roc_year(int(require(params, "year")))
            month = int(require(params, "month"))
            return module.crawler(
                {
                    "kind": params.get("market", "sii"),
                    "industry_code": params.get("industry_code"),
                    "year": year,
                    "month": month,
                }
            )

        if self.kind == "mops-insider-holding-detail":
            year = normalize_roc_year(int(require(params, "year")))
            month = int(require(params, "month"))
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "all"),
                    "year": year,
                    "month": month,
                }
            )

        if self.kind == "mops-insider-transfer-detail":
            year = normalize_roc_year(int(require(params, "year")))
            start_month, end_month = month_range(params)
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "all"),
                    "year": year,
                    "start_month": start_month,
                    "end_month": end_month,
                }
            )

        if self.kind == "mops-insider-transfer-summary":
            year = normalize_roc_year(int(require(params, "year")))
            start_month, end_month = month_range(params)
            return module.crawler(
                {
                    "kind": params.get("market", "sii"),
                    "year": year,
                    "start_month": start_month,
                    "end_month": end_month,
                }
            )

        if self.kind == "mops-insider-pledge-summary":
            year = normalize_roc_year(int(require(params, "year")))
            month = int(require(params, "month"))
            return module.crawler(
                {
                    "kind": params.get("market", "sii"),
                    "year": year,
                    "month": month,
                }
            )

        if self.kind == "mops-insider-pledge-ratio-summary":
            year = normalize_roc_year(int(require(params, "year")))
            month = int(require(params, "month"))
            return module.crawler(
                {
                    "kind": params.get("market", "sii"),
                    "year": year,
                    "month": month,
                }
            )

        if self.kind == "mops-investor-conference":
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "stock_id": params.get("stock_id"),
                    "kind": params.get("market", "sii"),
                    "year": year,
                    "month": params.get("month"),
                }
            )

        if self.kind == "mops-material-info":
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "stock_id": params.get("stock_id"),
                    "kind": params.get("market", "all"),
                    "year": year,
                    "month": params.get("month"),
                    "start_day": params.get("start_day"),
                    "end_day": params.get("end_day"),
                }
            )

        if self.kind == "mops-material-info-detail":
            return module.crawler(
                {
                    "stock_id": str(require(params, "stock_id")),
                    "kind": params.get("market", "all"),
                    "seq_no": str(require(params, "seq_no")),
                    "spoke_date": str(require(params, "spoke_date")),
                    "spoke_time": str(require(params, "spoke_time")),
                }
            )

        if self.kind == "mops-shareholder-meeting":
            year = normalize_roc_year(int(require(params, "year")))
            return module.crawler(
                {
                    "stock_id": params.get("stock_id"),
                    "kind": params.get("market", "sii"),
                    "year": year,
                    "month": params.get("month"),
                    "start_day": params.get("start_day"),
                    "end_day": params.get("end_day"),
                }
            )

        raise ValueError(f"Unsupported dataset kind: {self.kind}")


def require(params: dict[str, Any], key: str) -> Any:
    value = params.get(key)
    if value in (None, ""):
        raise ValueError(f"Missing required parameter: {key}")
    return value


def normalize_roc_year(year: int) -> int:
    return year - 1911 if year >= 1912 else year


def month_range(params: dict[str, Any]) -> tuple[int, int]:
    if params.get("month") not in (None, ""):
        month = int(params["month"])
        return month, month
    start_month = int(params.get("start_month") or 1)
    end_month = int(params.get("end_month") or start_month or 12)
    if params.get("end_month") in (None, "") and params.get("start_month") in (None, ""):
        end_month = 12
    return start_month, end_month


DATASETS: dict[str, Dataset] = {
    "twse.stock-price": Dataset(
        id="twse.stock-price",
        title="上市股票每日收盤價",
        group="twse",
        description="Daily close quotes for TWSE listed securities, including open, high, low, and close.",
        module="tw_stock_cli.crawlers.twse.stock_price",
        kind="date",
        returns=("stock_id", "stock_name", "open", "high", "low", "close", "date"),
        source_urls=("https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX",),
    ),
    "twse.stock-list": Dataset(
        id="twse.stock-list",
        title="上市股票清單",
        group="twse",
        description="TWSE listed security codes and names for a trading date.",
        module="tw_stock_cli.crawlers.twse.stock_list",
        kind="date",
        returns=("stock_id", "stock_name", "date"),
        source_urls=("https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX",),
    ),
    "twse.stock-per": Dataset(
        id="twse.stock-per",
        title="上市本益比與殖利率",
        group="twse",
        description="TWSE PER, dividend yield, and price-to-book ratio by security.",
        module="tw_stock_cli.crawlers.twse.stock_valuation",
        kind="date",
        returns=(
            "stock_id",
            "stock_name",
            "close",
            "dividend_yield",
            "dividend_year",
            "per",
            "pbr",
            "financial_report_period",
            "date",
        ),
        source_urls=("https://www.twse.com.tw/exchangeReport/BWIBBU_d",),
    ),
    "twse.institutional-trade": Dataset(
        id="twse.institutional-trade",
        title="上市三大法人買賣超",
        group="twse",
        description="TWSE daily institutional investor buy/sell details.",
        module="tw_stock_cli.crawlers.twse.institutional_trade",
        kind="date",
        returns=("stock_id", "stock_name", "institutional_net_buy"),
        source_urls=("https://www.twse.com.tw/fund/T86",),
    ),
    "twse.margin-trade": Dataset(
        id="twse.margin-trade",
        title="上市融資融券餘額",
        group="twse",
        description="TWSE margin purchase and short sale balances.",
        module="tw_stock_cli.crawlers.twse.margin_trade",
        kind="date",
        returns=("stock_id", "stock_name", "margin_purchase_balance", "short_sale_balance"),
        source_urls=("https://www.twse.com.tw/exchangeReport/MI_MARGN",),
    ),
    "twse.foreign-holding": Dataset(
        id="twse.foreign-holding",
        title="上市外資及陸資持股",
        group="twse",
        description="Foreign and mainland China investor holding statistics for TWSE listed securities.",
        module="tw_stock_cli.crawlers.twse.foreign_holding",
        kind="date",
        returns=(
            "stock_id",
            "stock_name",
            "issued_shares",
            "foreign_held_shares",
            "foreign_held_ratio",
        ),
        source_urls=("https://www.twse.com.tw/fund/MI_QFIIS",),
    ),
    "twse.total-return-index": Dataset(
        id="twse.total-return-index",
        title="發行量加權股價報酬指數",
        group="twse",
        description="TWSE total return index values for the month containing the requested date.",
        module="tw_stock_cli.crawlers.twse.total_return_index",
        kind="date",
        returns=("date", "total_return_index"),
        source_urls=("https://www.twse.com.tw/indicesReport/MFI94U",),
    ),
    "tpex.stock-price": Dataset(
        id="tpex.stock-price",
        title="上櫃股票每日收盤價",
        group="tpex",
        description="Daily close quotes for TPEx securities, including open, high, low, and close.",
        module="tw_stock_cli.crawlers.tpex.stock_price",
        kind="date",
        returns=("stock_id", "stock_name", "close", "open", "high", "low", "date"),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php",
        ),
    ),
    "tpex.stock-list": Dataset(
        id="tpex.stock-list",
        title="上櫃股票清單",
        group="tpex",
        description="TPEx security list and daily quote columns by industry category.",
        module="tw_stock_cli.crawlers.tpex.stock_list",
        kind="date",
        returns=("stock_id", "stock_name", "industry_category", "date"),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php",
        ),
    ),
    "tpex.stock-per": Dataset(
        id="tpex.stock-per",
        title="上櫃本益比與殖利率",
        group="tpex",
        description="TPEx PER, dividend yield, and price-to-book ratio by security.",
        module="tw_stock_cli.crawlers.tpex.stock_valuation",
        kind="date",
        returns=(
            "stock_id",
            "stock_name",
            "per",
            "dividend_per_share",
            "dividend_year",
            "dividend_yield",
            "pbr",
            "date",
        ),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_result.php",
        ),
    ),
    "tpex.institutional-trade": Dataset(
        id="tpex.institutional-trade",
        title="上櫃三大法人買賣超",
        group="tpex",
        description="TPEx daily institutional investor buy/sell details.",
        module="tw_stock_cli.crawlers.tpex.institutional_trade",
        kind="date",
        returns=("stock_id", "stock_name", "institutional_net_buy"),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php",
        ),
    ),
    "tpex.margin-trade": Dataset(
        id="tpex.margin-trade",
        title="上櫃融資融券餘額",
        group="tpex",
        description="TPEx margin purchase and short sale balances.",
        module="tw_stock_cli.crawlers.tpex.margin_trade",
        kind="date",
        returns=("stock_id", "stock_name", "margin_purchase_balance", "short_sale_balance"),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal_result.php",
        ),
    ),
    "tpex.foreign-holding": Dataset(
        id="tpex.foreign-holding",
        title="上櫃外資持股比例",
        group="tpex",
        description="TPEx foreign investor holding ratio ranking.",
        module="tw_stock_cli.crawlers.tpex.foreign_holding",
        kind="date",
        returns=(
            "rank",
            "stock_id",
            "stock_name",
            "foreign_held_shares",
            "foreign_held_ratio",
        ),
        source_urls=("https://www.tpex.org.tw/web/stock/3insti/qfii/qfii_result.php",),
    ),
    "tpex.total-return-index": Dataset(
        id="tpex.total-return-index",
        title="櫃買指數與報酬指數",
        group="tpex",
        description="TPEx index and total return index values for the month containing the requested date.",
        module="tw_stock_cli.crawlers.tpex.total_return_index",
        kind="date",
        returns=("date", "index", "total_return_index"),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/iNdex_info/reward_index/ROE_result.php",
        ),
    ),
    "taifex.futures-daily": Dataset(
        id="taifex.futures-daily",
        title="期貨每日交易行情",
        group="taifex",
        description="TAIFEX daily futures market data.",
        module="tw_stock_cli.crawlers.taifex.futures_daily",
        kind="date",
        returns=(
            "trade_date",
            "contract",
            "expiry_month_week",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ),
        source_urls=("https://www.taifex.com.tw/cht/3/dlFutDataDown",),
    ),
    "taifex.options-daily": Dataset(
        id="taifex.options-daily",
        title="選擇權每日交易行情",
        group="taifex",
        description="TAIFEX daily options market data.",
        module="tw_stock_cli.crawlers.taifex.options_daily",
        kind="date",
        returns=(
            "trade_date",
            "contract",
            "expiry_month_week",
            "strike_price",
            "call_put",
            "close",
            "volume",
        ),
        source_urls=("https://www.taifex.com.tw/cht/3/dlOptDataDown",),
    ),
    "taifex.futures-tick": Dataset(
        id="taifex.futures-tick",
        title="期貨逐筆成交",
        group="taifex",
        description="TAIFEX futures tick data. This can be very large.",
        module="tw_stock_cli.crawlers.taifex.futures_tick",
        kind="date",
        returns=(
            "trade_date",
            "contract",
            "expiry_month_week",
            "trade_time",
            "trade_price",
            "trade_volume",
        ),
        source_urls=(
            "https://www.taifex.com.tw/file/taifex/Dailydownload/DailydownloadCSV/",
        ),
        notes="Large dataset. Use --limit for exploration.",
    ),
    "taifex.options-tick": Dataset(
        id="taifex.options-tick",
        title="選擇權逐筆成交",
        group="taifex",
        description="TAIFEX options tick data. This can be very large.",
        module="tw_stock_cli.crawlers.taifex.options_tick",
        kind="date",
        returns=(
            "trade_date",
            "contract",
            "strike_price",
            "expiry_month_week",
            "call_put",
            "trade_time",
            "trade_price",
        ),
        source_urls=(
            "https://www.taifex.com.tw/file/taifex/Dailydownload/OptionsDailydownloadCSV/",
        ),
        notes="Large dataset. Use --limit for exploration.",
    ),
    "taifex.futures-institutional": Dataset(
        id="taifex.futures-institutional",
        title="期貨三大法人未平倉",
        group="taifex",
        description="TAIFEX futures institutional investor positions and open interest.",
        module="tw_stock_cli.crawlers.taifex.futures_institutional",
        kind="date",
        returns=(
            "row_number",
            "contract_name",
            "investor_type",
            "trade_long_volume",
            "open_interest_long_volume",
        ),
        source_urls=("https://www.taifex.com.tw/cht/3/futContractsDate",),
    ),
    "taifex.fcm-futures-volume-day": Dataset(
        id="taifex.fcm-futures-volume-day",
        title="期貨商期貨成交量日盤",
        group="taifex",
        description="TAIFEX futures commission merchant futures trading volume, regular session.",
        module="tw_stock_cli.crawlers.taifex.fcm_futures_volume_day",
        kind="none",
        returns=("fcm_id", "fcm_name", "subtotal"),
        source_urls=(
            "https://www.taifex.com.tw/cht/7/getFCMFile?filename=Daily_FUT_day.csv",
        ),
    ),
    "taifex.fcm-futures-volume-night": Dataset(
        id="taifex.fcm-futures-volume-night",
        title="期貨商期貨成交量夜盤",
        group="taifex",
        description="TAIFEX futures commission merchant futures trading volume, night session.",
        module="tw_stock_cli.crawlers.taifex.fcm_futures_volume_night",
        kind="none",
        returns=("fcm_id", "fcm_name", "total", "market_share"),
        source_urls=(
            "https://www.taifex.com.tw/cht/7/getFCMFile?filename=Daily_FUT_night.csv",
        ),
    ),
    "taifex.fcm-options-volume-day": Dataset(
        id="taifex.fcm-options-volume-day",
        title="期貨商選擇權成交量日盤",
        group="taifex",
        description="TAIFEX futures commission merchant options trading volume, regular session.",
        module="tw_stock_cli.crawlers.taifex.fcm_options_volume_day",
        kind="none",
        returns=("fcm_id", "fcm_name", "total", "market_share"),
        source_urls=(
            "https://www.taifex.com.tw/cht/7/getFCMFile?filename=Daily_OPT_day.csv",
        ),
    ),
    "taifex.fcm-options-volume-night": Dataset(
        id="taifex.fcm-options-volume-night",
        title="期貨商選擇權成交量夜盤",
        group="taifex",
        description="TAIFEX futures commission merchant options trading volume, night session.",
        module="tw_stock_cli.crawlers.taifex.fcm_options_volume_night",
        kind="none",
        returns=("fcm_id", "fcm_name", "total", "market_share"),
        source_urls=(
            "https://www.taifex.com.tw/cht/7/getFCMFile?filename=Daily_OPT_night.csv",
        ),
    ),
    "mops.month-revenue": Dataset(
        id="mops.month-revenue",
        title="月營收",
        group="mops",
        description="MOPS monthly revenue by company.",
        module="tw_stock_cli.crawlers.mops.month_revenue",
        kind="mops-month",
        returns=("stock_id", "revenue", "revenue_year", "revenue_month"),
        source_urls=("https://mopsov.twse.com.tw/nas/t21/",),
    ),
    "mops.income-statement": Dataset(
        id="mops.income-statement",
        title="綜合損益表",
        group="mops",
        description="MOPS quarterly income statement summary tables.",
        module="tw_stock_cli.crawlers.mops.income_statement",
        kind="mops-quarter",
        returns=("multiple tables",),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t163sb04",),
    ),
    "mops.balance-sheet": Dataset(
        id="mops.balance-sheet",
        title="資產負債表",
        group="mops",
        description="MOPS quarterly balance sheet summary tables.",
        module="tw_stock_cli.crawlers.mops.balance_sheet",
        kind="mops-quarter",
        returns=("multiple tables",),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t163sb05",),
    ),
    "mops.cash-flow": Dataset(
        id="mops.cash-flow",
        title="現金流量表",
        group="mops",
        description="MOPS quarterly cash flow summary tables.",
        module="tw_stock_cli.crawlers.mops.cash_flow",
        kind="mops-quarter",
        returns=("multiple tables",),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t163sb20",),
    ),
    "mops.company-balance-sheet": Dataset(
        id="mops.company-balance-sheet",
        title="個別公司資產負債表",
        group="mops",
        description="Detailed single-company MOPS balance sheet parsed from the company financial statement page.",
        module="tw_stock_cli.crawlers.mops.company_balance_sheet",
        kind="mops-company-quarter",
        returns=(
            "stock_id",
            "stock_name",
            "report_year",
            "quarter",
            "statement",
            "item",
            "dynamic period columns",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t164sb03",),
        notes="Single-company detailed statement. Dynamic columns depend on the requested period.",
    ),
    "mops.company-income-statement": Dataset(
        id="mops.company-income-statement",
        title="個別公司綜合損益表",
        group="mops",
        description="Detailed single-company MOPS income statement parsed from the company financial statement page.",
        module="tw_stock_cli.crawlers.mops.company_income_statement",
        kind="mops-company-quarter",
        returns=(
            "stock_id",
            "stock_name",
            "report_year",
            "quarter",
            "statement",
            "item",
            "dynamic period columns",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t164sb04",),
        notes="Single-company detailed statement. Dynamic columns depend on the requested period.",
    ),
    "mops.company-cash-flow": Dataset(
        id="mops.company-cash-flow",
        title="個別公司現金流量表",
        group="mops",
        description="Detailed single-company MOPS cash flow statement parsed from the company financial statement page.",
        module="tw_stock_cli.crawlers.mops.company_cash_flow",
        kind="mops-company-quarter",
        returns=(
            "stock_id",
            "stock_name",
            "report_year",
            "quarter",
            "statement",
            "item",
            "dynamic period columns",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t164sb05",),
        notes="Includes cash flow line items such as PPE and intangible asset acquisitions when disclosed by MOPS.",
    ),
    "mops.company-equity-changes": Dataset(
        id="mops.company-equity-changes",
        title="個別公司權益變動表",
        group="mops",
        description="Detailed single-company MOPS statement of changes in equity parsed from the company financial statement page.",
        module="tw_stock_cli.crawlers.mops.company_equity_changes",
        kind="mops-company-quarter",
        returns=(
            "stock_id",
            "stock_name",
            "report_year",
            "quarter",
            "statement_year",
            "item",
            "equity columns",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t164sb06",),
        notes="Returns one table per statement year when MOPS includes comparative years.",
    ),
    "mops.company-basic-info": Dataset(
        id="mops.company-basic-info",
        title="公司基本資料",
        group="mops",
        description="MOPS company basic information by market and optional industry or stock ID filter.",
        module="tw_stock_cli.crawlers.mops.company_basic_info",
        kind="mops-basic-info",
        returns=(
            "stock_id",
            "stock_name",
            "short_name",
            "industry",
            "chairman",
            "general_manager",
            "spokesperson",
            "paid_in_capital",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t51sb01",),
        notes="Use --market and optionally --industry-code or --stock-id to filter.",
    ),
    "mops.treasury-stock-buyback": Dataset(
        id="mops.treasury-stock-buyback",
        title="庫藏股買回基本資料",
        group="mops",
        description="MOPS single-company treasury stock buyback basic information and detail text.",
        module="tw_stock_cli.crawlers.mops.treasury_stock_buyback",
        kind="mops-treasury-stock-buyback",
        returns=(
            "stock_id",
            "stock_name",
            "buyback_no",
            "report_date",
            "board_resolution_date",
            "buyback_purpose",
            "share_type",
            "planned_buyback_shares",
            "planned_start_date",
            "planned_end_date",
            "price_floor",
            "price_ceiling",
            "buyback_method",
            "detail_text",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_t35sb01_q1",
            "https://mopsov.twse.com.tw/mops/web/ajax_t35sb01",
        ),
        notes="MOPS first returns a company-specific list; this crawler follows each buyback detail form.",
    ),
    "mops.private-placement": Dataset(
        id="mops.private-placement",
        title="私募有價證券資料",
        group="mops",
        description="MOPS private placement securities summary by market and optional company.",
        module="tw_stock_cli.crawlers.mops.private_placement",
        kind="mops-private-placement",
        returns=(
            "stock_id",
            "stock_name",
            "market",
            "security_type",
            "decision_date",
            "year_period",
            "pricing_detail_available",
            "payment_detail_available",
            "fund_utilization_periods",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t116sb01",),
        notes="Detail buttons are represented by availability flags and source report keys.",
    ),
    "mops.asset-acquisition-disposal": Dataset(
        id="mops.asset-acquisition-disposal",
        title="月取得或處分資產資訊",
        group="mops",
        description="MOPS monthly asset acquisition or disposal information by single company.",
        module="tw_stock_cli.crawlers.mops.asset_acquisition_disposal",
        kind="mops-asset-acquisition-disposal",
        returns=(
            "stock_id",
            "stock_name",
            "market",
            "report_year",
            "report_month",
            "detail_available",
            "detail_text",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_t12sc01_q2",
            "https://mopsov.twse.com.tw/mops/web/ajax_t12sc01",
        ),
        notes="MOPS uses an auto form before the final t12sc01 report; this crawler follows that form.",
    ),
    "mops.asset-acquisition-disposal-financial": Dataset(
        id="mops.asset-acquisition-disposal-financial",
        title="取得或處分資產財務資料表",
        group="mops",
        description="MOPS financial information table related to asset acquisition/disposal monthly reporting.",
        module="tw_stock_cli.crawlers.mops.asset_acquisition_disposal_financial",
        kind="mops-asset-acquisition-disposal-financial",
        returns=(
            "stock_id",
            "stock_name",
            "report_year",
            "report_month",
            "financial_assets_total",
            "total_assets_ratio",
            "equity_ratio",
            "working_capital",
            "pledged_securities_market_value",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_t12sc01_q3",
            "https://mopsov.twse.com.tw/mops/web/ajax_t12sc01",
        ),
        notes="MOPS notes this financial table is no longer required from 2025-04 ROC 114/04 onward.",
    ),
    "mops.fund-lending": Dataset(
        id="mops.fund-lending",
        title="資金貸與明細",
        group="mops",
        description="MOPS fund lending disclosure detail table by single company and month.",
        module="tw_stock_cli.crawlers.mops.fund_lending",
        kind="mops-fund-lending",
        returns=(
            "stock_id",
            "stock_name",
            "report_year",
            "report_month",
            "lender_name",
            "borrower_name",
            "is_related_party",
            "ending_balance",
            "actual_drawdown_amount",
            "interest_rate_range",
            "lending_nature",
            "short_term_financing_reason",
            "individual_lending_limit",
            "total_lending_limit",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t65sb04",),
        notes="The source page also contains endorsement guarantee data; use mops.endorsement-guarantee for that section.",
    ),
    "mops.endorsement-guarantee": Dataset(
        id="mops.endorsement-guarantee",
        title="背書保證明細",
        group="mops",
        description="MOPS endorsement guarantee disclosure detail table by single company and month.",
        module="tw_stock_cli.crawlers.mops.endorsement_guarantee",
        kind="mops-endorsement-guarantee",
        returns=(
            "stock_id",
            "stock_name",
            "report_year",
            "report_month",
            "guarantor_name",
            "guaranteed_party_name",
            "relationship",
            "individual_guarantee_limit",
            "ending_guarantee_balance",
            "actual_drawdown_amount",
            "net_worth_ratio",
            "total_guarantee_limit",
            "is_parent_to_subsidiary",
            "is_subsidiary_to_parent",
            "is_china_area_guarantee",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t65sb04",),
        notes="The source page also contains fund lending data; use mops.fund-lending for that section.",
    ),
    "mops.related-party-transaction": Dataset(
        id="mops.related-party-transaction",
        title="關係人交易申報明細",
        group="mops",
        description="MOPS related-party sales, purchases, receivables, payables, and asset transaction monthly disclosure.",
        module="tw_stock_cli.crawlers.mops.related_party_transaction",
        kind="mops-related-party-transaction",
        returns=(
            "stock_id",
            "stock_name",
            "report_year",
            "report_month",
            "transaction_type",
            "related_party_name",
            "asset_item",
            "current_month_amount",
            "current_month_ratio",
            "ytd_amount",
            "ytd_ratio",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t141sb02",),
        notes="The crawler flattens each related-party section into one row per counterparty and transaction type.",
    ),
    "mops.related-party-transaction-difference": Dataset(
        id="mops.related-party-transaction-difference",
        title="關係人交易查核核閱差異說明",
        group="mops",
        description="MOPS quarterly explanations for differences between related-party transaction filings and auditor audited/reviewed figures.",
        module="tw_stock_cli.crawlers.mops.related_party_transaction_difference",
        kind="mops-related-party-transaction-difference",
        returns=(
            "stock_id",
            "stock_name",
            "report_year",
            "quarter",
            "transaction_type",
            "reported_amount",
            "audited_reviewed_amount",
            "difference_amount",
            "difference_ratio",
            "difference_reason",
            "countermeasure",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t141sb03",),
        notes="This disclosure is sparse; companies without audit/review differences return an empty table.",
    ),
    "mops.director-supervisor-remuneration": Dataset(
        id="mops.director-supervisor-remuneration",
        title="董監事酬金相關資訊",
        group="mops",
        description="MOPS annual director/supervisor remuneration summary by market, including total remuneration, average remuneration, profit ratio, and reasonableness explanation.",
        module="tw_stock_cli.crawlers.mops.director_supervisor_remuneration",
        kind="mops-director-supervisor-remuneration",
        returns=(
            "market",
            "report_year",
            "report_type",
            "role",
            "industry",
            "stock_id",
            "stock_name",
            "base_remuneration_total",
            "with_employee_salary_total",
            "base_remuneration_profit_ratio",
            "average_base_remuneration",
            "after_tax_profit_loss",
            "eps",
            "roe",
            "reasonableness_explanation",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t119sb04",),
        notes="Defaults to company-level director remuneration sorted by stock ID; the source publishes a Big5 static report that the crawler follows.",
    ),
    "mops.financial-report-electronic-book": Dataset(
        id="mops.financial-report-electronic-book",
        title="財務報告電子書 metadata",
        group="mops",
        description="MOPS financial report electronic book metadata for a single company and year, including filenames and download request URLs.",
        module="tw_stock_cli.crawlers.mops.financial_report_electronic_book",
        kind="mops-financial-report-electronic-book",
        returns=(
            "stock_id",
            "document_year",
            "document_type",
            "detail_type",
            "detail_description",
            "filename",
            "file_size",
            "upload_datetime",
            "download_request_url",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_t57sb01_q1",
            "https://doc.twse.com.tw/server-java/t57sb01",
        ),
        notes="Returns electronic book metadata and the doc.twse download request URL; it does not parse PDF contents.",
    ),
    "mops.annual-report-electronic-book": Dataset(
        id="mops.annual-report-electronic-book",
        title="年報與股東會電子書 metadata",
        group="mops",
        description="MOPS annual report, shareholder meeting, and sustainability electronic book metadata for a single company and year.",
        module="tw_stock_cli.crawlers.mops.annual_report_electronic_book",
        kind="mops-annual-report-electronic-book",
        returns=(
            "stock_id",
            "document_year",
            "document_type",
            "detail_type",
            "meeting_type",
            "detail_description",
            "filename",
            "file_size",
            "upload_datetime",
            "download_request_url",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_t57sb01_q5",
            "https://doc.twse.com.tw/server-java/t57sb01",
        ),
        notes="Returns electronic book metadata and the doc.twse download request URL; it does not parse PDF contents.",
    ),
    "mops.related-company-reports": Dataset(
        id="mops.related-company-reports",
        title="關係企業三書表電子書 metadata",
        group="mops",
        description="MOPS affiliated enterprise report electronic book metadata for a single company and year, including filenames and download request URLs.",
        module="tw_stock_cli.crawlers.mops.related_company_reports_electronic_book",
        kind="mops-related-company-reports",
        returns=(
            "stock_id",
            "document_year",
            "document_type",
            "detail_type",
            "detail_description",
            "filename",
            "file_size",
            "upload_datetime",
            "download_request_url",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_t57sb01_q10",
            "https://doc.twse.com.tw/server-java/t57sb01",
        ),
        notes="Returns electronic book metadata and the doc.twse download request URL; it does not parse PDF contents.",
    ),
    "mops.major-shareholder-relationship": Dataset(
        id="mops.major-shareholder-relationship",
        title="年報前十大股東相互間關係 metadata",
        group="mops",
        description="MOPS annual report top-ten shareholder relationship metadata by year and market, with optional company filter.",
        module="tw_stock_cli.crawlers.mops.major_shareholder_relationship",
        kind="mops-major-shareholder-relationship",
        returns=(
            "market",
            "report_year",
            "stock_id",
            "stock_name",
            "shareholder_meeting_date",
            "detail_available",
            "filename",
            "download_request_url",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_t144sb10_w",
            "https://doc.twse.com.tw/server-java/t144sb10",
        ),
        notes="The detailed relationship table is published as a PDF; this dataset returns report metadata and download request URLs.",
    ),
    "mops.employee-benefit-expense": Dataset(
        id="mops.employee-benefit-expense",
        title="員工福利及薪資費用統計",
        group="mops",
        description="MOPS employee benefit and salary expense statistics by market, year, and optional industry code.",
        module="tw_stock_cli.crawlers.mops.employee_benefit_expense",
        kind="mops-employee-benefit-expense",
        returns=(
            "market",
            "report_year",
            "industry",
            "stock_id",
            "stock_name",
            "employee_benefit_expense_thousand",
            "employee_salary_expense_thousand",
            "employee_count",
            "avg_employee_salary_expense_thousand",
            "avg_employee_salary_change_ratio",
            "eps",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t100sb14",),
    ),
    "mops.employee-welfare-policy": Dataset(
        id="mops.employee-welfare-policy",
        title="員工福利政策及權益維護措施",
        group="mops",
        description="MOPS single-company employee welfare policy and rights protection disclosure, including welfare policy text, labor-management dispute status, social responsibility text, salary adjustment disclosure, and starting salary disclosure.",
        module="tw_stock_cli.crawlers.mops.employee_welfare_policy",
        kind="mops-employee-welfare-policy",
        returns=(
            "stock_id",
            "stock_name",
            "report_year",
            "disclosure_year",
            "section",
            "item",
            "value",
            "note",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t100sb12",),
        notes="Long text fields are preserved as source text; salary adjustment and starting salary tables are flattened into item/value rows.",
    ),
    "mops.full-time-employee-salary": Dataset(
        id="mops.full-time-employee-salary",
        title="非擔任主管職務全時員工薪資統計",
        group="mops",
        description="MOPS non-manager full-time employee salary statistics by market, year, and optional industry code.",
        module="tw_stock_cli.crawlers.mops.full_time_employee_salary",
        kind="mops-full-time-employee-salary",
        returns=(
            "market",
            "report_year",
            "industry",
            "stock_id",
            "stock_name",
            "salary_total_thousand",
            "employee_count_avg",
            "salary_avg_thousand",
            "salary_median_thousand",
            "eps",
            "peer_salary_avg_thousand",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t100sb15",),
    ),
    "mops.independent-director-profile": Dataset(
        id="mops.independent-director-profile",
        title="獨立董事基本資料",
        group="mops",
        description="MOPS independent director profile summary by market.",
        module="tw_stock_cli.crawlers.mops.independent_director_profile",
        kind="mops-independent-director-profile",
        returns=(
            "market",
            "sequence_no",
            "stock_id",
            "stock_name",
            "role",
            "person_name",
            "appointment_date",
            "current_positions",
            "experience",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t93sc01_1",),
    ),
    "mops.board-attendance-training": Dataset(
        id="mops.board-attendance-training",
        title="董事會出席與進修情形",
        group="mops",
        description="MOPS single-company board meeting attendance and director training detail.",
        module="tw_stock_cli.crawlers.mops.board_attendance_training",
        kind="mops-board-attendance-training",
        returns=(
            "stock_id",
            "stock_name",
            "market",
            "section",
            "role",
            "person_name",
            "attendance_count",
            "attendance_ratio",
            "course_name",
            "training_hours",
            "annual_training_hours",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t93sc03_1",),
        notes="Rows are split by section: board_attendance and director_training.",
    ),
    "mops.functional-committee": Dataset(
        id="mops.functional-committee",
        title="功能性委員會設置及成員",
        group="mops",
        description="MOPS functional committee establishment and member summary by market and committee code.",
        module="tw_stock_cli.crawlers.mops.functional_committee",
        kind="mops-functional-committee",
        returns=(
            "market",
            "committee_code",
            "committee_name",
            "stock_id",
            "stock_name",
            "established_date",
            "convener",
            "members",
            "operation_info",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_t100sb03_1",
            "https://mopsov.twse.com.tw/mops/web/ajax_t135sb02",
        ),
        notes="Use --committee for committee code; default 4 is remuneration committee, 6 uses the mandatory audit committee endpoint.",
    ),
    "mops.company-governance-structure": Dataset(
        id="mops.company-governance-structure",
        title="公司治理組織架構",
        group="mops",
        description="MOPS company governance organization structure table, including board seats, independent director seats, committee status, legal advisor, and shareholder service contact.",
        module="tw_stock_cli.crawlers.mops.company_governance_structure",
        kind="mops-company-governance-structure",
        returns=(
            "market",
            "stock_id",
            "stock_name",
            "articles_board_seats",
            "articles_independent_director_seats",
            "articles_supervisor_seats",
            "director_term_start",
            "director_term_end",
            "board_seats",
            "independent_director_seats",
            "audit_committee_status",
            "remuneration_committee_status",
            "legal_advisor",
            "shareholder_service_contact",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t100sb01_1",),
    ),
    "mops.sustainability-report": Dataset(
        id="mops.sustainability-report",
        title="永續報告書 metadata",
        group="mops",
        description="MOPS/ESGGen+ sustainability report metadata for a market/year with optional company filter, including website links and report download URLs.",
        module="tw_stock_cli.crawlers.mops.sustainability_report",
        kind="mops-sustainability-report",
        returns=(
            "market",
            "report_year",
            "stock_id",
            "stock_name",
            "industry",
            "reporting_interval",
            "compliance_notes",
            "assurance_provider",
            "assurance_standard",
            "tw_report_url",
            "tw_report_download_url",
            "en_report_url",
            "en_report_download_url",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_t100sb11",
            "https://esggenplus.twse.com.tw/api/api/MopsSustainReport/data",
        ),
        notes="Returns ESG report metadata and download links; it does not parse PDF contents.",
    ),
    "mops.esg-company-disclosure": Dataset(
        id="mops.esg-company-disclosure",
        title="企業 ESG 資訊揭露個別公司查詢 metadata",
        group="mops",
        description="MOPS ESG company disclosure inquiry metadata for a single company and year. MOPS redirects this query to ESGGen+.",
        module="tw_stock_cli.crawlers.mops.esg_company_disclosure",
        kind="mops-esg-company-disclosure",
        returns=(
            "stock_id",
            "mops_year",
            "report_year",
            "inquiry_url",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_t214sb01",
            "https://esggenplus.twse.com.tw/inquiry/info/individual",
        ),
        notes="Returns the ESGGen+ inquiry URL exposed by MOPS; it does not scrape the front-end rendered indicator table.",
    ),
    "mops.manager-compensation-distribution": Dataset(
        id="mops.manager-compensation-distribution",
        title="經理人員工酬勞分派情形",
        group="mops",
        description="MOPS single-company disclosure for managers receiving distributed employee compensation, including stock and cash compensation.",
        module="tw_stock_cli.crawlers.mops.manager_compensation_distribution",
        kind="mops-manager-compensation-distribution",
        returns=(
            "stock_id",
            "stock_name",
            "compensation_year",
            "distribution_year",
            "stock_compensation_shares",
            "stock_compensation_amount",
            "cash_compensation_amount",
            "total_compensation_amount",
            "profit_ratio",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t114sb07",),
        notes="The requested year is the distribution year; MOPS also reports the compensation year in the table heading.",
    ),
    "mops.shareholding-distribution": Dataset(
        id="mops.shareholding-distribution",
        title="股權分散表",
        group="mops",
        description="MOPS single-company shareholding distribution and shareholder structure table by year.",
        module="tw_stock_cli.crawlers.mops.shareholding_distribution",
        kind="mops-shareholding-distribution",
        returns=(
            "stock_id",
            "stock_name",
            "query_year",
            "data_date",
            "section",
            "bucket_or_category",
            "holders",
            "shares",
            "holding_ratio",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t16sn02",),
        notes="Includes both holding-level buckets and shareholder-structure categories from the MOPS table.",
    ),
    "mops.dividend-distribution": Dataset(
        id="mops.dividend-distribution",
        title="公司股利分派情形",
        group="mops",
        description="MOPS single-company dividend distribution and dividend policy table.",
        module="tw_stock_cli.crawlers.mops.dividend_distribution",
        kind="mops-company-year",
        returns=(
            "stock_id",
            "stock_name",
            "dividend_year",
            "cash_dividend_per_share",
            "capital_surplus_cash_per_share",
            "stock_dividend_per_share",
            "policy_text",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t05st09_2",),
        notes="Uses the board-resolution dividend distribution page for the requested ROC/AD year.",
    ),
    "mops.ex-dividend-announcement": Dataset(
        id="mops.ex-dividend-announcement",
        title="除權息公告",
        group="mops",
        description="MOPS ex-rights and ex-dividend announcement summary by year, optional company, month, and day range.",
        module="tw_stock_cli.crawlers.mops.ex_dividend_announcement",
        kind="mops-ex-dividend",
        returns=(
            "stock_id",
            "stock_name",
            "dividend_period",
            "record_date",
            "cash_dividend_from_earnings_per_share",
            "ex_dividend_date",
            "cash_dividend_payment_date",
            "announcement_date",
            "announcement_time",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t108sb27",),
        notes="Use with mops.dividend-distribution to connect board/shareholder dividend decisions to ex-dividend events.",
    ),
    "mops.investor-conference": Dataset(
        id="mops.investor-conference",
        title="法人說明會一覽表",
        group="mops",
        description="MOPS investor conference list by year, optional company and month.",
        module="tw_stock_cli.crawlers.mops.investor_conference",
        kind="mops-investor-conference",
        returns=(
            "stock_id",
            "stock_name",
            "conference_date",
            "conference_time",
            "location",
            "summary",
            "presentation_zh_file",
            "presentation_en_file",
            "presentation_zh_download_url",
            "presentation_en_download_url",
            "company_ir_url",
            "media_links",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t100sb02_1",),
        notes="Presentation columns contain MOPS file names and FileDownLoad URLs when files are disclosed.",
    ),
    "mops.insider-shareholding-change": Dataset(
        id="mops.insider-shareholding-change",
        title="內部人股權異動彙總表",
        group="mops",
        description="MOPS monthly summary of directors, supervisors, managers, and 10%+ major shareholder shareholding changes.",
        module="tw_stock_cli.crawlers.mops.insider_shareholding_change",
        kind="mops-insider-shareholding-change",
        returns=(
            "stock_id",
            "stock_name",
            "report_ym",
            "issued_shares",
            "directors_supervisors_increase_shares",
            "directors_supervisors_decrease_shares",
            "directors_supervisors_held_shares",
            "directors_supervisors_holding_ratio",
            "managers_held_shares",
            "major_shareholders_held_shares",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_IRB110",
            "https://siis.twse.com.tw/publish/",
        ),
        notes="MOPS returns a redirect to a TWSE published Big5 HTML report; this crawler follows and parses that report.",
    ),
    "mops.insider-shareholding-detail": Dataset(
        id="mops.insider-shareholding-detail",
        title="內部人持股異動事後申報表",
        group="mops",
        description="MOPS single-company monthly insider shareholding details by role, person, and share type.",
        module="tw_stock_cli.crawlers.mops.insider_shareholding_detail",
        kind="mops-insider-shareholding-detail",
        returns=(
            "stock_id",
            "stock_name",
            "report_ym",
            "role",
            "person_name",
            "share_type",
            "previous_month_held_shares",
            "increase_centralized_shares",
            "decrease_centralized_shares",
            "current_held_shares",
            "current_pledged_shares",
            "role_notes",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_query6_1",),
        notes="Insiders with multiple roles are disclosed in each role; do not sum rows without deduplicating role overlaps.",
    ),
    "mops.insider-holding-company-list": Dataset(
        id="mops.insider-holding-company-list",
        title="內部人持股餘額公司清單",
        group="mops",
        description="MOPS company list for the insider holding balance report by market, optional industry, year, and month.",
        module="tw_stock_cli.crawlers.mops.insider_holding_company_list",
        kind="mops-insider-holding-company-list",
        returns=(
            "stock_id",
            "stock_name",
            "report_ym",
            "market",
            "detail_available",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_stapap1_all",),
        notes="The MOPS summary page returns a company list; use mops.insider-holding-detail for the per-person holding balance detail.",
    ),
    "mops.insider-holding-detail": Dataset(
        id="mops.insider-holding-detail",
        title="董監事持股餘額明細資料",
        group="mops",
        description="MOPS single-company insider holding balance detail by role and person.",
        module="tw_stock_cli.crawlers.mops.insider_holding_detail",
        kind="mops-insider-holding-detail",
        returns=(
            "stock_id",
            "stock_name",
            "report_ym",
            "role",
            "person_name",
            "elected_shares",
            "current_shares",
            "pledged_shares",
            "pledged_ratio",
            "related_current_shares",
            "related_pledged_shares",
            "related_pledged_ratio",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_stapap1",),
        notes="MOPS warns that insiders with multiple roles disclose the same shares under each role; do not sum rows without deduplicating overlaps.",
    ),
    "mops.insider-transfer-declaration-detail": Dataset(
        id="mops.insider-transfer-declaration-detail",
        title="內部人持股轉讓事前申報表-個別公司",
        group="mops",
        description="MOPS single-company insider prior transfer declarations for a ROC/AD year and optional month range.",
        module="tw_stock_cli.crawlers.mops.insider_transfer_declaration_detail",
        kind="mops-insider-transfer-detail",
        returns=(
            "stock_id",
            "stock_name",
            "declaration_date",
            "declarer_role",
            "declarer_name",
            "transfer_method",
            "planned_transfer_shares",
            "current_own_shares",
            "planned_transfer_own_shares",
            "post_transfer_own_shares",
            "effective_transfer_period",
            "untransferred_report_filed",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t56sb21",),
        notes="Use --month for a single month or --start-month/--end-month for a range.",
    ),
    "mops.insider-transfer-untransferred-detail": Dataset(
        id="mops.insider-transfer-untransferred-detail",
        title="內部人持股未轉讓申報表-個別公司",
        group="mops",
        description="MOPS single-company insider untransferred declaration reports for a ROC/AD year and optional month range.",
        module="tw_stock_cli.crawlers.mops.insider_transfer_untransferred_detail",
        kind="mops-insider-transfer-detail",
        returns=(
            "stock_id",
            "stock_name",
            "declaration_date",
            "declarer_role",
            "declarer_name",
            "untransferred_own_shares",
            "current_own_shares",
            "original_planned_transfer_own_shares",
            "untransferred_reason",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t56sb21",),
        notes="Use --month for a single month or --start-month/--end-month for a range.",
    ),
    "mops.insider-transfer-declaration-summary": Dataset(
        id="mops.insider-transfer-declaration-summary",
        title="內部人持股轉讓事前申報彙總表",
        group="mops",
        description="MOPS market summary of insider prior transfer declarations for a ROC/AD year and optional month range.",
        module="tw_stock_cli.crawlers.mops.insider_transfer_declaration_summary",
        kind="mops-insider-transfer-summary",
        returns=(
            "stock_id",
            "stock_name",
            "declaration_date",
            "declarer_role",
            "declarer_name",
            "transfer_method",
            "planned_transfer_shares",
            "current_own_shares",
            "planned_transfer_own_shares",
            "post_transfer_own_shares",
            "effective_transfer_period",
            "untransferred_report_filed",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t56sb21",),
        notes="Use --month for a single month to avoid MOPS row-count limits.",
    ),
    "mops.insider-transfer-untransferred-summary": Dataset(
        id="mops.insider-transfer-untransferred-summary",
        title="內部人持股未轉讓申報彙總表",
        group="mops",
        description="MOPS market summary of insider untransferred declaration reports for a ROC/AD year and optional month range.",
        module="tw_stock_cli.crawlers.mops.insider_transfer_untransferred_summary",
        kind="mops-insider-transfer-summary",
        returns=(
            "stock_id",
            "stock_name",
            "declaration_date",
            "declarer_role",
            "declarer_name",
            "untransferred_own_shares",
            "current_own_shares",
            "original_planned_transfer_own_shares",
            "untransferred_reason",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t56sb21",),
        notes="Use --month for a single month to avoid MOPS row-count limits.",
    ),
    "mops.insider-pledge-summary": Dataset(
        id="mops.insider-pledge-summary",
        title="內部人質權設定彙總表",
        group="mops",
        description="MOPS monthly summary of pledge settings for directors, supervisors, managers, and 10%+ major shareholders.",
        module="tw_stock_cli.crawlers.mops.insider_pledge_summary",
        kind="mops-insider-pledge-summary",
        returns=(
            "stock_id",
            "stock_name",
            "report_ym",
            "directors_supervisors_held_shares",
            "directors_supervisors_pledged_shares",
            "directors_supervisors_released_pledge_shares",
            "directors_supervisors_cumulative_pledged_shares",
            "directors_supervisors_pledged_ratio",
            "managers_major_shareholders_pledged_shares",
            "managers_major_shareholders_pledged_ratio",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_IRB130",
            "https://siis.twse.com.tw/publish/",
        ),
        notes="MOPS returns a redirect to a TWSE published Big5 HTML report; this crawler follows and parses that report.",
    ),
    "mops.insider-pledge-ratio-summary": Dataset(
        id="mops.insider-pledge-ratio-summary",
        title="董監事質權設定持股占比彙總表",
        group="mops",
        description="MOPS monthly bucketed summary of director/supervisor pledge ratios as a share of actual holdings.",
        module="tw_stock_cli.crawlers.mops.insider_pledge_ratio_summary",
        kind="mops-insider-pledge-ratio-summary",
        returns=(
            "stock_id",
            "stock_name",
            "report_ym",
            "pledge_ratio_bucket",
            "pledge_ratio",
        ),
        source_urls=(
            "https://mopsov.twse.com.tw/mops/web/ajax_IRB180",
            "https://siis.twse.com.tw/publish/",
        ),
        notes="The source groups companies into percentage buckets; this crawler flattens each company entry into one row.",
    ),
    "mops.material-info": Dataset(
        id="mops.material-info",
        title="重大訊息",
        group="mops",
        description="MOPS material information announcement list by year, optional company, month, and day range.",
        module="tw_stock_cli.crawlers.mops.material_info",
        kind="mops-material-info",
        returns=(
            "stock_id",
            "stock_name",
            "announcement_date",
            "announcement_time",
            "subject",
            "detail_seq_no",
            "detail_spoke_date",
            "detail_spoke_time",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t05st01",),
        notes="Returns announcement list metadata. Detail keys are included for future detail fetching.",
    ),
    "mops.material-info-detail": Dataset(
        id="mops.material-info-detail",
        title="重大訊息詳細資料",
        group="mops",
        description="MOPS material information detail page parsed by company, sequence, spoke date, and spoke time.",
        module="tw_stock_cli.crawlers.mops.material_info_detail",
        kind="mops-material-info-detail",
        returns=(
            "stock_id",
            "stock_name",
            "seq_no",
            "announcement_date",
            "announcement_time",
            "spokesperson",
            "subject",
            "clause",
            "event_date",
            "description",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t05st01",),
        notes="Use detail keys returned by mops.material-info.",
    ),
    "mops.shareholder-meeting": Dataset(
        id="mops.shareholder-meeting",
        title="股東會日期地點及電子投票",
        group="mops",
        description="MOPS shareholder meeting date, location, book closure, and e-voting summary by year, optional company, month, and day range.",
        module="tw_stock_cli.crawlers.mops.shareholder_meeting",
        kind="mops-shareholder-meeting",
        returns=(
            "stock_id",
            "stock_name",
            "meeting_type",
            "meeting_date",
            "book_closure_start",
            "book_closure_end",
            "meeting_method",
            "location",
            "e_voting_period",
            "e_voting_url",
            "announcement_date",
            "announcement_time",
        ),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t108sb31",),
        notes="This is the MOPS summary for shareholder meeting date, location, and e-voting information.",
    ),
}


def list_datasets(group: str | None = None) -> list[Dataset]:
    datasets = sorted(DATASETS.values(), key=lambda dataset: dataset.id)
    if group:
        datasets = [dataset for dataset in datasets if dataset.group == group]
    return datasets


def get_dataset(dataset_id: str) -> Dataset:
    try:
        return DATASETS[dataset_id]
    except KeyError as exc:
        raise KeyError(f"Unknown dataset: {dataset_id}") from exc
