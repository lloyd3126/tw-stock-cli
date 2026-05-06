# FinMind 欄位對照

這份文件把 `tw-stock` 目前資料集的輸出欄位，對照到 FinMind API v4 的資料集與欄位。

參考來源：

- FinMind API base URL: `https://api.finmindtrade.com/api/v4`
- FinMind `llms-full.txt`: `https://finmind.github.io/llms-full.txt`
- FinMind `/translation`: `https://api.finmindtrade.com/api/v4/translation`
- 本專案資料集 catalog: `tw_stock_cli/registry.py`
- 本專案 crawler 欄位常數與 normalize helpers: `tw_stock_cli/crawlers/**`

## 對照狀態

| 狀態 | 意義 |
|---|---|
| exact | FinMind 有同語意欄位，欄位名稱不同也可直接 rename |
| join | 需要用 `stock_id` 或其他 key join 另一個 FinMind dataset |
| expression | 需要從 FinMind 欄位計算或 pivot |
| partial | 可部分對照，但語意或粒度不完全一致 |
| missing | 未在相近 FinMind dataset 找到直接欄位 |
| dynamic | 本專案輸出欄位由來源 HTML/CSV 動態決定 |

## Dataset 對照總覽

| tw-stock dataset | FinMind dataset | 覆蓋狀態 | 備註 |
|---|---|---|---|
| `twse.stock-price` | `TaiwanStockPrice`, `TaiwanStockInfo` | partial | FinMind 價格表無 `stock_name`，需 join `TaiwanStockInfo` 並 filter `type=twse` |
| `tpex.stock-price` | `TaiwanStockPrice`, `TaiwanStockInfo` | partial | FinMind 價格表無 `stock_name`，需 join `TaiwanStockInfo` 並 filter `type=tpex` |
| `twse.stock-list` | `TaiwanStockInfo` | exact | filter `type=twse` |
| `tpex.stock-list` | `TaiwanStockInfo` | exact | filter `type=tpex` |
| `twse.stock-per` | `TaiwanStockPER`, `TaiwanStockPrice`, `TaiwanStockInfo` | partial | `dividend_year`, `financial_report_period` 無直接對應 |
| `tpex.stock-per` | `TaiwanStockPER`, `TaiwanStockDividend`, `TaiwanStockInfo` | partial | `dividend_per_share`, `dividend_year` 只能用股利政策近似，非同一日 PER 表欄位 |
| `twse.institutional-trade` | `TaiwanStockInstitutionalInvestorsBuySell`, `TaiwanStockInfo` | expression | FinMind 是長表，需要依 `name` pivot 並計算 buy-sell |
| `tpex.institutional-trade` | `TaiwanStockInstitutionalInvestorsBuySell`, `TaiwanStockInfo` | expression | 同上 |
| `twse.margin-trade` | `TaiwanStockMarginPurchaseShortSale`, `TaiwanStockInfo` | partial | 融券償還欄位名稱不同但語意可對；部分 limit 欄位粒度可能不同 |
| `tpex.margin-trade` | `TaiwanStockMarginPurchaseShortSale`, `TaiwanStockInfo` | partial | FinMind 缺使用率與資券撥轉/來源欄位 |
| `twse.foreign-holding` | `TaiwanStockShareholding` | exact | 欄位語意高度相近 |
| `tpex.foreign-holding` | `TaiwanStockShareholding` | partial | FinMind 無 `rank` |
| `twse.total-return-index` | `TaiwanStockTotalReturnIndex` | exact | `data_id=TAIEX` |
| `tpex.total-return-index` | `TaiwanStockTotalReturnIndex` | partial | `data_id=TPEx` 可對報酬指數；一般櫃買指數 `index` 無直接欄位 |
| `taifex.futures-daily` | `TaiwanFuturesDaily` | exact | 欄位名稱可直接轉換 |
| `taifex.options-daily` | `TaiwanOptionDaily` | exact | 欄位名稱可直接轉換 |
| `taifex.futures-tick` | `TaiwanFuturesTick` | partial | FinMind tick 需 Backer/Sponsor；時間欄位與本專案拆法可能不同 |
| `taifex.options-tick` | `TaiwanOptionTick` | partial | FinMind API enum 是 `TaiwanOptionTick`；部分文件曾寫成 `TaiwanOptionTIck` |
| `taifex.futures-institutional` | `TaiwanFuturesInstitutionalInvestors` | expression | FinMind 缺淨額欄位，需自行 long-short |
| `taifex.fcm-futures-volume-day` | `TaiwanFuturesDealerTradingVolumeDaily` | expression | FinMind 是 broker/contract/session 長表，日盤用 `is_after_hour=false` 後 group |
| `taifex.fcm-futures-volume-night` | `TaiwanFuturesDealerTradingVolumeDaily` | expression | 夜盤用 `is_after_hour=true` 後 group |
| `taifex.fcm-options-volume-day` | `TaiwanOptionDealerTradingVolumeDaily` | expression | 日盤用 `is_after_hour=false` 後 group |
| `taifex.fcm-options-volume-night` | `TaiwanOptionDealerTradingVolumeDaily` | expression | 夜盤用 `is_after_hour=true` 後 group |
| `mops.month-revenue` | `TaiwanStockMonthRevenue` | exact | 欄位基本一致 |
| `mops.income-statement` | `TaiwanStockFinancialStatements` | partial | 本專案是多張寬表；FinMind 是 `type,value,origin_name` 長表 |
| `mops.balance-sheet` | `TaiwanStockBalanceSheet` | partial | 同上 |
| `mops.cash-flow` | `TaiwanStockCashFlowsStatement` | partial | 同上 |

## 股票清單

適用資料集：`twse.stock-list`, `tpex.stock-list`

FinMind dataset: `TaiwanStockInfo`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `stock_id` | `stock_id` | exact |  |
| `stock_name` | `stock_name` | exact |  |
| `industry_category` | `industry_category` | exact | `tpex.stock-list` 目前會輸出；TWSE 可從 FinMind 取得 |
| `date` | `date` | exact |  |
| 市場別 | `type` | expression | TWSE filter `type=twse`，TPEx filter `type=tpex` |

## 股票每日價格

適用資料集：`twse.stock-price`, `tpex.stock-price`

FinMind dataset: `TaiwanStockPrice`; 股票名稱需 join `TaiwanStockInfo`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `date` | `date` | exact |  |
| `stock_id` | `stock_id` | exact |  |
| `stock_name` | `TaiwanStockInfo.stock_name` | join | 依 `stock_id` join，並用 `type` 區分 TWSE/TPEx |
| `open` | `open` | exact |  |
| `high` | `max` | exact | FinMind 用 `max` |
| `low` | `min` | exact | FinMind 用 `min` |
| `close` | `close` | exact |  |

FinMind 另有但本專案價格資料集目前未輸出的欄位：`Trading_Volume`, `Trading_money`, `spread`, `Trading_turnover`。

## 本益比、殖利率、PBR

適用資料集：`twse.stock-per`, `tpex.stock-per`

主要 FinMind dataset: `TaiwanStockPER`; 股票名稱需 join `TaiwanStockInfo`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `date` | `date` | exact |  |
| `stock_id` | `stock_id` | exact |  |
| `stock_name` | `TaiwanStockInfo.stock_name` | join |  |
| `close` | `TaiwanStockPrice.close` | join | FinMind `TaiwanStockPER` 不含收盤價 |
| `dividend_yield` | `dividend_yield` | exact |  |
| `per` | `PER` | exact | FinMind 欄位大寫 |
| `pbr` | `PBR` | exact | FinMind 欄位大寫 |
| `dividend_per_share` | `TaiwanStockDividend.CashEarningsDistribution` | partial | 只適合補股利政策語意，不是 PER 日表同欄位 |
| `dividend_year` | `TaiwanStockDividend.year` | partial | FinMind PER 表無此欄位 |
| `financial_report_period` |  | missing | FinMind PER 表無此欄位 |

## 三大法人買賣超

適用資料集：`twse.institutional-trade`, `tpex.institutional-trade`

FinMind dataset: `TaiwanStockInstitutionalInvestorsBuySell`

FinMind 欄位是長表：`date`, `stock_id`, `name`, `buy`, `sell`。本專案欄位是寬表，所以多數欄位需要依 `name` pivot。

| tw-stock 欄位 | FinMind 對照 | 狀態 | 備註 |
|---|---|---|---|
| `stock_id` | `stock_id` | exact |  |
| `stock_name` | `TaiwanStockInfo.stock_name` | join |  |
| `foreign_ex_dealer_buy` | `buy` where `name=Foreign_Investor` | expression | translation 中文為「外資」 |
| `foreign_ex_dealer_sell` | `sell` where `name=Foreign_Investor` | expression |  |
| `foreign_ex_dealer_net_buy` | `buy - sell` where `name=Foreign_Investor` | expression |  |
| `foreign_dealer_buy` | `buy` where `name=Foreign_Dealer_Self` | expression | translation 中文為「外資自營商」 |
| `foreign_dealer_sell` | `sell` where `name=Foreign_Dealer_Self` | expression |  |
| `foreign_dealer_net_buy` | `buy - sell` where `name=Foreign_Dealer_Self` | expression |  |
| `foreign_total_buy` | sum `buy` for `Foreign_Investor`, `Foreign_Dealer_Self` | expression | TPEx 欄位 |
| `foreign_total_sell` | sum `sell` for `Foreign_Investor`, `Foreign_Dealer_Self` | expression | TPEx 欄位 |
| `foreign_total_net_buy` | `foreign_total_buy - foreign_total_sell` | expression | TPEx 欄位 |
| `investment_trust_buy` | `buy` where `name=Investment_Trust` | expression | translation 中文為「投信」 |
| `investment_trust_sell` | `sell` where `name=Investment_Trust` | expression |  |
| `investment_trust_net_buy` | `buy - sell` where `name=Investment_Trust` | expression |  |
| `dealer_self_buy` | `buy` where `name=Dealer_self` | expression | translation 中文為「自營商自行買賣」 |
| `dealer_self_sell` | `sell` where `name=Dealer_self` | expression |  |
| `dealer_self_net_buy` | `buy - sell` where `name=Dealer_self` | expression |  |
| `dealer_hedge_buy` | `buy` where `name=Dealer_Hedging` | expression | translation 中文為「自營商避險」 |
| `dealer_hedge_sell` | `sell` where `name=Dealer_Hedging` | expression |  |
| `dealer_hedge_net_buy` | `buy - sell` where `name=Dealer_Hedging` | expression |  |
| `dealer_total_buy` | sum `buy` for `Dealer_self`, `Dealer_Hedging` | expression | TPEx 欄位 |
| `dealer_total_sell` | sum `sell` for `Dealer_self`, `Dealer_Hedging` | expression | TPEx 欄位 |
| `dealer_total_net_buy` | `dealer_total_buy - dealer_total_sell` | expression | TPEx 欄位 |
| `dealer_net_buy` | `buy - sell` where `name=Dealer`, or dealer total expression | expression | TWSE 欄位；實作時需用樣本驗證 FinMind 是否回傳 aggregate `Dealer` |
| `institutional_net_buy` | sum all tracked `buy - sell` | expression | 本專案三大法人合計 |

## 融資融券

適用資料集：`twse.margin-trade`, `tpex.margin-trade`

FinMind dataset: `TaiwanStockMarginPurchaseShortSale`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `date` | `date` | exact | 本專案 registry 回傳欄位未列出，但資料語意有日期 |
| `stock_id` | `stock_id` | exact |  |
| `stock_name` | `TaiwanStockInfo.stock_name` | join |  |
| `margin_purchase_buy` | `MarginPurchaseBuy` | exact |  |
| `margin_purchase_sell` | `MarginPurchaseSell` | exact |  |
| `margin_purchase_cash_repayment` | `MarginPurchaseCashRepayment` | exact |  |
| `margin_purchase_previous_balance` | `MarginPurchaseYesterdayBalance` | exact |  |
| `margin_purchase_balance` | `MarginPurchaseTodayBalance` | exact |  |
| `margin_purchase_next_limit` | `MarginPurchaseLimit` | partial | TWSE 欄名為次一營業日限額；FinMind 為融資限額 |
| `margin_purchase_limit` | `MarginPurchaseLimit` | exact | TPEx 欄位 |
| `margin_purchase_usage_ratio` |  | missing | TPEx 欄位，FinMind margin dataset 未列 |
| `margin_purchase_from_finance_company` |  | missing | TPEx 欄位，FinMind margin dataset 未列 |
| `short_sale_buy` | `ShortSaleBuy` | exact |  |
| `short_sale_sell` | `ShortSaleSell` | exact |  |
| `short_sale_stock_repayment` | `ShortSaleCashRepayment` | partial | 來源中文可能是券償/融券償還；FinMind 欄名為 cash repayment |
| `short_sale_previous_balance` | `ShortSaleYesterdayBalance` | exact |  |
| `short_sale_balance` | `ShortSaleTodayBalance` | exact |  |
| `short_sale_next_limit` | `ShortSaleLimit` | partial | TWSE 欄名為次一營業日限額；FinMind 為融券限額 |
| `short_sale_limit` | `ShortSaleLimit` | exact | TPEx 欄位 |
| `short_sale_usage_ratio` |  | missing | TPEx 欄位，FinMind margin dataset 未列 |
| `short_sale_from_finance_company` |  | missing | TPEx 欄位，FinMind margin dataset 未列 |
| `offsetting_trade` | `OffsetLoanAndShort` | exact |  |
| `note` | `Note` | exact |  |

## 外資持股

適用資料集：`twse.foreign-holding`, `tpex.foreign-holding`

FinMind dataset: `TaiwanStockShareholding`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `date` | `date` | exact |  |
| `rank` |  | missing | TPEx 排名欄位，FinMind 無直接欄位 |
| `stock_id` | `stock_id` | exact |  |
| `stock_name` | `stock_name` | exact |  |
| `isin` | `InternationalCode` | exact |  |
| `issued_shares` | `NumberOfSharesIssued` | exact |  |
| `foreign_available_shares` | `ForeignInvestmentRemainingShares` | exact |  |
| `foreign_held_shares` | `ForeignInvestmentShares` | exact |  |
| `foreign_available_ratio` | `ForeignInvestmentRemainRatio` | exact |  |
| `foreign_held_ratio` | `ForeignInvestmentSharesRatio` | exact |  |
| `foreign_investment_limit_ratio` | `ForeignInvestmentUpperLimitRatio` | exact |  |
| `mainland_investment_limit_ratio` | `ChineseInvestmentUpperLimitRatio` | exact |  |
| `change_reason` | `note` | partial | FinMind translation 將 `note` 說明為與前日異動原因 |
| `last_change_date` | `RecentlyDeclareDate` | exact |  |
| `note` | `note` | exact | TPEx 欄位 |

## 報酬指數

適用資料集：`twse.total-return-index`, `tpex.total-return-index`

FinMind dataset: `TaiwanStockTotalReturnIndex`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `date` | `date` | exact |  |
| `total_return_index` | `price` | exact | TWSE 用 `data_id=TAIEX`，TPEx 用 `data_id=TPEx` |
| `index` |  | missing | `tpex.total-return-index` 的一般櫃買指數值，FinMind 此 dataset 只列 `price` |
| market id | `stock_id` | exact | `TAIEX` 或 `TPEx` |

## 期貨每日行情

適用資料集：`taifex.futures-daily`

FinMind dataset: `TaiwanFuturesDaily`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `trade_date` | `date` | exact |  |
| `contract` | `futures_id` | exact |  |
| `expiry_month_week` | `contract_date` | exact |  |
| `open` | `open` | exact |  |
| `high` | `max` | exact |  |
| `low` | `min` | exact |  |
| `close` | `close` | exact |  |
| `change` | `spread` | exact | 本專案 daily market helper 會保留此欄 |
| `change_pct` | `spread_per` | exact |  |
| `volume` | `volume` | exact |  |
| `settlement_price` | `settlement_price` | exact |  |
| `open_interest` | `open_interest` | exact |  |
| `session` | `trading_session` | exact |  |
| `best_bid` |  | missing |  |
| `best_ask` |  | missing |  |
| `historical_high` |  | missing |  |
| `historical_low` |  | missing |  |
| `halt_note` |  | missing |  |
| `spread_volume` |  | missing |  |
| `contract_expiry_date` |  | missing |  |

## 選擇權每日行情

適用資料集：`taifex.options-daily`

FinMind dataset: `TaiwanOptionDaily`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `trade_date` | `date` | exact |  |
| `contract` | `option_id` | exact |  |
| `expiry_month_week` | `contract_date` | exact |  |
| `strike_price` | `strike_price` | exact |  |
| `call_put` | `call_put` | exact |  |
| `open` | `open` | exact |  |
| `high` | `max` | exact |  |
| `low` | `min` | exact |  |
| `close` | `close` | exact |  |
| `volume` | `volume` | exact |  |
| `settlement_price` | `settlement_price` | exact |  |
| `open_interest` | `open_interest` | exact |  |
| `session` | `trading_session` | exact |  |
| `change` |  | missing | FinMind option daily schema 未列 spread |
| `change_pct` |  | missing |  |
| `best_bid` |  | missing |  |
| `best_ask` |  | missing |  |
| `historical_high` |  | missing |  |
| `historical_low` |  | missing |  |
| `halt_note` |  | missing |  |
| `spread_volume` |  | missing |  |
| `contract_expiry_date` |  | missing |  |

## 期貨逐筆

適用資料集：`taifex.futures-tick`

FinMind dataset: `TaiwanFuturesTick`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `trade_date` | `date` | partial | FinMind tick 欄位可能包含時間資訊；導入時需實測切分 |
| `trade_time` | `date` | partial | 同上 |
| `contract` | `futures_id` | exact |  |
| `expiry_month_week` | `contract_date` | exact |  |
| `trade_price` | `price` | exact |  |
| `trade_volume` | `volume` | exact |  |
| `near_month_price` |  | missing |  |
| `far_month_price` |  | missing |  |
| `opening_auction` |  | missing |  |

## 選擇權逐筆

適用資料集：`taifex.options-tick`

FinMind dataset: `TaiwanOptionTick`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `trade_date` | `date` | partial | FinMind tick 欄位可能包含時間資訊；導入時需實測切分 |
| `trade_time` | `date` | partial | 同上 |
| `contract` | `option_id` | exact |  |
| `strike_price` | `ExercisePrice` | exact |  |
| `expiry_month_week` | `contract_date` | exact |  |
| `call_put` | `PutCall` | exact |  |
| `trade_price` | `price` | exact |  |
| `trade_volume` | `volume` | exact |  |
| `opening_auction` |  | missing |  |

## 期貨三大法人未平倉

適用資料集：`taifex.futures-institutional`

FinMind dataset: `TaiwanFuturesInstitutionalInvestors`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `row_number` |  | missing |  |
| `contract_name` | `futures_id` or `name` | partial | FinMind 文件列 `name`，API 樣本回傳 `futures_id` |
| `investor_type` | `institutional_investors` | exact |  |
| `trade_long_volume` | `long_deal_volume` | exact |  |
| `trade_long_amount` | `long_deal_amount` | exact |  |
| `trade_short_volume` | `short_deal_volume` | exact |  |
| `trade_short_amount` | `short_deal_amount` | exact |  |
| `trade_net_volume` | `long_deal_volume - short_deal_volume` | expression |  |
| `trade_net_amount` | `long_deal_amount - short_deal_amount` | expression |  |
| `open_interest_long_volume` | `long_open_interest_balance_volume` | exact |  |
| `open_interest_long_amount` | `long_open_interest_balance_amount` | exact |  |
| `open_interest_short_volume` | `short_open_interest_balance_volume` | exact |  |
| `open_interest_short_amount` | `short_open_interest_balance_amount` | exact |  |
| `open_interest_net_volume` | `long_open_interest_balance_volume - short_open_interest_balance_volume` | expression |  |
| `open_interest_net_amount` | `long_open_interest_balance_amount - short_open_interest_balance_amount` | expression |  |

## 期貨商成交量

適用資料集：`taifex.fcm-futures-volume-day`, `taifex.fcm-futures-volume-night`, `taifex.fcm-options-volume-day`, `taifex.fcm-options-volume-night`

FinMind datasets:

- futures: `TaiwanFuturesDealerTradingVolumeDaily`
- options: `TaiwanOptionDealerTradingVolumeDaily`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `fcm_id` | `dealer_code` | exact |  |
| `fcm_name` | `dealer_name` | exact |  |
| contract columns | `futures_id` or `option_id` plus `volume` | expression | 本專案 CSV 可能是一欄一商品；FinMind 是一列一商品 |
| `subtotal` | sum `volume` grouped by dealer/session | expression | 期貨日盤 |
| `total` | sum `volume` grouped by dealer/session | expression | 期貨夜盤、選擇權日/夜盤 |
| `market_share` |  | missing | FinMind dealer volume dataset 未列 |
| session | `is_after_hour` | expression | 日盤 `false`，夜盤 `true` |

## 月營收

適用資料集：`mops.month-revenue`

FinMind dataset: `TaiwanStockMonthRevenue`

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `stock_id` | `stock_id` | exact |  |
| `revenue` | `revenue` | exact |  |
| `revenue_year` | `revenue_year` | exact |  |
| `revenue_month` | `revenue_month` | exact |  |
| date | `date` | join | 本專案用 `year/month` 參數；FinMind 用 period date |
| country | `country` | missing | FinMind 額外欄位，本專案未輸出 |

## 財報多表資料

適用資料集：

- `mops.income-statement` -> `TaiwanStockFinancialStatements`
- `mops.balance-sheet` -> `TaiwanStockBalanceSheet`
- `mops.cash-flow` -> `TaiwanStockCashFlowsStatement`

本專案 MOPS 財報 crawler 會解析 MOPS HTML，輸出多個 DataFrame，並保留來源表格中的多數中文會計科目欄位。FinMind 財報資料是長表，欄位為 `date`, `stock_id`, `type`, `value`, `origin_name`。

| tw-stock 欄位 | FinMind 欄位 | 狀態 | 備註 |
|---|---|---|---|
| `stock_id` | `stock_id` | exact |  |
| `stock_name` | `TaiwanStockInfo.stock_name` | join | FinMind 財報長表不含公司名稱 |
| `section` | `type` or `origin_name` | partial | 本專案 section 來自 MOPS 表格結構，FinMind 用科目代碼/原始名稱表示 |
| 中文會計科目欄位 | `origin_name`, `type`, `value` | dynamic | 需要把本專案寬表 melt 成長表，或把 FinMind 長表 pivot 回寬表 |
| 財報期間 | `date` | partial | FinMind 用期末日期；本專案用 `year`/`quarter` 查詢 |

## 導入建議

如果要在 CLI 內支援 FinMind provider，建議先做三層轉換：

1. `dataset_id -> FinMind dataset + query params` mapping。
2. `FinMind columns -> tw-stock columns` rename/expression mapping。
3. 對長表資料實作 per-dataset adapter，例如法人買賣超 pivot、期貨商成交量 group by、財報 long/wide 轉換。

第一批最容易接入的資料集：

- `twse.stock-list`, `tpex.stock-list`
- `twse.stock-price`, `tpex.stock-price`
- `twse.total-return-index`
- `taifex.futures-daily`
- `taifex.options-daily`
- `mops.month-revenue`
