# 資料集指南

這份文件整理 `tw-stock` 目前可抓取的每一種資料。每個資料集都包含簡介、參數、範例指令、主要欄位與常見用途。

範例日期多使用 `2026-04-30`；實際使用時請改成需要查詢的交易日或財報期間。逐筆成交與部分期貨資料量可能很大，探索時建議搭配 `--limit`。

## 參數速查

- `date`：交易日，格式為 `YYYY-MM-DD`。
- `year`：西元年或民國年，MOPS 會自動轉成來源端需要的民國年。
- `month`：月份，適用於 MOPS 月營收、公告清單與內部人月彙總資料。
- `start_month`, `end_month`：MOPS 月份區間，適用於內部人轉讓申報資料；若提供 `month`，會查單月。
- `quarter`：季度，值為 `1` 到 `4`。
- `market`：MOPS 市場別，預設 `sii`；可用值為 `sii`、`otc`、`rotc`、`pub`、`all`。
- `industry_code`：MOPS 產業別代碼，適用於部分公司清單類查詢。
- `foreign`：MOPS 月營收外國公司旗標，預設 `0`。
- `stock_id`：公司股票代號，適用於 MOPS 單一公司詳細財報與公司公告類資料。
- `committee`：MOPS 功能性委員會代碼，預設 `4` 薪資報酬委員會；`6` 使用強制設置審計委員會端點。

## TWSE 上市資料

### `twse.stock-price` - 上市股票每日收盤價

抓取 TWSE 上市有價證券每日行情，包含開盤、最高、最低與收盤價。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch twse.stock-price --date 2026-04-30 --limit 5 --format table
```

- 主要欄位：`stock_id`, `stock_name`, `open`, `high`, `low`, `close`, `date`
- 常見用途：建立 OHLC 價格資料、每日行情檢查、匯出上市市場價格。

### `twse.stock-list` - 上市股票清單

抓取指定交易日 TWSE 上市有價證券代號與名稱。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch twse.stock-list --date 2026-04-30 --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `date`
- 常見用途：建立上市股票 universe、代號名稱對照、與其他上市資料集 join。

### `twse.stock-per` - 上市本益比與殖利率

抓取 TWSE 上市股票的本益比、殖利率、股價淨值比與財報年季。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch twse.stock-per --date 2026-04-30 --limit 5 --format table
```

- 主要欄位：`stock_id`, `stock_name`, `close`, `dividend_yield`, `dividend_year`, `per`, `pbr`, `financial_report_period`, `date`
- 常見用途：估值篩選、殖利率比較、基本面指標匯出。

### `twse.institutional-trade` - 上市三大法人買賣超

抓取 TWSE 上市股票每日三大法人買進、賣出與買賣超資料。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch twse.institutional-trade --date 2026-04-30 --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `foreign_ex_dealer_net_buy`, `investment_trust_net_buy`, `dealer_net_buy`, `institutional_net_buy`
- 常見用途：追蹤法人資金流、排行法人買賣超、分析籌碼變化。

### `twse.margin-trade` - 上市融資融券餘額

抓取 TWSE 上市股票每日融資融券買賣、償還與餘額。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch twse.margin-trade --date 2026-04-30 --limit 5 --format table
```

- 主要欄位：`stock_id`, `stock_name`, `margin_purchase_balance`, `short_sale_balance`, `offsetting_trade`, `note`
- 常見用途：信用交易餘額監控、融資融券變化分析、籌碼風險觀察。

### `twse.foreign-holding` - 上市外資及陸資持股

抓取 TWSE 上市有價證券外資及陸資持股、可投資股數與持股比率。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch twse.foreign-holding --date 2026-04-30 --limit 5 --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `issued_shares`, `foreign_held_shares`, `foreign_held_ratio`
- 常見用途：外資持股比例追蹤、外資持股上限檢查、持股集中度分析。

### `twse.total-return-index` - 發行量加權股價報酬指數

抓取指定日期所在月份的 TWSE 發行量加權股價報酬指數。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch twse.total-return-index --date 2026-04-30 --format table
```

- 主要欄位：`date`, `total_return_index`
- 常見用途：市場報酬指標、總報酬比較、指數走勢資料匯出。

## TPEx 上櫃資料

### `tpex.stock-price` - 上櫃股票每日收盤價

抓取 TPEx 上櫃有價證券每日行情，包含開盤、最高、最低與收盤價。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch tpex.stock-price --date 2026-04-30 --limit 5 --format table
```

- 主要欄位：`stock_id`, `stock_name`, `close`, `open`, `high`, `low`, `date`
- 常見用途：建立上櫃 OHLC 價格資料、每日行情檢查、匯出上櫃市場價格。

### `tpex.stock-list` - 上櫃股票清單

依產業分類抓取 TPEx 上櫃有價證券代號與名稱。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch tpex.stock-list --date 2026-04-30 --limit 10 --format table
```

- 主要欄位：`stock_id`, `stock_name`, `industry_category`, `date`
- 常見用途：建立上櫃股票 universe、產業分類對照、與其他上櫃資料集 join。

### `tpex.stock-per` - 上櫃本益比與殖利率

抓取 TPEx 上櫃股票的本益比、每股股利、殖利率與股價淨值比。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch tpex.stock-per --date 2026-04-30 --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `per`, `dividend_per_share`, `dividend_year`, `dividend_yield`, `pbr`, `date`
- 常見用途：上櫃股票估值比較、殖利率排行、基本面資料匯出。

### `tpex.institutional-trade` - 上櫃三大法人買賣超

抓取 TPEx 上櫃股票每日三大法人買進、賣出與買賣超資料。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch tpex.institutional-trade --date 2026-04-30 --limit 5 --format table
```

- 主要欄位：`stock_id`, `stock_name`, `foreign_total_net_buy`, `investment_trust_net_buy`, `dealer_total_net_buy`, `institutional_net_buy`
- 常見用途：觀察上櫃法人資金流、比較三大法人買賣超、籌碼面分析。

### `tpex.margin-trade` - 上櫃融資融券餘額

抓取 TPEx 上櫃股票每日融資融券買賣、償還、使用率與餘額。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch tpex.margin-trade --date 2026-04-30 --limit 5 --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `margin_purchase_balance`, `margin_purchase_usage_ratio`, `short_sale_balance`, `short_sale_usage_ratio`
- 常見用途：信用交易監控、融資融券使用率分析、籌碼風險觀察。

### `tpex.foreign-holding` - 上櫃外資持股比例

抓取 TPEx 上櫃股票外資持股數、持股比率與可投資比率排行。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch tpex.foreign-holding --date 2026-04-30 --limit 5 --format table
```

- 主要欄位：`rank`, `stock_id`, `stock_name`, `foreign_held_shares`, `foreign_held_ratio`
- 常見用途：外資持股排行、持股比例監控、上櫃外資籌碼分析。

### `tpex.total-return-index` - 櫃買指數與報酬指數

抓取指定日期所在月份的櫃買指數與櫃買報酬指數。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch tpex.total-return-index --date 2026-04-30 --format table
```

- 主要欄位：`date`, `index`, `total_return_index`
- 常見用途：上櫃市場指標追蹤、報酬指數比較、指數走勢匯出。

## TAIFEX 期貨與選擇權資料

### `taifex.futures-daily` - 期貨每日交易行情

抓取 TAIFEX 期貨每日行情，包含契約、到期月份、OHLC、成交量與未平倉等資訊。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch taifex.futures-daily --date 2026-04-30 --limit 10 --format table
```

- 主要欄位：`trade_date`, `contract`, `expiry_month_week`, `open`, `high`, `low`, `close`, `volume`
- 常見用途：期貨行情分析、契約成交量比較、未平倉資料整理。

### `taifex.options-daily` - 選擇權每日交易行情

抓取 TAIFEX 選擇權每日行情，包含契約、履約價、買賣權、收盤價與成交量。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch taifex.options-daily --date 2026-04-30 --limit 10 --format jsonl
```

- 主要欄位：`trade_date`, `contract`, `expiry_month_week`, `strike_price`, `call_put`, `close`, `volume`
- 常見用途：選擇權鏈資料整理、履約價成交量分析、波動與部位研究。

### `taifex.futures-tick` - 期貨逐筆成交

抓取 TAIFEX 期貨逐筆成交資料。此資料集通常很大，探索時請搭配 `--limit`。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch taifex.futures-tick --date 2026-04-30 --limit 20 --format jsonl
```

- 主要欄位：`trade_date`, `contract`, `expiry_month_week`, `trade_time`, `trade_price`, `trade_volume`
- 常見用途：高頻成交分析、成交時間分布、盤中交易行為研究。

### `taifex.options-tick` - 選擇權逐筆成交

抓取 TAIFEX 選擇權逐筆成交資料。此資料集通常很大，探索時請搭配 `--limit`。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch taifex.options-tick --date 2026-04-30 --limit 20 --format jsonl
```

- 主要欄位：`trade_date`, `contract`, `strike_price`, `expiry_month_week`, `call_put`, `trade_time`, `trade_price`
- 常見用途：選擇權逐筆成交分析、履約價成交分布、盤中成交研究。

### `taifex.futures-institutional` - 期貨三大法人未平倉

抓取 TAIFEX 期貨三大法人交易口數、契約金額與未平倉餘額。

- 必填參數：`date`
- 範例：

```sh
uv run tw-stock fetch taifex.futures-institutional --date 2026-04-30 --format table
```

- 主要欄位：`row_number`, `contract_name`, `investor_type`, `trade_long_volume`, `open_interest_long_volume`
- 常見用途：分析法人期貨部位、觀察多空淨額、追蹤未平倉變化。

### `taifex.fcm-futures-volume-day` - 期貨商期貨成交量日盤

抓取期貨商期貨日盤成交量排行與市佔資料。

- 必填參數：無
- 範例：

```sh
uv run tw-stock fetch taifex.fcm-futures-volume-day --limit 10 --format table
```

- 主要欄位：`fcm_id`, `fcm_name`, `subtotal`
- 常見用途：期貨商成交量排行、日盤市佔分析、經紀商活動觀察。

### `taifex.fcm-futures-volume-night` - 期貨商期貨成交量夜盤

抓取期貨商期貨夜盤成交量排行與市佔資料。

- 必填參數：無
- 範例：

```sh
uv run tw-stock fetch taifex.fcm-futures-volume-night --limit 10 --format json
```

- 主要欄位：`fcm_id`, `fcm_name`, `total`, `market_share`
- 常見用途：夜盤期貨商市佔分析、日夜盤成交結構比較。

### `taifex.fcm-options-volume-day` - 期貨商選擇權成交量日盤

抓取期貨商選擇權日盤成交量排行與市佔資料。

- 必填參數：無
- 範例：

```sh
uv run tw-stock fetch taifex.fcm-options-volume-day --limit 10 --format table
```

- 主要欄位：`fcm_id`, `fcm_name`, `total`, `market_share`
- 常見用途：選擇權日盤成交排行、期貨商市佔分析、商品別成交量比較。

### `taifex.fcm-options-volume-night` - 期貨商選擇權成交量夜盤

抓取期貨商選擇權夜盤成交量排行與市佔資料。

- 必填參數：無
- 範例：

```sh
uv run tw-stock fetch taifex.fcm-options-volume-night --limit 10 --format jsonl
```

- 主要欄位：`fcm_id`, `fcm_name`, `total`, `market_share`
- 常見用途：夜盤選擇權成交觀察、日夜盤期貨商活動比較。

## MOPS 公開資訊觀測站資料

### `mops.month-revenue` - 月營收

抓取公開資訊觀測站公司月營收資料。

- 必填參數：`year`, `month`
- 選填參數：`market`, `foreign`
- 範例：

```sh
uv run tw-stock fetch mops.month-revenue --year 2026 --month 3 --market sii --format jsonl
```

- 主要欄位：`stock_id`, `revenue`, `revenue_year`, `revenue_month`
- 常見用途：月營收追蹤、營收年增/月增分析、公司基本面資料建立。

### `mops.income-statement` - 綜合損益表

抓取公開資訊觀測站季度綜合損益表。此資料集會回傳多張表，因不同產業財報格式可能不同。

- 必填參數：`year`, `quarter`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.income-statement --year 2025 --quarter 4 --market sii --format json
```

- 主要欄位：多張表；共用識別欄位包含 `stock_id`, `stock_name`
- 常見用途：損益表彙整、獲利能力分析、EPS 與營業利益觀察。

### `mops.balance-sheet` - 資產負債表

抓取公開資訊觀測站季度資產負債表。此資料集會回傳多張表，因不同產業財報格式可能不同。

- 必填參數：`year`, `quarter`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.balance-sheet --year 2025 --quarter 4 --market sii --format json
```

- 主要欄位：多張表；共用識別欄位包含 `stock_id`, `stock_name`
- 常見用途：資產負債結構分析、淨值與負債比較、財務體質檢查。

### `mops.cash-flow` - 現金流量表

抓取公開資訊觀測站季度現金流量表。此資料集會回傳多張表，因不同產業財報格式可能不同。

- 必填參數：`year`, `quarter`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.cash-flow --year 2025 --quarter 4 --market sii --format json
```

- 主要欄位：多張表；共用識別欄位包含 `stock_id`, `stock_name`
- 常見用途：營業現金流追蹤、投資與籌資現金流分析、自由現金流資料整理。

### `mops.company-income-statement` - 個別公司綜合損益表

抓取公開資訊觀測站單一公司的詳細綜合損益表。這個資料集比彙總表保留更多會計科目細項，欄位會依查詢年度與比較期間動態產生。

- 必填參數：`stock_id`, `year`, `quarter`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.company-income-statement --stock-id 2395 --year 2025 --quarter 4 --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `report_year`, `quarter`, `statement`, `item`, `indent_level`，以及動態期間欄位如 `114年度_amount`
- 常見用途：分析單一公司的損益表細項、取得彙總表未列出的營業費用與營業外項目。

### `mops.company-balance-sheet` - 個別公司資產負債表

抓取公開資訊觀測站單一公司的詳細資產負債表。欄位會依查詢年度與比較期末日動態產生。

- 必填參數：`stock_id`, `year`, `quarter`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.company-balance-sheet --stock-id 2395 --year 2025 --quarter 4 --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `report_year`, `quarter`, `statement`, `item`, `indent_level`，以及動態期間欄位如 `114年12月31日_amount`
- 常見用途：分析單一公司的資產、負債與權益細項。

### `mops.company-cash-flow` - 個別公司現金流量表

抓取公開資訊觀測站單一公司的詳細現金流量表。這是計算標準自由現金流時較適合使用的資料集，因為它可保留資本支出相關細項。

- 必填參數：`stock_id`, `year`, `quarter`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.company-cash-flow --stock-id 2395 --year 2025 --quarter 4 --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `report_year`, `quarter`, `statement`, `item`, `indent_level`，以及動態期間欄位如 `114年度_amount`
- 常見用途：取得營業活動現金流、取得不動產廠房及設備、取得無形資產等細項，進一步計算自由現金流。

### `mops.company-equity-changes` - 個別公司權益變動表

抓取公開資訊觀測站單一公司的詳細權益變動表。來源通常會同時提供本年度與比較年度，所以 JSON 輸出會回傳多張表。

- 必填參數：`stock_id`, `year`, `quarter`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.company-equity-changes --stock-id 2395 --year 2025 --quarter 4 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `report_year`, `quarter`, `statement_year`, `statement`, `item`, `indent_level`，以及權益科目欄位
- 常見用途：追蹤股本、資本公積、保留盈餘、其他權益與現金股利對權益的影響。

### `mops.company-basic-info` - 公司基本資料

抓取公開資訊觀測站公司基本資料，可依市場別、產業別或公司代號篩選。

- 必填參數：無
- 選填參數：`market`, `industry_code`, `stock_id`
- 範例：

```sh
uv run tw-stock fetch mops.company-basic-info --market sii --stock-id 2395 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `short_name`, `industry`, `chairman`, `general_manager`, `spokesperson`, `paid_in_capital`
- 常見用途：建立公司基本資料表、補公司產業分類、股本、董總與投資人關係資訊。

### `mops.treasury-stock-buyback` - 庫藏股買回基本資料

抓取公開資訊觀測站單一公司的庫藏股買回基本資料。MOPS 會先回傳買回次數清單，CLI 會自動逐筆跟進詳細資料，並保留買回辦法、董事會決議內容等長文字在 `detail_text` 與延伸欄位。

- 必填參數：`stock_id`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.treasury-stock-buyback --stock-id 1101 --market sii --limit 2 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `buyback_no`, `report_date`, `board_resolution_date`, `buyback_purpose`, `share_type`, `planned_buyback_shares`, `planned_start_date`, `planned_end_date`, `price_floor`, `price_ceiling`, `buyback_method`, `detail_text`
- 常見用途：追蹤公司買回庫藏股目的、預定買回股數、買回期間、價格區間與董事會決議內容。

### `mops.private-placement` - 私募有價證券資料

抓取公開資訊觀測站私募有價證券一覽表，可依市場別或單一公司查詢。來源頁包含多種詳細申報按鈕，CLI 會將是否有董事會決議、定價、繳款與資金運用季報資料整理成欄位。

- 必填參數：無
- 選填參數：`market`, `stock_id`
- 範例：

```sh
uv run tw-stock fetch mops.private-placement --stock-id 1316 --market sii --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `market`, `security_type`, `decision_date`, `year_period`, `pricing_detail_available`, `payment_detail_available`, `fund_utilization_periods`
- 常見用途：建立私募事件清單、追蹤實際定價/繳款完成狀態與資金運用季報期間。

### `mops.asset-acquisition-disposal` - 月取得或處分資產資訊

抓取公開資訊觀測站單一公司的月取得或處分資產資訊。此頁會先回傳 MOPS auto form，再轉入 `t12sc01` 報表；若公司該月份未申報，CLI 會回傳空表。

- 必填參數：`stock_id`, `year`, `month`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.asset-acquisition-disposal --stock-id 8011 --year 2024 --month 9 --market sii --format json
```

- 主要欄位：`stock_id`, `stock_name`, `market`, `report_year`, `report_month`, `detail_available`, `detail_text`
- 常見用途：追蹤公司月度取得或處分資產申報，搭配重大訊息可建立資產交易事件資料。

### `mops.asset-acquisition-disposal-financial` - 取得或處分資產財務資料表

抓取公開資訊觀測站取得或處分資產相關財務資料表，包含金融資產合計、占總資產比率、占歸母權益比率、營運資金與有價證券質設市值。來源註明自民國 114 年 4 月起免申報此財務資料表。

- 必填參數：`stock_id`, `year`, `month`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.asset-acquisition-disposal-financial --stock-id 8011 --year 2024 --month 9 --market sii --format json
```

- 主要欄位：`stock_id`, `stock_name`, `report_year`, `report_month`, `financial_assets_total`, `total_assets_ratio`, `equity_ratio`, `working_capital`, `pledged_securities_market_value`
- 常見用途：補足取得或處分資產月報的財務背景，監控金融資產部位、資產/權益占比與營運資金。

### `mops.fund-lending` - 資金貸與明細

抓取公開資訊觀測站單一公司的資金貸與資訊揭露明細表。來源 `t65sb04` 同頁也包含背書保證資訊，CLI 將兩個區塊拆成獨立資料集，方便分別建模。

- 必填參數：`stock_id`, `year`, `month`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.fund-lending --stock-id 1101 --year 2025 --month 3 --market sii --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `report_year`, `report_month`, `lender_name`, `borrower_name`, `is_related_party`, `ending_balance`, `actual_drawdown_amount`, `interest_rate_range`, `lending_nature`, `short_term_financing_reason`, `individual_lending_limit`, `total_lending_limit`
- 常見用途：追蹤集團內外資金貸與、關係人往來、期末餘額、實際動支金額與貸與額度控管。

### `mops.endorsement-guarantee` - 背書保證明細

抓取公開資訊觀測站單一公司的背書保證資訊揭露明細表。來源 `t65sb04` 同頁也包含資金貸與資訊，CLI 將背書保證區塊單獨整理成一列一被保證對象。

- 必填參數：`stock_id`, `year`, `month`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.endorsement-guarantee --stock-id 1101 --year 2025 --month 3 --market sii --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `report_year`, `report_month`, `guarantor_name`, `guaranteed_party_name`, `relationship`, `individual_guarantee_limit`, `ending_guarantee_balance`, `actual_drawdown_amount`, `net_worth_ratio`, `total_guarantee_limit`, `is_parent_to_subsidiary`, `is_subsidiary_to_parent`, `is_china_area_guarantee`
- 常見用途：監控背書保證餘額、實際動支、淨值占比、對子公司/母公司/大陸地區保證暴險。

### `mops.related-party-transaction` - 關係人交易申報明細

抓取公開資訊觀測站單一公司的關係人交易申報明細，並將銷貨、進貨、應收款、應付款、取得資產與處分資產等分段表格攤平成一列一關係人交易類型。

- 必填參數：`stock_id`, `year`, `month`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.related-party-transaction --stock-id 8011 --year 2024 --month 9 --market sii --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `report_year`, `report_month`, `transaction_type`, `related_party_name`, `asset_item`, `current_month_amount`, `current_month_ratio`, `ytd_amount`, `ytd_ratio`
- 常見用途：追蹤關係人銷進貨、往來款、資產交易與合併報表占比，建立關係人交易監控資料。

### `mops.related-party-transaction-difference` - 關係人交易查核核閱差異說明

抓取公開資訊觀測站單一公司季度關係人交易「申報數」與會計師查核（核閱）數差異說明。此揭露只有在公司達差異門檻時才會有資料，沒有差異時來源通常回空表。

- 必填參數：`stock_id`, `year`, `quarter`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.related-party-transaction-difference --stock-id 3162 --year 2025 --quarter 1 --market otc --format json
```

- 主要欄位：`stock_id`, `stock_name`, `report_year`, `quarter`, `transaction_type`, `reported_amount`, `audited_reviewed_amount`, `difference_amount`, `difference_ratio`, `difference_reason`, `countermeasure`
- 常見用途：補強關係人交易申報資料，追蹤自結/申報數與會計師查核或核閱數差異及原因。

### `mops.director-supervisor-remuneration` - 董監事酬金相關資訊

抓取公開資訊觀測站年度董監事酬金彙總。來源會先產生 Big5 靜態報表，CLI 會自動跟進並整理酬金總額、加計兼任員工酬金、平均每位酬金、稅後損益、EPS、ROE 與合理性說明。

- 必填參數：`year`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.director-supervisor-remuneration --year 2024 --market sii --limit 5 --format json
```

- 主要欄位：`market`, `report_year`, `report_type`, `role`, `industry`, `stock_id`, `stock_name`, `base_remuneration_total`, `with_employee_salary_total`, `base_remuneration_profit_ratio`, `average_base_remuneration`, `after_tax_profit_loss`, `eps`, `roe`, `reasonableness_explanation`
- 常見用途：分析董監事酬金與公司獲利、ROE、EPS 的關係，建立治理與薪酬風險指標。

### `mops.financial-report-electronic-book` - 財務報告電子書 metadata

抓取公開資訊觀測站單一公司的財務報告電子書 metadata。此資料集回傳 PDF 檔名、檔案大小、上傳日期與 doc.twse 下載請求 URL，不解析 PDF 內容。

- 必填參數：`stock_id`, `year`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.financial-report-electronic-book --stock-id 2395 --year 2024 --market all --format json
```

- 主要欄位：`stock_id`, `document_year`, `document_type`, `detail_type`, `detail_description`, `filename`, `file_size`, `upload_datetime`, `download_request_url`
- 常見用途：盤點財報 PDF、建立下載清單、追蹤補正或上傳時間。

### `mops.annual-report-electronic-book` - 年報與股東會電子書 metadata

抓取公開資訊觀測站單一公司的年報、股東會與永續相關電子書 metadata。適合先取得年報 PDF 檔案資訊，再交給後續 PDF parser。

- 必填參數：`stock_id`, `year`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.annual-report-electronic-book --stock-id 2395 --year 2024 --market all --format json
```

- 主要欄位：`stock_id`, `document_year`, `document_type`, `detail_type`, `meeting_type`, `detail_description`, `filename`, `upload_datetime`, `download_request_url`
- 常見用途：年報下載清單、股東會資料歸檔、永續專章檔案追蹤。

### `mops.related-company-reports` - 關係企業三書表電子書 metadata

抓取公開資訊觀測站單一公司的關係企業三書表電子書 metadata。此資料集回傳電子檔名、上傳時間與 doc.twse 下載請求 URL，不解析 PDF 內容。

- 必填參數：`stock_id`, `year`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.related-company-reports --stock-id 2395 --year 2024 --market all --format json
```

- 主要欄位：`stock_id`, `document_year`, `document_type`, `detail_type`, `detail_description`, `filename`, `file_size`, `upload_datetime`, `download_request_url`
- 常見用途：關係企業報告書下載清單、集團關係文件盤點、PDF 後續處理入口。

### `mops.major-shareholder-relationship` - 年報前十大股東相互間關係 metadata

抓取公開資訊觀測站「年報前十大股東相互間關係」清單。來源細節是 PDF，CLI 目前回傳公司、股東會日期、PDF 檔名與下載請求 URL。

- 必填參數：`year`
- 選填參數：`market`, `stock_id`
- 範例：

```sh
uv run tw-stock fetch mops.major-shareholder-relationship --stock-id 2395 --year 2024 --market sii --format json
```

- 主要欄位：`market`, `report_year`, `stock_id`, `stock_name`, `shareholder_meeting_date`, `detail_available`, `filename`, `download_request_url`
- 常見用途：主要股東關係 PDF 盤點、關係人治理資料索引、年報附表下載清單。

### `mops.sustainability-report` - 永續報告書 metadata

抓取 MOPS/ESGGen+ 永續報告書 metadata，包含永續報告書網站連結、中文/英文報告下載 URL、報告期間、準則與確信資訊。此資料集只回傳 metadata 與下載連結，不解析 PDF。

- 必填參數：`year`
- 選填參數：`market`, `stock_id`
- 範例：

```sh
uv run tw-stock fetch mops.sustainability-report --stock-id 2395 --year 2024 --market sii --format json
```

- 主要欄位：`market`, `report_year`, `stock_id`, `stock_name`, `industry`, `reporting_interval`, `compliance_notes`, `assurance_provider`, `assurance_standard`, `tw_report_url`, `tw_report_download_url`, `en_report_url`, `en_report_download_url`
- 常見用途：ESG 報告書下載清單、永續報告揭露盤點、確信資訊整理。

### `mops.esg-company-disclosure` - 企業 ESG 資訊揭露個別公司查詢 metadata

抓取公開資訊觀測站「企業 ESG 資訊揭露」個別公司查詢入口。MOPS 目前會將查詢結果跳轉到 ESGGen+，因此此資料集回傳該查詢 URL，不硬拆前端渲染的指標表。

- 必填參數：`stock_id`, `year`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.esg-company-disclosure --stock-id 2395 --year 2024 --market sii --format json
```

- 主要欄位：`stock_id`, `mops_year`, `report_year`, `inquiry_url`
- 常見用途：建立 ESGGen+ 個別公司揭露入口索引、與永續報告書 metadata 串接。

### `mops.employee-benefit-expense` - 員工福利及薪資費用統計

抓取公開資訊觀測站員工福利與薪資費用統計，包含員工人數、福利費用、薪資費用、平均薪資與同業平均。

- 必填參數：`year`
- 選填參數：`market`, `industry_code`
- 範例：

```sh
uv run tw-stock fetch mops.employee-benefit-expense --year 2024 --market sii --limit 5 --format json
```

- 主要欄位：`market`, `report_year`, `industry`, `stock_id`, `stock_name`, `employee_benefit_expense_thousand`, `employee_salary_expense_thousand`, `employee_count`, `avg_employee_salary_expense_thousand`, `eps`
- 常見用途：薪資福利比較、產業人均費用分析、ESG 社會面指標整理。

### `mops.employee-welfare-policy` - 員工福利政策及權益維護措施

抓取公開資訊觀測站單一公司的員工福利政策及權益維護措施揭露，保留長文字內容，並將平均調薪與新進員工起薪表攤平成 `section`/`item`/`value` 列。

- 必填參數：`stock_id`, `year`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.employee-welfare-policy --stock-id 2395 --year 2025 --market all --format json
```

- 主要欄位：`stock_id`, `stock_name`, `report_year`, `disclosure_year`, `section`, `item`, `value`, `note`
- 常見用途：員工福利政策文字索引、勞資糾紛揭露、薪資調整與起薪揭露盤點。

### `mops.full-time-employee-salary` - 非擔任主管職務全時員工薪資統計

抓取公開資訊觀測站非主管全時員工薪資統計，包含平均數、中位數、與前期變動比率。

- 必填參數：`year`
- 選填參數：`market`, `industry_code`
- 範例：

```sh
uv run tw-stock fetch mops.full-time-employee-salary --year 2024 --market sii --limit 5 --format json
```

- 主要欄位：`market`, `report_year`, `industry`, `stock_id`, `stock_name`, `salary_total_thousand`, `employee_count_avg`, `salary_avg_thousand`, `salary_median_thousand`, `eps`
- 常見用途：員工薪資中位數比較、薪資與 EPS 關係分析、ESG 社會面揭露整理。

### `mops.independent-director-profile` - 獨立董事基本資料

抓取公開資訊觀測站獨立董事基本資料彙總，包含職稱、姓名、就任日期、主要現職、主要經歷與兼任情形。

- 必填參數：無
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.independent-director-profile --market sii --limit 5 --format json
```

- 主要欄位：`market`, `sequence_no`, `stock_id`, `stock_name`, `role`, `person_name`, `appointment_date`, `current_positions`, `experience`
- 常見用途：獨董名單盤點、兼任情形查核、治理資料庫建立。

### `mops.board-attendance-training` - 董事會出席與進修情形

抓取公開資訊觀測站單一公司的董事會出席與董事進修情形。輸出會以 `section` 區分 `board_attendance` 與 `director_training`。

- 必填參數：`stock_id`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.board-attendance-training --stock-id 2395 --market sii --format json
```

- 主要欄位：`stock_id`, `stock_name`, `section`, `role`, `person_name`, `attendance_count`, `attendance_ratio`, `course_name`, `training_hours`, `annual_training_hours`
- 常見用途：董事出席率檢查、董事進修紀錄整理、公司治理評估。

### `mops.functional-committee` - 功能性委員會設置及成員

抓取公開資訊觀測站功能性委員會設置與成員摘要。預設查薪資報酬委員會；可用 `--committee 6` 查強制設置審計委員會。

- 必填參數：無
- 選填參數：`market`, `committee`
- 範例：

```sh
uv run tw-stock fetch mops.functional-committee --market sii --committee 4 --limit 5 --format json
```

- 主要欄位：`market`, `committee_code`, `committee_name`, `stock_id`, `stock_name`, `established_date`, `convener`, `members`, `operation_info`
- 常見用途：功能性委員會設置率、委員名單盤點、審計/薪酬委員會治理資料整理。

### `mops.company-governance-structure` - 公司治理組織架構

抓取公開資訊觀測站「公司治理組織架構部分」資料，包含公司章程席次、董事任期、缺額情形、審計/薪資報酬委員會設置狀態、法律顧問與股東建議或糾紛處理窗口。

- 必填參數：無
- 選填參數：`market`, `stock_id`
- 範例：

```sh
uv run tw-stock fetch mops.company-governance-structure --stock-id 2395 --market sii --format json
```

- 主要欄位：`market`, `stock_id`, `stock_name`, `articles_board_seats`, `articles_independent_director_seats`, `director_term_start`, `director_term_end`, `board_seats`, `independent_director_seats`, `audit_committee_status`, `remuneration_committee_status`, `legal_advisor`, `shareholder_service_contact`
- 常見用途：董事會席次與委員會設置盤點、公司治理資料索引、法遵窗口整理。

### `mops.manager-compensation-distribution` - 經理人員工酬勞分派情形

抓取公開資訊觀測站單一公司分派員工酬勞之經理人姓名及分派情形彙總表，整理股票酬勞、現金酬勞、合計金額與占稅後純益比例。

- 必填參數：`stock_id`, `year`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.manager-compensation-distribution --stock-id 2395 --year 2024 --market sii --format json
```

- 主要欄位：`stock_id`, `stock_name`, `compensation_year`, `distribution_year`, `stock_compensation_shares`, `stock_compensation_amount`, `cash_compensation_amount`, `total_compensation_amount`, `profit_ratio`
- 常見用途：追蹤經理人分派員工酬勞，與公司章程、獲利與董監酬金資料交叉分析。

### `mops.shareholding-distribution` - 股權分散表

抓取公開資訊觀測站單一公司的股權分散表，包含持股分級與股東結構兩個區塊，並攤平成一列一個級距或結構類別。

- 必填參數：`stock_id`, `year`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.shareholding-distribution --stock-id 2395 --year 2024 --market sii --format json
```

- 主要欄位：`stock_id`, `stock_name`, `query_year`, `data_date`, `section`, `bucket_or_category`, `holders`, `shares`, `holding_ratio`
- 常見用途：觀察股權集中度、散戶/法人結構、持股級距分布，並補足內部人與主要股東持股之外的股權結構輪廓。

### `mops.dividend-distribution` - 公司股利分派情形

抓取公開資訊觀測站單一公司指定年度的股利分派資料，包含董事會決議日、每股現金股利、資本公積發放、配股與公司章程中的股利政策文字。

- 必填參數：`stock_id`, `year`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.dividend-distribution --stock-id 2395 --year 2025 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `query_year`, `dividend_year`, `board_resolution_date`, `cash_dividend_per_share`, `capital_surplus_cash_per_share`, `total_cash_dividend`, `policy_text`
- 常見用途：股利政策分析、殖利率資料建立、股利決議事件追蹤。

### `mops.ex-dividend-announcement` - 除權息公告

抓取公開資訊觀測站除權息公告彙總表。可查單一公司全年資料，也可用月份與日期區間查詢全市場或特定公司公告。

- 必填參數：`year`
- 選填參數：`market`, `stock_id`, `month`, `start_day`, `end_day`
- 範例：

```sh
uv run tw-stock fetch mops.ex-dividend-announcement --stock-id 2395 --year 2025 --market sii --format json
uv run tw-stock fetch mops.ex-dividend-announcement --year 2025 --market sii --month 7 --start-day 1 --end-day 31 --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `dividend_period`, `record_date`, `cash_dividend_from_earnings_per_share`, `ex_dividend_date`, `cash_dividend_payment_date`, `announcement_date`, `announcement_time`
- 常見用途：把股利決議接到實際除息日、權利分派基準日與現金股利發放日，建立股利事件時程。

### `mops.investor-conference` - 法人說明會一覽表

抓取公開資訊觀測站法人說明會一覽表。可查單一公司全年或指定月份，也可依市場別查詢。

- 必填參數：`year`
- 選填參數：`market`, `stock_id`, `month`
- 範例：

```sh
uv run tw-stock fetch mops.investor-conference --stock-id 2395 --year 2025 --market sii --format jsonl
uv run tw-stock fetch mops.investor-conference --year 2025 --market sii --month 3 --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `conference_date`, `conference_time`, `location`, `summary`, `presentation_zh_file`, `presentation_en_file`, `presentation_zh_download_url`, `presentation_en_download_url`, `company_ir_url`, `media_links`
- 常見用途：建立法說會事件資料、追蹤簡報檔下載連結、公司 IR 頁面與影音連結。

### `mops.shareholder-meeting` - 股東會日期地點及電子投票

抓取公開資訊觀測站股東常會/臨時會日期、地點、停止過戶期間與電子投票資訊。可查單一公司全年資料，也可用月份與日期區間查詢全市場或特定公司公告。

- 必填參數：`year`
- 選填參數：`market`, `stock_id`, `month`, `start_day`, `end_day`
- 範例：

```sh
uv run tw-stock fetch mops.shareholder-meeting --stock-id 2395 --year 2025 --market sii --format json
uv run tw-stock fetch mops.shareholder-meeting --year 2025 --market sii --month 6 --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `meeting_type`, `meeting_date`, `book_closure_start`, `book_closure_end`, `meeting_method`, `location`, `e_voting_period`, `e_voting_url`, `announcement_date`, `announcement_time`
- 常見用途：建立股東會事件資料、追蹤停止過戶期間、電子投票期間與公司治理時程。

### `mops.insider-shareholding-change` - 內部人股權異動彙總表

抓取公開資訊觀測站董事、監察人、經理人及百分之十以上大股東股權異動月彙總表。MOPS 會先回傳 TWSE publish 靜態報表連結，CLI 會自動跟隨並解析 Big5 HTML 表格。

- 必填參數：`year`, `month`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.insider-shareholding-change --year 2025 --month 3 --market sii --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `report_ym`, `issued_shares`, `directors_supervisors_increase_shares`, `directors_supervisors_decrease_shares`, `directors_supervisors_held_shares`, `directors_supervisors_holding_ratio`, `managers_held_shares`, `major_shareholders_held_shares`
- 常見用途：追蹤董監事與內部人持股變化、觀察經理人與大股東持股水位、建立公司治理與籌碼面月資料。

### `mops.insider-shareholding-detail` - 內部人持股異動事後申報表

抓取公開資訊觀測站單一公司的內部人持股異動事後申報表。資料會依身份別、姓名與持股種類列出選任當時、上月、本月增減與本月底持股/信託/設質/私募股數。

- 必填參數：`stock_id`, `year`, `month`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.insider-shareholding-detail --stock-id 2395 --year 2025 --month 3 --market sii --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `report_ym`, `role`, `person_name`, `share_type`, `previous_month_held_shares`, `increase_centralized_shares`, `decrease_centralized_shares`, `current_held_shares`, `current_pledged_shares`, `role_notes`
- 常見用途：追蹤單一公司董監事、經理人、大股東逐人持股變化；分析設質、信託與身份別備註。來源提醒：內部人若具二種以上身份，每種身份別會揭露同樣股數，分析時不可直接加總。

### `mops.insider-holding-company-list` - 內部人持股餘額公司清單

抓取公開資訊觀測站「內部人持股餘額明細資料」的公司清單。來源頁 `stapap1_all` 只列出特定市場、月份與產業別下可進一步查詢的公司，逐人持股餘額請接 `mops.insider-holding-detail`。

- 必填參數：`year`, `month`
- 選填參數：`market`, `industry_code`
- 範例：

```sh
uv run tw-stock fetch mops.insider-holding-company-list --year 2025 --month 3 --market sii --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `query_year`, `query_month`, `report_ym`, `market`, `detail_available`
- 常見用途：建立每月可查詢公司 universe、依市場或產業批次展開單一公司持股餘額明細。

### `mops.insider-holding-detail` - 董監事持股餘額明細資料

抓取公開資訊觀測站單一公司的董監事持股餘額明細。資料依職稱與姓名列出選任時股數、目前持股、設質股數、設質比率，以及關係人持股與設質資訊。

- 必填參數：`stock_id`, `year`, `month`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.insider-holding-detail --stock-id 2395 --year 2025 --month 3 --market sii --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `report_ym`, `role`, `person_name`, `elected_shares`, `current_shares`, `pledged_shares`, `pledged_ratio`, `related_current_shares`, `related_pledged_shares`, `related_pledged_ratio`
- 常見用途：追蹤董監事逐人目前持股、設質比率與關係人設質情形。來源提醒：內部人若具二種以上身份，每種身份別會揭露同樣股數，分析時不可直接加總。

### `mops.insider-transfer-declaration-detail` - 內部人持股轉讓事前申報表-個別公司

抓取公開資訊觀測站單一公司內部人持股轉讓事前申報資料，也就是「持股轉讓日報表」個別公司版。

- 必填參數：`stock_id`, `year`
- 選填參數：`market`, `month`, `start_month`, `end_month`
- 範例：

```sh
uv run tw-stock fetch mops.insider-transfer-declaration-detail --stock-id 1210 --year 2025 --month 3 --market sii --format json
```

- 主要欄位：`stock_id`, `stock_name`, `declaration_date`, `declarer_role`, `declarer_name`, `transfer_method`, `planned_transfer_shares`, `current_own_shares`, `planned_transfer_own_shares`, `post_transfer_own_shares`, `effective_transfer_period`, `untransferred_report_filed`
- 常見用途：追蹤單一公司內部人預告轉讓股票、轉讓方式、有效轉讓期間與是否後續申報未完成轉讓。

### `mops.insider-transfer-untransferred-detail` - 內部人持股未轉讓申報表-個別公司

抓取公開資訊觀測站單一公司內部人持股未轉讓申報資料，也就是「持股未轉讓日報表」個別公司版。

- 必填參數：`stock_id`, `year`
- 選填參數：`market`, `month`, `start_month`, `end_month`
- 範例：

```sh
uv run tw-stock fetch mops.insider-transfer-untransferred-detail --stock-id 2254 --year 2025 --month 3 --market sii --format json
```

- 主要欄位：`stock_id`, `stock_name`, `declaration_date`, `declarer_role`, `declarer_name`, `untransferred_own_shares`, `current_own_shares`, `original_planned_transfer_own_shares`, `untransferred_reason`
- 常見用途：追蹤內部人未完成轉讓股數與原因，例如股價不理想、期間屆滿等。

### `mops.insider-transfer-declaration-summary` - 內部人持股轉讓事前申報彙總表

抓取公開資訊觀測站全市場內部人持股轉讓事前申報彙總表。建議使用 `month` 查單月，避免來源端回覆資料筆數過多。

- 必填參數：`year`
- 選填參數：`market`, `month`, `start_month`, `end_month`
- 範例：

```sh
uv run tw-stock fetch mops.insider-transfer-declaration-summary --year 2025 --month 3 --market sii --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `declaration_date`, `declarer_role`, `declarer_name`, `transfer_method`, `planned_transfer_shares`, `current_own_shares`, `planned_transfer_own_shares`, `post_transfer_own_shares`, `effective_transfer_period`, `untransferred_report_filed`
- 常見用途：建立全市場內部人預告轉讓事件資料、監控大額轉讓與轉讓方式。

### `mops.insider-transfer-untransferred-summary` - 內部人持股未轉讓申報彙總表

抓取公開資訊觀測站全市場內部人持股未轉讓申報彙總表。建議使用 `month` 查單月，避免來源端回覆資料筆數過多。

- 必填參數：`year`
- 選填參數：`market`, `month`, `start_month`, `end_month`
- 範例：

```sh
uv run tw-stock fetch mops.insider-transfer-untransferred-summary --year 2025 --month 3 --market sii --format json
```

- 主要欄位：`stock_id`, `stock_name`, `declaration_date`, `declarer_role`, `declarer_name`, `untransferred_own_shares`, `current_own_shares`, `original_planned_transfer_own_shares`, `untransferred_reason`
- 常見用途：分析預告轉讓後未完成的情形，補足內部人轉讓事件後續追蹤。

### `mops.insider-pledge-summary` - 內部人質權設定彙總表

抓取公開資訊觀測站董事、監察人、經理人及百分之十以上大股東質權設定月彙總表。MOPS 會先回傳 TWSE publish 靜態報表連結，CLI 會自動跟隨並解析 Big5 HTML 表格。

- 必填參數：`year`, `month`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.insider-pledge-summary --year 2025 --month 3 --market sii --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `report_ym`, `directors_supervisors_held_shares`, `directors_supervisors_pledged_shares`, `directors_supervisors_released_pledge_shares`, `directors_supervisors_cumulative_pledged_shares`, `directors_supervisors_pledged_ratio`, `managers_major_shareholders_pledged_shares`, `managers_major_shareholders_pledged_ratio`
- 常見用途：追蹤董監事與大股東設質風險，建立公司治理風險指標。

### `mops.insider-pledge-ratio-summary` - 董監事質權設定持股占比彙總表

抓取公開資訊觀測站董監事質權設定持股占比月彙總表。MOPS 會先回傳 TWSE publish 靜態報表連結，來源表依設質比例級距分組，CLI 會自動攤平成一家公司一列。

- 必填參數：`year`, `month`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.insider-pledge-ratio-summary --year 2025 --month 3 --market sii --limit 5 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `report_ym`, `pledge_ratio_bucket`, `pledge_ratio`
- 常見用途：快速篩選董監事持股設質比率偏高公司、建立設質風險級距監控名單。

### `mops.material-info` - 重大訊息

抓取公開資訊觀測站重大訊息清單。可查單一公司全年資料，也可用月份與日期區間查詢全市場或特定公司公告。

- 必填參數：`year`
- 選填參數：`market`, `stock_id`, `month`, `start_day`, `end_day`
- 範例：

```sh
uv run tw-stock fetch mops.material-info --stock-id 2395 --year 2025 --format jsonl
uv run tw-stock fetch mops.material-info --year 2026 --month 5 --start-day 1 --end-day 5 --format jsonl
```

- 主要欄位：`stock_id`, `stock_name`, `announcement_date`, `announcement_time`, `subject`, `detail_seq_no`, `detail_spoke_date`, `detail_spoke_time`
- 常見用途：建立公司公告事件資料庫、事件研究、風險監控、後續接重大訊息詳細內容。

### `mops.material-info-detail` - 重大訊息詳細資料

抓取公開資訊觀測站重大訊息詳細頁。通常先用 `mops.material-info` 取得 `detail_seq_no`, `detail_spoke_date`, `detail_spoke_time`, `detail_type`，再帶入此資料集取得完整公告內容。

- 必填參數：`stock_id`, `seq_no`, `spoke_date`, `spoke_time`
- 選填參數：`market`
- 範例：

```sh
uv run tw-stock fetch mops.material-info-detail --stock-id 2395 --market sii --seq-no 4 --spoke-date 20250227 --spoke-time 143238 --format json
```

- 主要欄位：`stock_id`, `stock_name`, `seq_no`, `announcement_date`, `announcement_time`, `spokesperson`, `subject`, `clause`, `event_date`, `description`
- 常見用途：取得重大訊息正文、公告條款、事實發生日、發言人資訊，支援事件研究與風險監控。
