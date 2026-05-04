# 資料集指南

這份文件整理 `tw-stock` 目前可抓取的每一種資料。每個資料集都包含簡介、參數、範例指令、主要欄位與常見用途。

範例日期多使用 `2026-04-30`；實際使用時請改成需要查詢的交易日或財報期間。逐筆成交與部分期貨資料量可能很大，探索時建議搭配 `--limit`。

## 參數速查

- `date`：交易日，格式為 `YYYY-MM-DD`。
- `year`：西元年或民國年，MOPS 會自動轉成來源端需要的民國年。
- `month`：月份，適用於 MOPS 月營收。
- `quarter`：季度，值為 `1` 到 `4`。
- `market`：MOPS 市場別，預設 `sii`；可用值為 `sii`、`otc`、`rotc`、`pub`。
- `foreign`：MOPS 月營收外國公司旗標，預設 `0`。

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
