from __future__ import annotations

import pandas as pd

from tw_stock_cli.crawlers.mops.common import company_statement_form_data
from tw_stock_cli.crawlers.mops.common import has_no_data
from tw_stock_cli.crawlers.mops.common import normalize_company_statement_table
from tw_stock_cli.crawlers.mops.common import statement_form_data
from tw_stock_cli.crawlers.mops.company_basic_info import company_basic_info_form_data
from tw_stock_cli.crawlers.mops.company_basic_info import normalize_company_basic_info_table
from tw_stock_cli.crawlers.mops.company_equity_changes import normalize_equity_changes_table
from tw_stock_cli.crawlers.mops.annual_report_electronic_book import (
    electronic_book_form_data,
)
from tw_stock_cli.crawlers.mops.annual_report_electronic_book import (
    parse_electronic_book_html,
)
from tw_stock_cli.crawlers.mops.asset_acquisition_disposal import (
    asset_acquisition_disposal_query_form_data,
)
from tw_stock_cli.crawlers.mops.asset_acquisition_disposal import (
    parse_asset_acquisition_disposal_html,
)
from tw_stock_cli.crawlers.mops.asset_acquisition_disposal_financial import (
    asset_acquisition_disposal_financial_query_form_data,
)
from tw_stock_cli.crawlers.mops.asset_acquisition_disposal_financial import (
    parse_asset_acquisition_disposal_financial_detail_html,
)
from tw_stock_cli.crawlers.mops.dividend_distribution import dividend_distribution_form_data
from tw_stock_cli.crawlers.mops.dividend_distribution import normalize_dividend_distribution_table
from tw_stock_cli.crawlers.mops.director_supervisor_remuneration import (
    director_supervisor_remuneration_form_data,
)
from tw_stock_cli.crawlers.mops.director_supervisor_remuneration import (
    parse_director_supervisor_remuneration_html,
)
from tw_stock_cli.crawlers.mops.board_attendance_training import (
    board_attendance_training_form_data,
)
from tw_stock_cli.crawlers.mops.board_attendance_training import (
    parse_board_attendance_training_html,
)
from tw_stock_cli.crawlers.mops.company_governance_structure import (
    company_governance_structure_form_data,
)
from tw_stock_cli.crawlers.mops.company_governance_structure import (
    parse_company_governance_structure_html,
)
from tw_stock_cli.crawlers.mops.employee_benefit_expense import (
    employee_salary_form_data,
)
from tw_stock_cli.crawlers.mops.employee_benefit_expense import normalize_employee_table
from tw_stock_cli.crawlers.mops.employee_welfare_policy import (
    employee_welfare_policy_form_data,
)
from tw_stock_cli.crawlers.mops.employee_welfare_policy import (
    parse_employee_welfare_policy_html,
)
from tw_stock_cli.crawlers.mops.esg_company_disclosure import (
    esg_company_disclosure_form_data,
)
from tw_stock_cli.crawlers.mops.esg_company_disclosure import (
    parse_esg_company_disclosure_html,
)
from tw_stock_cli.crawlers.mops.ex_dividend_announcement import (
    ex_dividend_announcement_form_data,
)
from tw_stock_cli.crawlers.mops.ex_dividend_announcement import (
    normalize_ex_dividend_table,
)
from tw_stock_cli.crawlers.mops.endorsement_guarantee import (
    parse_endorsement_guarantee_html,
)
from tw_stock_cli.crawlers.mops.fund_lending import parse_fund_lending_html
from tw_stock_cli.crawlers.mops.fund_lending import lending_endorsement_form_data
from tw_stock_cli.crawlers.mops.full_time_employee_salary import (
    full_time_employee_salary_form_data,
)
from tw_stock_cli.crawlers.mops.full_time_employee_salary import (
    parse_full_time_employee_salary_html,
)
from tw_stock_cli.crawlers.mops.functional_committee import functional_committee_form_data
from tw_stock_cli.crawlers.mops.functional_committee import (
    parse_functional_committee_html,
)
from tw_stock_cli.crawlers.mops.independent_director_profile import (
    independent_director_profile_form_data,
)
from tw_stock_cli.crawlers.mops.independent_director_profile import (
    parse_independent_director_profile_html,
)
from tw_stock_cli.crawlers.mops.insider_shareholding_change import (
    insider_shareholding_change_form_data,
)
from tw_stock_cli.crawlers.mops.insider_shareholding_change import (
    normalize_insider_shareholding_change_table,
)
from tw_stock_cli.crawlers.mops.insider_shareholding_change import published_report_url
from tw_stock_cli.crawlers.mops.insider_shareholding_detail import (
    insider_shareholding_detail_form_data,
)
from tw_stock_cli.crawlers.mops.insider_shareholding_detail import (
    parse_insider_shareholding_detail_html,
)
from tw_stock_cli.crawlers.mops.insider_holding_company_list import (
    insider_holding_company_list_form_data,
)
from tw_stock_cli.crawlers.mops.insider_holding_company_list import (
    parse_insider_holding_company_list_html,
)
from tw_stock_cli.crawlers.mops.insider_holding_detail import (
    insider_holding_detail_form_data,
)
from tw_stock_cli.crawlers.mops.insider_holding_detail import (
    parse_insider_holding_detail_html,
)
from tw_stock_cli.crawlers.mops.insider_pledge_summary import (
    insider_pledge_summary_form_data,
)
from tw_stock_cli.crawlers.mops.insider_pledge_summary import (
    normalize_insider_pledge_summary_table,
)
from tw_stock_cli.crawlers.mops.insider_pledge_ratio_summary import (
    insider_pledge_ratio_summary_form_data,
)
from tw_stock_cli.crawlers.mops.insider_pledge_ratio_summary import (
    normalize_insider_pledge_ratio_summary_table,
)
from tw_stock_cli.crawlers.mops.insider_transfer_common import parse_transfer_html
from tw_stock_cli.crawlers.mops.insider_transfer_common import transfer_form_data
from tw_stock_cli.crawlers.mops.investor_conference import (
    investor_conference_form_data,
)
from tw_stock_cli.crawlers.mops.investor_conference import (
    normalize_investor_conference_table,
)
from tw_stock_cli.crawlers.mops.investor_conference import (
    presentation_file_download_url,
)
from tw_stock_cli.crawlers.mops.material_info import material_info_form_data
from tw_stock_cli.crawlers.mops.material_info import parse_material_info_html
from tw_stock_cli.crawlers.mops.material_info_detail import (
    material_info_detail_form_data,
)
from tw_stock_cli.crawlers.mops.material_info_detail import (
    parse_material_info_detail_html,
)
from tw_stock_cli.crawlers.mops.manager_compensation_distribution import (
    manager_compensation_distribution_form_data,
)
from tw_stock_cli.crawlers.mops.manager_compensation_distribution import (
    parse_manager_compensation_distribution_html,
)
from tw_stock_cli.crawlers.mops.major_shareholder_relationship import (
    major_shareholder_relationship_form_data,
)
from tw_stock_cli.crawlers.mops.major_shareholder_relationship import (
    parse_major_shareholder_relationship_html,
)
from tw_stock_cli.crawlers.mops.month_revenue import source_url
from tw_stock_cli.crawlers.mops.private_placement import parse_private_placement_html
from tw_stock_cli.crawlers.mops.private_placement import private_placement_form_data
from tw_stock_cli.crawlers.mops.related_party_transaction import (
    parse_related_party_transaction_html,
)
from tw_stock_cli.crawlers.mops.related_party_transaction import (
    related_party_transaction_form_data,
)
from tw_stock_cli.crawlers.mops.related_party_transaction_difference import (
    parse_related_party_transaction_difference_html,
)
from tw_stock_cli.crawlers.mops.related_party_transaction_difference import (
    related_party_transaction_difference_form_data,
)
from tw_stock_cli.crawlers.mops.shareholding_distribution import (
    parse_shareholding_distribution_html,
)
from tw_stock_cli.crawlers.mops.shareholding_distribution import (
    shareholding_distribution_form_data,
)
from tw_stock_cli.crawlers.mops.related_company_reports_electronic_book import (
    electronic_book_form_data as related_company_reports_form_data,
)
from tw_stock_cli.crawlers.mops.shareholder_meeting import (
    normalize_shareholder_meeting_table,
)
from tw_stock_cli.crawlers.mops.sustainability_report import (
    file_stream_url,
)
from tw_stock_cli.crawlers.mops.sustainability_report import (
    normalize_sustainability_report_rows,
)
from tw_stock_cli.crawlers.mops.sustainability_report import (
    sustainability_report_form_data,
)
from tw_stock_cli.crawlers.mops.sustainability_report import (
    sustainability_report_payload,
)
from tw_stock_cli.crawlers.mops.sustainability_report import to_ad_year
from tw_stock_cli.crawlers.mops.shareholder_meeting import shareholder_meeting_form_data
from tw_stock_cli.crawlers.mops.treasury_stock_buyback import (
    parse_treasury_stock_buyback_detail_html,
)
from tw_stock_cli.crawlers.mops.treasury_stock_buyback import (
    parse_treasury_stock_buyback_list_html,
)
from tw_stock_cli.crawlers.mops.treasury_stock_buyback import (
    treasury_stock_buyback_query_form_data,
)
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


def test_mops_company_statement_form_data_uses_source_parameter_names() -> None:
    form_data = company_statement_form_data(
        {"stock_id": "2395", "kind": "all", "year": 114, "quar": 4}
    )

    assert form_data == {
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
        "TYPEK": "all",
        "co_id": "2395",
        "year": 114,
        "season": "04",
    }


def test_normalize_company_statement_table_keeps_cash_flow_line_items() -> None:
    columns = pd.MultiIndex.from_tuples(
        [
            ("民國114年第4季", "單位：新台幣仟元", "會計項目", "Unnamed: 0_level_3"),
            ("民國114年第4季", "單位：新台幣仟元", "114年度", "金額"),
            ("民國114年第4季", "單位：新台幣仟元", "113年度", "金額"),
            (
                "民國114年第4季",
                "單位：新台幣仟元",
                "Unnamed: 3_level_2",
                "Unnamed: 3_level_3",
            ),
        ]
    )
    table = pd.DataFrame(
        [
            ["營業活動之淨現金流入（流出）", 9902694, 10510851, None],
            ["　　取得不動產、廠房及設備", -2823514, -1475070, None],
        ],
        columns=columns,
    )

    result = normalize_company_statement_table(
        table,
        "本資料由研華公司提供",
        {"stock_id": "2395", "year": 114, "quar": 4},
        "cash_flow",
    )

    assert list(result.columns) == [
        "stock_id",
        "stock_name",
        "report_year",
        "quarter",
        "statement",
        "item",
        "indent_level",
        "114年度_amount",
        "113年度_amount",
    ]
    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "stock_name": "研華",
        "report_year": 114,
        "quarter": 4,
        "statement": "cash_flow",
        "item": "營業活動之淨現金流入（流出）",
        "indent_level": 0,
        "114年度_amount": 9902694,
        "113年度_amount": 10510851,
    }
    assert result.iloc[1]["item"] == "取得不動產、廠房及設備"
    assert result.iloc[1]["indent_level"] == 2


def test_mops_company_basic_info_form_data_supports_market_and_industry() -> None:
    form_data = company_basic_info_form_data({"kind": "sii", "industry_code": "25"})

    assert form_data == {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "TYPEK": "sii",
        "code": "25",
    }


def test_normalize_company_basic_info_table_renames_core_columns() -> None:
    table = pd.DataFrame(
        [
            {
                "公司 代號": "2395",
                "公司名稱": "研華股份有限公司",
                "公司簡稱": "研華",
                "產業類別": "電腦及週邊設備業",
                "董事長": "劉克振",
                "實收資本額(元)": 8682544790,
            }
        ]
    )

    result = normalize_company_basic_info_table(table)

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "stock_name": "研華股份有限公司",
        "short_name": "研華",
        "industry": "電腦及週邊設備業",
        "chairman": "劉克振",
        "paid_in_capital": 8682544790,
    }


def test_normalize_equity_changes_table_uses_first_row_as_columns() -> None:
    columns = pd.MultiIndex.from_tuples(
        [
            ("民國114年度", "單位：新台幣仟元"),
            ("民國114年度", "單位：新台幣仟元.1"),
            ("民國114年度", "單位：新台幣仟元.2"),
        ]
    )
    table = pd.DataFrame(
        [
            ["會計項目", "普通股股本", "資本公積"],
            ["期初餘額", 8634322, 11156003],
        ],
        columns=columns,
    )

    result = normalize_equity_changes_table(
        table,
        "本資料由研華公司提供",
        {"stock_id": "2395", "year": 114, "quar": 4},
    )

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "stock_name": "研華",
        "report_year": 114,
        "quarter": 4,
        "statement_year": 114,
        "statement": "equity_changes",
        "item": "期初餘額",
        "indent_level": 0,
        "普通股股本": 8634322,
        "資本公積": 11156003,
    }


def test_dividend_distribution_form_data_uses_year_range_parameters() -> None:
    form_data = dividend_distribution_form_data(
        {"stock_id": "2395", "kind": "all", "year": 114}
    )

    assert form_data["co_id"] == "2395"
    assert form_data["date1"] == 114
    assert form_data["date2"] == 114
    assert form_data["qryType"] == "1"


def test_normalize_dividend_distribution_table_renames_core_columns() -> None:
    columns = pd.MultiIndex.from_tuples(
        [
            ("決議（擬議） 進度", "決議（擬議） 進度", "決議（擬議） 進度"),
            ("股利所屬 年(季)度", "股利所屬 年(季)度", "股利所屬 年(季)度"),
            ("股東配發內容", "盈餘分配 之現金股利 (元/股)", "盈餘分配 之現金股利 (元/股)"),
            ("股利分派之公司章程", "股利分派之公司章程", "股利分派之公司章程"),
        ]
    )
    table = pd.DataFrame(
        [["董事會決議", "113年 年度", 8.4, "每年分配不低於30%"]],
        columns=columns,
    )

    result = normalize_dividend_distribution_table(
        table,
        "本資料由　(上市公司) 研華　公司提供",
        {"stock_id": "2395", "year": 114},
    )

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "stock_name": "研華",
        "query_year": 114,
        "resolution_status": "董事會決議",
        "dividend_year": "113年 年度",
        "cash_dividend_per_share": 8.4,
        "policy_text": "每年分配不低於30%",
    }


def test_ex_dividend_announcement_form_data_supports_company_and_date_range() -> None:
    form_data = ex_dividend_announcement_form_data(
        {
            "stock_id": "2395",
            "kind": "sii",
            "year": 114,
            "month": 7,
            "start_day": 1,
            "end_day": 31,
        }
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["co_id_1"] == "2395"
    assert form_data["co_id_2"] == "2395"
    assert form_data["year"] == 114
    assert form_data["month"] == "7"
    assert form_data["b_date"] == "1"
    assert form_data["e_date"] == "31"
    assert form_data["type"] == "1"


def test_normalize_ex_dividend_table_renames_core_columns() -> None:
    columns = pd.MultiIndex.from_tuples(
        [
            ("公司代號", "公司代號"),
            ("公司名稱", "公司名稱"),
            ("股利所屬期間", "股利所屬期間"),
            ("權利分派基準日", "權利分派基準日"),
            ("現金股利", "盈餘分配之股東現金股利(元/股)"),
            ("現金股利", "除息交易日"),
            ("現金股利", "現金股利發放日"),
            ("公告日期", "公告日期"),
            ("公告時間", "公告時間"),
        ]
    )
    table = pd.DataFrame(
        [
            [
                "2395",
                "研華",
                "113年",
                "114/07/25",
                8.39237117,
                "114/07/17",
                "114/08/08",
                "114/07/02",
                "16:37:17",
            ]
        ],
        columns=columns,
    )

    result = normalize_ex_dividend_table(
        table,
        "適用停止過戶期間規定之公司",
        {"year": 114},
    )

    assert result.iloc[0].to_dict() == {
        "query_year": 114,
        "source_section": "適用停止過戶期間規定之公司",
        "stock_id": "2395",
        "stock_name": "研華",
        "dividend_period": "113年",
        "record_date": "114/07/25",
        "cash_dividend_from_earnings_per_share": 8.39237117,
        "ex_dividend_date": "114/07/17",
        "cash_dividend_payment_date": "114/08/08",
        "announcement_date": "114/07/02",
        "announcement_time": "16:37:17",
    }


def test_investor_conference_form_data_supports_company_and_month() -> None:
    form_data = investor_conference_form_data(
        {"stock_id": "2395", "kind": "sii", "year": 114, "month": 3}
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["co_id"] == "2395"
    assert form_data["year"] == 114
    assert form_data["month"] == "3"


def test_insider_shareholding_change_form_data_uses_monthly_report_params() -> None:
    form_data = insider_shareholding_change_form_data(
        {"kind": "sii", "year": 114, "month": 3}
    )

    assert form_data == {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "TYPEK": "sii",
        "year": 114,
        "month": "03",
    }


def test_published_report_url_extracts_twse_static_report() -> None:
    html = """
    <input type='hidden' name='run' value="var w1=window.open(
    'https://siis.twse.com.tw/publish/sii/114IRB110_03.HTM','');">
    """

    assert (
        published_report_url(html)
        == "https://siis.twse.com.tw/publish/sii/114IRB110_03.HTM"
    )


def test_normalize_insider_shareholding_change_table_splits_company_column() -> None:
    table = pd.DataFrame(
        [
            [
                "公 司 名 稱",
                "實際發行股票總額",
                "增加股數",
                "減少股數",
                "實際持有股數",
                "佔股份總額%",
                "經理人持股",
                "大股東持股",
            ],
            [
                "2395研華股份有限公司",
                "864,167,125",
                "0",
                "0",
                "252,346,429",
                "29.20",
                "735,143",
                "313,292,036",
            ],
        ]
    )

    result = normalize_insider_shareholding_change_table(
        table, {"year": 114, "month": 3}
    )

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "stock_name": "研華股份有限公司",
        "query_year": 114,
        "query_month": 3,
        "report_ym": "11403",
        "issued_shares": 864167125,
        "directors_supervisors_increase_shares": 0,
        "directors_supervisors_decrease_shares": 0,
        "directors_supervisors_held_shares": 252346429,
        "directors_supervisors_holding_ratio": 29.2,
        "managers_held_shares": 735143,
        "major_shareholders_held_shares": 313292036,
    }


def test_insider_shareholding_detail_form_data_uses_single_company_params() -> None:
    form_data = insider_shareholding_detail_form_data(
        {"stock_id": "2395", "kind": "sii", "year": 114, "month": 3}
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["isnew"] == "false"
    assert form_data["co_id"] == "2395"
    assert form_data["year"] == 114
    assert form_data["month"] == "03"


def test_parse_insider_shareholding_detail_html_splits_share_blocks() -> None:
    html = """
    <table class='noBorder'><tr><td class='compName'>
    <b>本資料由　(上市公司) 研華　公司提供</b>
    </td></tr></table>
    <table class='hasBorder'>
      <tr class='tblHead'><th colspan='7'>資料年月：11403</th></tr>
      <tr class='tblHead'>
        <th>身份別</th><th>姓　名</th><th>持股種類</th>
        <th>選任當時持有股數<br>上月實際持有股數<br>截至上月底保留運用決定權信託股數<br>截至上月底累計設質<br>截至上月底累計持有私募股票股數</th>
        <th>本月增加</th><th>本月減少</th><th>本月底</th>
      </tr>
      <tr class='odd'>
        <td>董事本人</td><td>研本投資股份有限公司</td><td>普通股</td>
        <td>90,295,663<br>99,314,136<br>0<br>0<br>0</td>
        <td>0<br>0<br>0<br>0<br>0</td>
        <td>0<br>0<br>0<br>0<br>0</td>
        <td>99,314,136<br>0<br>0<br>0<br>0<br>身份別備註：<br>兼大股東</td>
      </tr>
    </table>
    """

    result = parse_insider_shareholding_detail_html(
        html, {"stock_id": "2395", "year": 114, "month": 3}
    )

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "stock_name": "研華",
        "query_year": 114,
        "query_month": 3,
        "report_ym": "11403",
        "role": "董事本人",
        "person_name": "研本投資股份有限公司",
        "share_type": "普通股",
        "elected_shares": 90295663,
        "previous_month_held_shares": 99314136,
        "previous_month_trust_shares": 0,
        "previous_month_pledged_shares": 0,
        "previous_month_private_shares": 0,
        "increase_centralized_shares": 0,
        "increase_other_shares": 0,
        "increase_private_shares": 0,
        "increase_trust_shares": 0,
        "increase_pledged_shares": 0,
        "decrease_centralized_shares": 0,
        "decrease_other_shares": 0,
        "decrease_private_shares": 0,
        "decrease_trust_shares": 0,
        "decrease_released_pledge_shares": 0,
        "current_held_shares": 99314136,
        "current_custody_shares": 0,
        "current_trust_shares": 0,
        "current_pledged_shares": 0,
        "current_private_shares": 0,
        "role_notes": "兼大股東",
    }


def test_insider_holding_company_list_form_data_uses_report_ym() -> None:
    form_data = insider_holding_company_list_form_data(
        {"kind": "sii", "industry_code": "25", "year": 114, "month": 3}
    )

    assert form_data["sTYPEK"] == "sii"
    assert form_data["TYPEK"] == "sii"
    assert form_data["skind"] == "25"
    assert form_data["YM"] == "11403"


def test_parse_insider_holding_company_list_html_returns_available_companies() -> None:
    html = """
    <table class='hasBorder'>
      <tr class='tblHead'><th>公司代號</th><th>公司簡稱</th><th>&nbsp;</th></tr>
      <tr><td>2395</td><td>研華</td><td><input value='詳細資料'></td></tr>
    </table>
    """

    result = parse_insider_holding_company_list_html(
        html, {"kind": "sii", "year": 114, "month": 3}
    )

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "stock_name": "研華",
        "query_year": 114,
        "query_month": 3,
        "report_ym": "11403",
        "market": "sii",
        "detail_available": True,
    }


def test_insider_holding_detail_form_data_uses_single_company_params() -> None:
    form_data = insider_holding_detail_form_data(
        {"stock_id": "2395", "kind": "all", "year": 114, "month": 3}
    )

    assert form_data["TYPEK"] == "all"
    assert form_data["isnew"] == "false"
    assert form_data["co_id"] == "2395"
    assert form_data["year"] == 114
    assert form_data["month"] == "03"


def test_parse_insider_holding_detail_html_normalizes_pledge_ratios() -> None:
    html = """
    <b>本資料由　(上市公司) 研華　公司提供</b>
    <table class='noBorder'><tr><td>資料年月:11403</td></tr></table>
    <table class='hasBorder'>
      <tr><td>職稱</td><td>姓名</td><td>選任時持股</td><td>目前持股</td><td>設質股數</td><td>設質股數佔持股比例</td><td>內部人關係人目前持股合計</td><td>設質股數</td><td>設質比例</td></tr>
      <tr><td>董事長本人</td><td>劉克振</td><td>28,179,467</td><td>27,993,951</td><td>0</td><td>0.00%</td><td>4,701,052</td><td>0</td><td>0.00%</td></tr>
    </table>
    """

    result = parse_insider_holding_detail_html(
        html, {"stock_id": "2395", "year": 114, "month": 3}
    )

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "stock_name": "研華",
        "query_year": 114,
        "query_month": 3,
        "report_ym": "11403",
        "role": "董事長本人",
        "person_name": "劉克振",
        "elected_shares": 28179467,
        "current_shares": 27993951,
        "pledged_shares": 0,
        "pledged_ratio": 0.0,
        "related_current_shares": 4701052,
        "related_pledged_shares": 0,
        "related_pledged_ratio": 0.0,
    }


def test_insider_transfer_form_data_uses_final_ajax_endpoint_params() -> None:
    form_data = transfer_form_data(
        {
            "stock_id": "1210",
            "kind": "all",
            "year": 114,
            "start_month": 3,
            "end_month": 3,
        },
        sstep=1,
    )

    assert form_data == {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "true",
        "TYPEK": "all",
        "co_id": "1210",
        "year": 114,
        "smonth": "03",
        "emonth": "03",
        "isnew": "false",
        "sstep": "1",
    }


def test_parse_insider_transfer_declaration_html_normalizes_columns() -> None:
    html = """
    <table class='hasBorder'>
      <tr><th rowspan='2'>異動情形</th><th rowspan='2'>申報日期</th><th rowspan='2'>公司<br>代號</th><th rowspan='2'>公司名稱</th><th rowspan='2'>申報人身分</th><th rowspan='2'>姓名</th><th colspan='2'>預定轉讓方式及股數</th><th rowspan='2'>每日於盤中交易<br>最大得轉讓股數</th><th rowspan='2'>受讓人</th><th colspan='2'>目前持有股數</th><th colspan='2'>預定轉讓總股數</th><th colspan='2'>預定轉讓後持股</th><th rowspan='2'>有效轉讓期間</th><th rowspan='2'>是否申報持<br>股未完成轉讓</th></tr>
      <tr><th>轉讓方式</th><th>轉讓股數</th><th>自有持股</th><th>保留運用決定<br>權信託股數</th><th>自有持股</th><th>保留運用決定<br>權信託股數</th><th>自有持股</th><th>保留運用決定<br>權信託股數</th></tr>
      <tr><td></td><td>114/03/14</td><td>1210</td><td>大成</td><td>法人董事代表人配偶</td><td>韓家寰之配偶</td><td>一般交易</td><td>300,000</td><td>924,767</td><td></td><td>348,799</td><td>0</td><td>300,000</td><td>0</td><td>48,799</td><td>0</td><td>114/03/17 ~ 114/04/16</td><td>是</td></tr>
    </table>
    """

    result = parse_transfer_html(
        html,
        {"year": 114, "start_month": 3, "end_month": 3},
        report_type="declaration_summary",
    )

    assert result.iloc[0].to_dict() == {
        "query_year": 114,
        "start_month": 3,
        "end_month": 3,
        "report_type": "declaration_summary",
        "change_status": None,
        "declaration_date": "114/03/14",
        "stock_id": "1210",
        "stock_name": "大成",
        "declarer_role": "法人董事代表人配偶",
        "declarer_name": "韓家寰之配偶",
        "transfer_method": "一般交易",
        "planned_transfer_shares": 300000,
        "max_daily_intraday_transfer_shares": 924767,
        "transferee": None,
        "current_own_shares": 348799,
        "current_trust_shares": 0,
        "planned_transfer_own_shares": 300000,
        "planned_transfer_trust_shares": 0,
        "post_transfer_own_shares": 48799,
        "post_transfer_trust_shares": 0,
        "effective_transfer_period": "114/03/17 ~ 114/04/16",
        "untransferred_report_filed": "是",
    }


def test_parse_insider_transfer_untransferred_html_normalizes_columns() -> None:
    html = """
    <table class='hasBorder'>
      <tr><th rowspan='2'>申報日期</th><th rowspan='2'>公司代號</th><th rowspan='2'>公司名稱</th><th rowspan='2'>申報人身分</th><th rowspan='2'>姓名</th><th colspan='2'>未轉讓股數</th><th colspan='2'>目前持股</th><th colspan='2'>原申報預定轉讓股數</th><th rowspan='2'>未轉讓理由</th></tr>
      <tr><th>自有持股</th><th>保留運用決定<br>權信託股數</th><th>自有持股</th><th>保留運用決定<br>權信託股數</th><th>自有持股</th><th>保留運用決定<br>權信託股數</th></tr>
      <tr><td>114/03/20</td><td>2254</td><td>巨鎧精密-創</td><td>董事本人</td><td>昇祈投資有限公司</td><td>2,000,000</td><td>0</td><td>19,287,648</td><td>0</td><td>2,000,000</td><td>0</td><td>股價不理想</td></tr>
    </table>
    """

    result = parse_transfer_html(
        html,
        {"year": 114, "start_month": 3, "end_month": 3},
        report_type="untransferred_summary",
    )

    assert result.iloc[0].to_dict() == {
        "query_year": 114,
        "start_month": 3,
        "end_month": 3,
        "report_type": "untransferred_summary",
        "declaration_date": "114/03/20",
        "stock_id": "2254",
        "stock_name": "巨鎧精密-創",
        "declarer_role": "董事本人",
        "declarer_name": "昇祈投資有限公司",
        "untransferred_own_shares": 2000000,
        "untransferred_trust_shares": 0,
        "current_own_shares": 19287648,
        "current_trust_shares": 0,
        "original_planned_transfer_own_shares": 2000000,
        "original_planned_transfer_trust_shares": 0,
        "untransferred_reason": "股價不理想",
    }


def test_insider_pledge_summary_form_data_uses_monthly_report_params() -> None:
    form_data = insider_pledge_summary_form_data(
        {"kind": "sii", "year": 114, "month": 3}
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["year"] == 114
    assert form_data["month"] == "03"


def test_normalize_insider_pledge_summary_table_splits_company_column() -> None:
    table = pd.DataFrame(
        [
            ["公 司 名 稱", "實際持有股數", "設定股數", "解除股數", "累計設定股數", "佔持股比例%", "經理人持股", "大股東持股", "經理人大股東已設定股數", "佔持股比例%"],
            ["2395研華股份有限公司", "252,346,429", "0", "0", "0", "0.00", "735,143", "313,292,036", "0", "0.00"],
        ]
    )

    result = normalize_insider_pledge_summary_table(
        table, {"year": 114, "month": 3}
    )

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "stock_name": "研華股份有限公司",
        "query_year": 114,
        "query_month": 3,
        "report_ym": "11403",
        "directors_supervisors_held_shares": 252346429,
        "directors_supervisors_pledged_shares": 0,
        "directors_supervisors_released_pledge_shares": 0,
        "directors_supervisors_cumulative_pledged_shares": 0,
        "directors_supervisors_pledged_ratio": 0.0,
        "managers_held_shares": 735143,
        "major_shareholders_held_shares": 313292036,
        "managers_major_shareholders_pledged_shares": 0,
        "managers_major_shareholders_pledged_ratio": 0.0,
    }


def test_insider_pledge_ratio_summary_form_data_uses_monthly_report_params() -> None:
    form_data = insider_pledge_ratio_summary_form_data(
        {"kind": "sii", "year": 114, "month": 3}
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["year"] == 114
    assert form_data["month"] == "03"


def test_normalize_insider_pledge_ratio_summary_table_flattens_buckets() -> None:
    table = pd.DataFrame(
        [
            ["百 分 比", "公 司 名 稱", "公 司 名 稱"],
            ["90 以上", "6431 光麗-KY 99.99", "6695 芯鼎 99.99"],
            [None, "6141 柏承 91.54", None],
        ]
    )

    result = normalize_insider_pledge_ratio_summary_table(
        table, {"year": 114, "month": 3}
    )

    assert result.to_dict("records") == [
        {
            "stock_id": "6431",
            "stock_name": "光麗-KY",
            "query_year": 114,
            "query_month": 3,
            "report_ym": "11403",
            "pledge_ratio_bucket": "90 以上",
            "pledge_ratio": 99.99,
        },
        {
            "stock_id": "6695",
            "stock_name": "芯鼎",
            "query_year": 114,
            "query_month": 3,
            "report_ym": "11403",
            "pledge_ratio_bucket": "90 以上",
            "pledge_ratio": 99.99,
        },
        {
            "stock_id": "6141",
            "stock_name": "柏承",
            "query_year": 114,
            "query_month": 3,
            "report_ym": "11403",
            "pledge_ratio_bucket": "90 以上",
            "pledge_ratio": 91.54,
        },
    ]


def test_normalize_investor_conference_table_renames_core_columns() -> None:
    columns = pd.MultiIndex.from_tuples(
        [
            ("公司代號", "公司代號"),
            ("公司名稱", "公司名稱"),
            ("召開法人說明會日期", "召開法人說明會日期"),
            ("召開法人說明會時間", "召開法人說明會時間"),
            ("召開法人說明會地點", "召開法人說明會地點"),
            ("法人說明會擇要訊息", "法人說明會擇要訊息"),
            ("法人說明會簡報內容", "中文檔案"),
            ("法人說明會簡報內容", "英文檔案"),
            ("公司網站是否提供法人說明會相關資訊", "公司網站是否提供法人說明會相關資訊"),
            ("影音連結資訊", "影音連結資訊"),
        ]
    )
    table = pd.DataFrame(
        [
            [
                "2395",
                "研華",
                "114/03/05",
                "14:00",
                "研華內湖總部",
                "公布財務報告及業績展望",
                "239520250305M001.pdf",
                "239520250305E001.pdf",
                "https://www.advantech.com/zh-tw/investor/investor-events",
                "影音資訊網址：https://example.test/video",
            ]
        ],
        columns=columns,
    )

    result = normalize_investor_conference_table(table, {"year": 114})

    assert result.iloc[0].to_dict() == {
        "query_year": 114,
        "stock_id": "2395",
        "stock_name": "研華",
        "conference_date": "114/03/05",
        "conference_time": "14:00",
        "location": "研華內湖總部",
        "summary": "公布財務報告及業績展望",
        "presentation_zh_file": "239520250305M001.pdf",
        "presentation_en_file": "239520250305E001.pdf",
        "presentation_zh_download_url": presentation_file_download_url(
            "239520250305M001.pdf"
        ),
        "presentation_en_download_url": presentation_file_download_url(
            "239520250305E001.pdf"
        ),
        "company_ir_url": "https://www.advantech.com/zh-tw/investor/investor-events",
        "media_links": "影音資訊網址：https://example.test/video",
    }


def test_employee_welfare_policy_form_data_uses_single_company_params() -> None:
    form_data = employee_welfare_policy_form_data(
        {"stock_id": "2395", "kind": "all", "year": 114}
    )

    assert form_data["step"] == "0"
    assert form_data["TYPEK"] == "all"
    assert form_data["co_id"] == "2395"
    assert form_data["year"] == 114


def test_parse_employee_welfare_policy_html_flattens_sections() -> None:
    html = """
    <p align="center"><b>公司代號：</b>2395<b>公司名稱：</b>研華<b>申報年度：</b>114年</p>
    <p align="left">說明：公司係揭露113年度員工福利政策及權益維護措施</p>
    <table>
      <tr><th>項目</th><th>內容</th></tr>
      <tr><th>員工福利政策</th><td><pre>福利文字</pre></td></tr>
      <tr><th>員工權益維護措施</th><td><pre>權益文字</pre></td></tr>
    </table>
    <table>
      <tr><td colspan="8">平均員工薪資調整情形</td></tr>
      <tr><td>預計調薪%</td><td>備註</td><td>實際調薪%</td><td>備註</td><td>非經理人員工調薪%</td><td>備註</td><td>經理人員工調薪%</td><td>備註</td></tr>
      <tr><td>3</td><td>預計</td><td>2</td><td>實際</td><td>4</td><td>非經理人</td><td>1</td><td>經理人</td></tr>
    </table>
    <table>
      <tr><td colspan="4">新進員工之平均起薪金額</td></tr>
      <tr><td>碩士及以上</td><td>大專校院</td><td>高中及以下</td><td>備註</td></tr>
      <tr><td>50000</td><td>42000</td><td>32000</td><td>揭露</td></tr>
    </table>
    """

    result = parse_employee_welfare_policy_html(html, {"stock_id": "2395", "year": 114})

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "stock_name": "研華",
        "report_year": 114,
        "disclosure_year": 113,
        "section": "policy",
        "item": "員工福利政策",
        "value": "福利文字",
        "note": None,
    }
    assert "actual_salary_adjustment_ratio" in set(result["item"])
    assert "master_and_above_starting_salary" in set(result["item"])


def test_esg_company_disclosure_form_data_uses_redirect_query_params() -> None:
    form_data = esg_company_disclosure_form_data(
        {"stock_id": "2395", "kind": "sii", "year": 113}
    )

    assert form_data == {
        "step": "2",
        "TYPEK": "sii",
        "firstin": "1",
        "co_id": "2395",
        "YEAR": 113,
    }


def test_parse_esg_company_disclosure_html_returns_inquiry_url() -> None:
    html = """
    <form name='autoRunScript'>
      <input type='hidden' name='run' value="var w1=window.open('https://esggenplus.twse.com.tw/inquiry/info/individual?companyCode=2395&year=2024','');">
    </form>
    """

    result = parse_esg_company_disclosure_html(
        html,
        {"stock_id": "2395", "year": 113},
    )

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "mops_year": 113,
        "report_year": 2024,
        "inquiry_url": "https://esggenplus.twse.com.tw/inquiry/info/individual?companyCode=2395&year=2024",
    }


def test_shareholder_meeting_form_data_supports_company_and_date_range() -> None:
    form_data = shareholder_meeting_form_data(
        {
            "stock_id": "2395",
            "kind": "sii",
            "year": 114,
            "month": 5,
            "start_day": 1,
            "end_day": 31,
        }
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["co_id1"] == "2395"
    assert form_data["co_id2"] == "2395"
    assert form_data["YEAR"] == 114
    assert form_data["MONTH"] == "5"
    assert form_data["SDAY"] == "1"
    assert form_data["EDAY"] == "31"
    assert form_data["SK"] == "1"


def test_normalize_shareholder_meeting_table_drops_rowspan_placeholder_row() -> None:
    table = pd.DataFrame(
        [
            {
                "公司代號": 2395,
                "公司名稱": "研華",
                "股東常(臨時)會日期": "常會",
                "股東常(臨時)會日期.1": "114/05/29",
                "停止過戶起訖日期": "起",
                "停止過戶起訖日期.1": "迄",
                "召開方式": "實體並以視訊輔助",
                "開會地點": "台北市內湖區瑞光路26巷20弄1號B1",
                "行使期間": "自114年04月29日至114年05月26日止",
                "投票網址": "https://stockservices.tdcc.com.tw",
                "公告日期": "114/03/12",
                "公告時間": "15:37:02",
            },
            {
                "公司代號": 2395,
                "公司名稱": "研華",
                "股東常(臨時)會日期": "常會",
                "股東常(臨時)會日期.1": "114/05/29",
                "停止過戶起訖日期": "114/03/31",
                "停止過戶起訖日期.1": "114/05/29",
                "召開方式": "實體並以視訊輔助",
                "開會地點": "台北市內湖區瑞光路26巷20弄1號B1",
                "行使期間": "自114年04月29日至114年05月26日止",
                "投票網址": "https://stockservices.tdcc.com.tw",
                "公告日期": "114/03/12",
                "公告時間": "15:37:02",
            },
        ]
    )

    result = normalize_shareholder_meeting_table(table, {"year": 114})

    assert len(result) == 1
    assert result.iloc[0].to_dict() == {
        "query_year": 114,
        "stock_id": "2395",
        "stock_name": "研華",
        "meeting_type": "常會",
        "meeting_date": "114/05/29",
        "book_closure_start": "114/03/31",
        "book_closure_end": "114/05/29",
        "meeting_method": "實體並以視訊輔助",
        "location": "台北市內湖區瑞光路26巷20弄1號B1",
        "e_voting_period": "自114年04月29日至114年05月26日止",
        "e_voting_url": "https://stockservices.tdcc.com.tw",
        "announcement_date": "114/03/12",
        "announcement_time": "15:37:02",
    }


def test_material_info_form_data_uses_date_range_parameters() -> None:
    form_data = material_info_form_data(
        {
            "stock_id": "2395",
            "kind": "all",
            "year": 115,
            "month": 5,
            "start_day": 1,
            "end_day": 5,
        }
    )

    assert form_data["co_id"] == "2395"
    assert form_data["year"] == 115
    assert form_data["month"] == "05"
    assert form_data["b_date"] == "01"
    assert form_data["e_date"] == "05"


def test_parse_material_info_html_extracts_detail_keys() -> None:
    html = """
    <table class='hasBorder'>
      <tr class='tblHead'>
        <th>公司代號</th><th>公司名稱</th><th>發言日期</th>
        <th>發言時間</th><th>主旨</th><th>&nbsp;</th>
      </tr>
      <tr>
        <td>&nbsp;2395</td><td>&nbsp;研華</td><td>&nbsp;114/02/27</td>
        <td>&nbsp;14:32:38</td><td><pre>董事會決議股利分派</pre></td>
        <td><input type='button' value='詳細資料'
          onclick="document.t05st01_fm.seq_no.value='4';document.t05st01_fm.spoke_time.value='143238';document.t05st01_fm.spoke_date.value='20250227';document.t05st01_fm.co_id.value='2395';document.t05st01_fm.TYPEK.value='sii';">
        </td>
      </tr>
    </table>
    """

    result = parse_material_info_html(html, {"year": 114})

    assert result.iloc[0].to_dict() == {
        "query_year": 114,
        "source_table": "material_info",
        "stock_id": "2395",
        "stock_name": "研華",
        "announcement_date": "114/02/27",
        "announcement_time": "14:32:38",
        "subject": "董事會決議股利分派",
        "detail_seq_no": "4",
        "detail_spoke_date": "20250227",
        "detail_spoke_time": "143238",
        "detail_type": "sii",
    }


def test_material_info_detail_form_data_uses_detail_keys() -> None:
    form_data = material_info_detail_form_data(
        {
            "stock_id": "2395",
            "kind": "sii",
            "seq_no": "4",
            "spoke_date": "20250227",
            "spoke_time": "143238",
        }
    )

    assert form_data == {
        "encodeURIComponent": "1",
        "firstin": "true",
        "step": "2",
        "off": "1",
        "co_id": "2395",
        "TYPEK": "sii",
        "seq_no": "4",
        "spoke_date": "20250227",
        "spoke_time": "143238",
    }


def test_parse_material_info_detail_html_extracts_announcement_body() -> None:
    html = """
    <html>
      <body>
        本資料由　(上市公司) 2395 研華 　公司提供
        <table class='hasBorder'>
          <tr><th>序號</th><td>4</td><th>發言日期</th><td>114/02/27</td></tr>
          <tr><th>發言時間</th><td>14:32:38</td><th>發言人</th><td>陳清熙</td></tr>
          <tr><th>主旨</th><td colspan='3'>董事會決議股利分派</td></tr>
          <tr><th>符合條款</th><td>第 14 款</td><th>事實發生日</th><td>114/02/27</td></tr>
          <tr><th>說明</th><td colspan='3'><pre>1. 董事會決議日期：114/02/27
2. 現金股利：8.4元</pre></td></tr>
        </table>
        以上資料均由各公司依發言當時所屬市場別之規定申報後，由本公司對外公開，資料如有虛偽不實，均由該公司負責。
      </body>
    </html>
    """

    result = parse_material_info_detail_html(
        html,
        {
            "stock_id": "2395",
            "kind": "sii",
            "seq_no": "4",
            "spoke_date": "20250227",
            "spoke_time": "143238",
        },
    )

    assert result.iloc[0].to_dict() == {
        "stock_id": "2395",
        "detail_seq_no": "4",
        "detail_spoke_date": "20250227",
        "detail_spoke_time": "143238",
        "detail_type": "sii",
        "market_name": "上市公司",
        "stock_name": "研華",
        "seq_no": "4",
        "announcement_date": "114/02/27",
        "announcement_time": "14:32:38",
        "spokesperson": "陳清熙",
        "subject": "董事會決議股利分派",
        "clause": "第 14 款",
        "event_date": "114/02/27",
        "description": "1. 董事會決議日期：114/02/27 2. 現金股利：8.4元",
        "disclaimer": "以上資料均由各公司依發言當時所屬市場別之規定申報後，由本公司對外公開，資料如有虛偽不實，均由該公司負責。",
    }


def test_lending_endorsement_form_data_uses_monthly_company_params() -> None:
    form_data = lending_endorsement_form_data(
        {"stock_id": "1101", "kind": "sii", "year": 114, "month": 3}
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["co_id"] == "1101"
    assert form_data["year"] == 114
    assert form_data["month"] == "03"
    assert form_data["isnew"] == "false"


def test_parse_fund_lending_html_normalizes_detail_rows() -> None:
    html = """
    <table><tr><td>(上市公司)台泥 資金貸與資訊揭露明細表</td></tr></table>
    <table>
      <tr>
        <th>編號 (註2)</th><th>貸出資金之公司</th><th>貸與對象</th>
        <th>是否為關係人</th><th>往來科目 (註3)</th>
        <th>累計至本月止最高餘額 (註4)</th>
        <th>個別子公司本月增(減)金額(註5)_因業務往來金額</th>
        <th>個別子公司本月增(減)金額(註5)_短期融通資金</th>
        <th>期末餘額(註6)</th><th>實際動支金額(註7)</th>
        <th>利率區間</th><th>資金貸與性質 (註8)</th>
        <th>業務往來金額 (註9)</th>
        <th>有短期融通資金必要之原因 (註10)</th>
        <th>提列備抵呆帳金額</th><th>擔保品_名稱</th><th>擔保品_價值</th>
        <th>對個別對象資金貸與限額 (註11)</th><th>資金貸與總限額 (註11)</th>
      </tr>
      <tr>
        <td>1</td><td>台灣水泥股份有限公司</td><td>Hong Kong Cement</td>
        <td>Y</td><td>其他應收款</td><td>100,000</td><td>0</td><td>10,000</td>
        <td>90,000</td><td>80,000</td><td>1.50%</td><td>短期融通資金</td>
        <td>0</td><td>營運週轉</td><td>0</td><td>股票</td><td>50,000</td>
        <td>200,000</td><td>500,000</td>
      </tr>
      <tr><td></td><td>合計</td><td></td><td></td><td></td><td>100,000</td><td colspan="13"></td></tr>
    </table>
    """

    result = parse_fund_lending_html(
        html, {"stock_id": "1101", "kind": "sii", "year": 114, "month": 3}
    )

    assert len(result) == 1
    assert result.iloc[0]["stock_name"] == "台泥"
    assert result.iloc[0]["lender_name"] == "台灣水泥股份有限公司"
    assert result.iloc[0]["borrower_name"] == "Hong Kong Cement"
    assert result.iloc[0]["is_related_party"] == "Y"
    assert result.iloc[0]["ending_balance"] == 90000
    assert result.iloc[0]["short_term_financing_reason"] == "營運週轉"


def test_parse_endorsement_guarantee_html_normalizes_detail_rows() -> None:
    html = """
    <table><tr><td>(上市公司)台泥 背書保證資訊揭露明細表</td></tr></table>
    <table>
      <tr>
        <th>編號 (註2)</th><th>背書保證者公司名稱</th>
        <th>被背書保證對象_公司名稱</th><th>被背書保證對象_關係 (註3)</th>
        <th>對單一企業背書保證之限額 (註4)</th>
        <th>累計至本月止最高餘額 (註5)</th>
        <th>個別子公司本月增(減)金額 (註6)</th>
        <th>期末背書保證餘額 (註7)</th><th>實際動支金額 (註8)</th>
        <th>以財產擔保之背書保證金額 (註9)</th>
        <th>累計背書保證金額佔最近期財務報表淨值之比率</th>
        <th>背書保證最高限額(註4)</th>
        <th>屬母公司 對子公司 背書保證 (註10)</th>
        <th>屬子公司 對母公司 背書保證 (註10)</th>
        <th>屬對大陸 地區背書 保證 (註10)</th>
      </tr>
      <tr>
        <td>1</td><td>台灣水泥股份有限公司</td><td>TCC International</td>
        <td>子公司</td><td>300,000</td><td>250,000</td><td>10,000</td>
        <td>240,000</td><td>200,000</td><td>0</td><td>12.5</td><td>800,000</td>
        <td>Y</td><td>N</td><td>Y</td>
      </tr>
      <tr><td></td><td>合計</td><td colspan="13"></td></tr>
    </table>
    """

    result = parse_endorsement_guarantee_html(
        html, {"stock_id": "1101", "kind": "sii", "year": 114, "month": 3}
    )

    assert len(result) == 1
    assert result.iloc[0]["stock_name"] == "台泥"
    assert result.iloc[0]["guarantor_name"] == "台灣水泥股份有限公司"
    assert result.iloc[0]["guaranteed_party_name"] == "TCC International"
    assert result.iloc[0]["relationship"] == "子公司"
    assert result.iloc[0]["ending_guarantee_balance"] == 240000
    assert result.iloc[0]["is_china_area_guarantee"] == "Y"


def test_related_party_transaction_form_data_uses_report_month() -> None:
    form_data = related_party_transaction_form_data(
        {"stock_id": "8011", "kind": "sii", "year": 113, "month": 9}
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["co_id"] == "8011"
    assert form_data["year"] == 113
    assert form_data["month"] == "09"


def test_parse_related_party_transaction_html_flattens_sections() -> None:
    html = """
    <table><tr><td>台通</td><td>關係人交易申報明細資料查詢</td></tr></table>
    <table><tr><td>113年09月</td></tr><tr><td>【銷貨】</td></tr></table>
    <table>
      <tr>
        <th>關係人名稱</th><th>本月銷貨金額</th>
        <th>占本月合併報表銷貨金額百分比</th>
        <th>本年累計銷貨金額</th><th>占本年合併報表累計銷貨金額百分比</th>
      </tr>
      <tr><td>東豐科技股份有限公司</td><td>726</td><td>0.45</td><td>6781</td><td>0.34</td></tr>
      <tr><td>合計</td><td>726</td><td>0.45</td><td>6781</td><td>0.34</td></tr>
    </table>
    <table><tr><td>【取得資產】</td></tr></table>
    <table>
      <tr>
        <th>關係人名稱</th><th>取得資產項目</th>
        <th>本月取得資產金額</th><th>本年累計取得資產金額</th>
      </tr>
      <tr><td>皇輝科技股份有限公司</td><td>營運通訊設備</td><td>0</td><td>2060</td></tr>
    </table>
    """

    result = parse_related_party_transaction_html(
        html, {"stock_id": "8011", "kind": "sii", "year": 113, "month": 9}
    )

    assert len(result) == 2
    assert result.iloc[0]["stock_name"] == "台通"
    assert result.iloc[0]["transaction_type"] == "銷貨"
    assert result.iloc[0]["related_party_name"] == "東豐科技股份有限公司"
    assert result.iloc[0]["current_month_amount"] == 726
    assert result.iloc[0]["ytd_ratio"] == 0.34
    assert result.iloc[1]["transaction_type"] == "取得資產"
    assert result.iloc[1]["asset_item"] == "營運通訊設備"
    assert result.iloc[1]["ytd_amount"] == 2060


def test_related_party_transaction_difference_form_data_uses_quarter() -> None:
    form_data = related_party_transaction_difference_form_data(
        {"stock_id": "3162", "kind": "otc", "year": 114, "quar": 1}
    )

    assert form_data["TYPEK"] == "otc"
    assert form_data["co_id"] == "3162"
    assert form_data["year"] == 114
    assert form_data["season"] == "1"


def test_parse_related_party_transaction_difference_html_normalizes_rows() -> None:
    html = """
    <table>
      <tr>
        <th>交易類型</th><th>申報數</th><th>會計師查核(核閱)數</th>
        <th>差異數</th><th>差異比率</th><th>差異原因</th><th>因應措施</th>
      </tr>
      <tr>
        <td>銷貨</td><td>10,000</td><td>13,000</td><td>3,000</td>
        <td>30%</td><td>收入認列時點調整</td><td>發布重大訊息</td>
      </tr>
    </table>
    """

    result = parse_related_party_transaction_difference_html(
        html, {"stock_id": "3162", "kind": "otc", "year": 114, "quar": 1}
    )

    assert result.iloc[0].to_dict() == {
        "stock_id": "3162",
        "stock_name": None,
        "market": "otc",
        "report_year": 114,
        "quarter": 1,
        "transaction_type": "銷貨",
        "reported_amount": 10000,
        "audited_reviewed_amount": 13000,
        "difference_amount": 3000,
        "difference_ratio": 30,
        "difference_reason": "收入認列時點調整",
        "countermeasure": "發布重大訊息",
        "remark": None,
    }


def test_director_supervisor_remuneration_form_data_defaults_to_directors() -> None:
    form_data = director_supervisor_remuneration_form_data(
        {"kind": "sii", "year": 113}
    )

    assert form_data == {
        "step": "1",
        "firstin": "ture",
        "off": "1",
        "TYPEK": "sii",
        "year": 113,
        "rid": "1",
        "wid": "A",
        "sid": "2",
    }


def test_parse_director_supervisor_remuneration_html_normalizes_static_report() -> None:
    html = """
    <table>
      <tr>
        <th>產業類別</th><th>公司代號</th><th>公司名稱</th>
        <th>113年支付</th><th>114年支付</th><th>合計</th>
        <th>113年支付</th><th>114年支付</th><th>合計</th>
        <th>董事酬金</th><th>加計兼任員工酬金</th>
        <th>董事酬金</th><th>加計兼任員工酬金</th>
        <th>領取來自子公司以外轉投資事業或母公司酬金</th>
        <th>稅後損益</th><th>每股盈餘</th><th>股東權益報酬率</th>
        <th>實收資本額</th><th>說明</th>
      </tr>
      <tr>
        <td>水泥工業</td><td>1101</td><td>台泥</td>
        <td>30,438,469</td><td>123,167,600</td><td>153,606,069</td>
        <td>77,047,837</td><td>129,557,612</td><td>206,605,449</td>
        <td>1.36</td><td>1.83</td><td>10,413,971</td><td>14,007,149</td>
        <td>0</td><td>11,259,317</td><td>1.45</td><td>5.56</td>
        <td>77,511,817</td><td>依公司章程辦理</td>
      </tr>
    </table>
    """

    result = parse_director_supervisor_remuneration_html(
        html, {"kind": "sii", "year": 113, "role": "A", "report_type": "1"}
    )

    assert result.iloc[0]["stock_id"] == "1101"
    assert result.iloc[0]["stock_name"] == "台泥"
    assert result.iloc[0]["base_remuneration_total"] == 153606069
    assert result.iloc[0]["with_employee_salary_total"] == 206605449
    assert result.iloc[0]["average_base_remuneration"] == 10413971
    assert result.iloc[0]["reasonableness_explanation"] == "依公司章程辦理"


def test_manager_compensation_distribution_form_data_uses_company_range() -> None:
    form_data = manager_compensation_distribution_form_data(
        {"stock_id": "2395", "kind": "all", "year": 113}
    )

    assert form_data["TYPEK"] == "all"
    assert form_data["co_id_1"] == "2395"
    assert form_data["co_id_2"] == "2395"
    assert form_data["year"] == 113


def test_parse_manager_compensation_distribution_html_normalizes_row() -> None:
    html = """
    <table><tr><td>員工酬勞所屬年度：112  分派員工酬勞年度：113</td></tr></table>
    <table>
      <tr>
        <th>公司代號</th><th>公司名稱</th><th>股數</th><th>市價</th>
        <th>金額(A)</th><th>金額(B)</th><th>金額合計(A+B)</th>
        <th>總額(A+B)占稅後純益之比例(%)</th><th>備註</th>
      </tr>
      <tr><td>2395</td><td>研華</td><td>0</td><td>0</td><td>0</td><td>6,919,611</td><td>6,919,611</td><td>0.064</td><td></td></tr>
    </table>
    """

    result = parse_manager_compensation_distribution_html(
        html, {"stock_id": "2395", "kind": "all", "year": 113}
    )

    assert result.iloc[0]["stock_id"] == "2395"
    assert result.iloc[0]["compensation_year"] == 112
    assert result.iloc[0]["distribution_year"] == 113
    assert result.iloc[0]["cash_compensation_amount"] == 6919611
    assert result.iloc[0]["profit_ratio"] == 0.064


def test_shareholding_distribution_form_data_uses_single_company_params() -> None:
    form_data = shareholding_distribution_form_data(
        {"stock_id": "2395", "kind": "all", "year": 113}
    )

    assert form_data["TYPEK"] == "all"
    assert form_data["co_id"] == "2395"
    assert form_data["year"] == 113
    assert form_data["isnew"] == "true"


def test_parse_shareholding_distribution_html_flattens_sections() -> None:
    html = """
    <table><tr><td>本資料由　(上市公司) 研華　公司提供</td></tr></table>
    <table>
      <tr><td>資料日期:114/03/31</td><td>資料日期:114/03/31</td><td>資料日期:114/03/31</td><td>資料日期:114/03/31</td><td>資料日期:114/03/31</td></tr>
      <tr><td>序</td><td>持股分級</td><td>人數</td><td>股數</td><td>持股比例(%)</td></tr>
      <tr><td>1</td><td>1-999</td><td>11,383</td><td>1,745,056</td><td>0.2019</td></tr>
      <tr><td>16</td><td>合 計</td><td>18,033</td><td>864,167,125</td><td>100</td></tr>
      <tr><td>18</td><td>股東結構類別</td><td>人數</td><td>股數</td><td>持股比例(%)</td></tr>
      <tr><td>19</td><td>政府(公營)機構投資</td><td>1</td><td>8</td><td>0.0000</td></tr>
    </table>
    """

    result = parse_shareholding_distribution_html(
        html, {"stock_id": "2395", "kind": "all", "year": 113}
    )

    assert result.iloc[0]["stock_name"] == "研華"
    assert result.iloc[0]["data_date"] == "114/03/31"
    assert result.iloc[0]["section"] == "holding_distribution"
    assert result.iloc[0]["holders"] == 11383
    assert result.iloc[1]["bucket_or_category"] == "合計"
    assert result.iloc[2]["section"] == "shareholder_structure"
    assert result.iloc[2]["shares"] == 8


def test_electronic_book_form_data_uses_single_company_params() -> None:
    form_data = electronic_book_form_data(
        {"stock_id": "2395", "kind": "all", "year": 113},
        "t57sb01_q5",
    )

    assert form_data["TYPEK"] == "all"
    assert form_data["co_id"] == "2395"
    assert form_data["year"] == 113
    assert form_data["queryName"] == "co_id"


def test_related_company_reports_form_data_uses_ifrs_flags() -> None:
    form_data = related_company_reports_form_data(
        {"stock_id": "2395", "kind": "all", "year": 113},
        "t57sb01_q10",
    )

    assert form_data["TYPEK"] == "all"
    assert form_data["co_id"] == "2395"
    assert form_data["year"] == 113
    assert form_data["t05st29_c_ifrs"] == "N"
    assert form_data["t05st30_c_ifrs"] == "N"
    assert form_data["isnew"] == "true"


def test_parse_electronic_book_html_returns_download_metadata() -> None:
    html = """
    <table>
      <tr>
        <th>證券代號</th><th>資料年度</th><th>資料類型</th><th>結案類型</th>
        <th>股東會性質</th><th>資料細節說明</th><th>備註</th>
        <th>電子檔案</th><th>檔案大小</th><th>上傳日期</th>
        <th>永續專章更(補)正</th>
      </tr>
      <tr>
        <td>2395</td><td>113</td><td>股東會年報</td><td>結案</td>
        <td>常會</td><td>股東會年報</td><td></td>
        <td>2024_2395_20240530F04.pdf</td><td>1,024</td>
        <td>113/05/30 18:00</td><td></td>
      </tr>
    </table>
    """

    result = parse_electronic_book_html(html, "annual_shareholder_meeting")

    assert result.iloc[0]["stock_id"] == "2395"
    assert result.iloc[0]["document_year"] == 113
    assert result.iloc[0]["filename"] == "2024_2395_20240530F04.pdf"
    assert result.iloc[0]["file_size"] == 1024
    assert "filename=2024_2395_20240530F04.pdf" in result.iloc[0]["download_request_url"]


def test_major_shareholder_relationship_form_data_supports_company_filter() -> None:
    form_data = major_shareholder_relationship_form_data(
        {"stock_id": "2395", "kind": "sii", "year": 113}
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["year"] == 113
    assert form_data["co_id1"] == "2395"
    assert form_data["co_id2"] == "2395"


def test_parse_major_shareholder_relationship_html_adds_pdf_request_url() -> None:
    html = """
    <table>
      <tr><th>公司代號</th><th>公司名稱</th><th>召開股東會日期</th><th>年報前十大股東相互間關係</th></tr>
      <tr><td>2395</td><td>研華</td><td>113/05/30</td><td><a href='javascript:getFile("2024_2395_20240530F17.pdf");'>詳細資料</a></td></tr>
    </table>
    """

    result = parse_major_shareholder_relationship_html(
        html, {"kind": "sii", "year": 113}
    )

    assert result.iloc[0]["stock_id"] == "2395"
    assert result.iloc[0]["detail_available"]
    assert result.iloc[0]["filename"] == "2024_2395_20240530F17.pdf"
    assert "filename=2024_2395_20240530F17.pdf" in result.iloc[0]["download_request_url"]


def test_employee_salary_form_data_supports_industry_filter() -> None:
    form_data = employee_salary_form_data(
        {"kind": "sii", "year": 113, "industry_code": "24"}
    )

    assert form_data == {
        "step": "1",
        "firstin": "1",
        "TYPEK": "sii",
        "RYEAR": 113,
        "code": "24",
    }


def test_normalize_employee_table_handles_shifted_first_source_row() -> None:
    row = [None] * 27
    row[8:11] = ["水泥工業", "1101", "台泥"]
    row[15:27] = [
        "一般公司",
        "10,000",
        "8,000",
        "100",
        "100",
        "80",
        "75",
        "6.67",
        "1.45",
        "90",
        "70",
        "1.30",
    ]
    table = pd.DataFrame([row])

    result = normalize_employee_table(table, {"kind": "sii", "year": 113})

    assert result.iloc[0]["stock_id"] == "1101"
    assert result.iloc[0]["employee_benefit_expense_thousand"] == 10000
    assert result.iloc[0]["avg_employee_salary_expense_thousand"] == 80
    assert result.iloc[0]["industry_avg_eps"] == 1.3


def test_full_time_employee_salary_form_data_supports_industry_filter() -> None:
    form_data = full_time_employee_salary_form_data(
        {"kind": "sii", "year": 113, "industry_code": "24"}
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["RYEAR"] == 113
    assert form_data["code"] == "24"


def test_parse_full_time_employee_salary_html_normalizes_rows() -> None:
    headers = "".join(f"<th>h{i}</th>" for i in range(19))
    data = "".join(
        f"<td>{value}</td>"
        for value in [
            "電腦及週邊設備業",
            "2395",
            "研華",
            "1,000",
            "10",
            "100",
            "90",
            "11.11",
            "95",
            "85",
            "11.76",
            "17.84",
            "80",
            "10.0",
            "否",
            "否",
            "否",
            "合理",
            "無",
        ]
    )
    html = f"""
    <table>
      <tr>{headers}</tr>
      <tr>{headers}</tr>
      <tr>{headers}</tr>
      <tr>{data}</tr>
    </table>
    """

    result = parse_full_time_employee_salary_html(
        html, {"kind": "sii", "year": 113}
    )

    assert result.iloc[0]["stock_id"] == "2395"
    assert result.iloc[0]["salary_avg_thousand"] == 100
    assert result.iloc[0]["salary_median_change_ratio"] == 11.76
    assert result.iloc[0]["performance_compensation_reasonableness"] == "合理"


def test_independent_director_profile_form_data_uses_market() -> None:
    form_data = independent_director_profile_form_data({"kind": "sii"})

    assert form_data == {
        "step": "1",
        "firstin": "ture",
        "off": "1",
        "TYPEK": "sii",
    }


def test_parse_independent_director_profile_html_normalizes_rows() -> None:
    html = """
    <table>
      <tr><th>序號</th><th>公司代號</th><th>公司名稱</th><th>職稱</th><th>姓名</th><th>就任日期</th><th>主要現職</th><th>主要經歷</th><th>公司名稱</th><th>職稱</th><th>備註</th></tr>
      <tr><td>1</td><td>2395</td><td>研華</td><td>獨立董事</td><td>王大明</td><td>113/05/30</td><td>教授</td><td>總經理</td><td>A公司</td><td>董事</td><td></td></tr>
    </table>
    """

    result = parse_independent_director_profile_html(html, {"kind": "sii"})

    assert result.iloc[0]["market"] == "sii"
    assert result.iloc[0]["sequence_no"] == 1
    assert result.iloc[0]["stock_id"] == "2395"
    assert result.iloc[0]["person_name"] == "王大明"


def test_board_attendance_training_form_data_uses_company_detail_step() -> None:
    form_data = board_attendance_training_form_data(
        {"stock_id": "2395", "kind": "sii"}
    )

    assert form_data == {
        "step": "2",
        "firstin": "ture",
        "TYPEK": "sii",
        "co_id": "2395",
    }


def test_parse_board_attendance_training_html_splits_sections() -> None:
    html = """
    <table><tr><td>公司代號：2395 公司名稱：研華</td></tr></table>
    <table>
      <tr><th>職稱</th><th>姓名(或代表人姓名)</th><th>所代表法人姓名</th><th>實際出(列)席次數(B)</th><th>委託出席次數</th><th>應出(列)席次數(A)</th><th>實際出(列)席%(B/A)</th><th>備註</th></tr>
      <tr><td>董事長</td><td>劉克振</td><td></td><td>5</td><td>0</td><td>5</td><td>100</td><td></td></tr>
    </table>
    <table>
      <tr><th>職稱</th><th>姓名</th><th>就任日期</th><th>初任日期</th><th>進修日期_起</th><th>進修日期_迄</th><th>主辦單位</th><th>課程名稱</th><th>進修時數</th><th>當年度進修總時數</th><th>備註</th></tr>
      <tr><td>獨立董事</td><td>王大明</td><td>113/05/30</td><td>110/07/20</td><td>113/08/01</td><td>113/08/01</td><td>證基會</td><td>公司治理</td><td>3</td><td>6</td><td></td></tr>
    </table>
    """

    result = parse_board_attendance_training_html(
        html, {"stock_id": "2395", "kind": "sii"}
    )

    assert set(result["section"]) == {"board_attendance", "director_training"}
    assert result.iloc[0]["stock_name"] == "研華"
    assert result.iloc[0]["attendance_ratio"] == 100
    assert result.iloc[1]["course_name"] == "公司治理"
    assert result.iloc[1]["training_hours"] == 3


def test_functional_committee_form_data_defaults_to_remuneration_committee() -> None:
    form_data = functional_committee_form_data({"kind": "sii"})

    assert form_data == {
        "firstin": "true",
        "step": "0",
        "TYPEK": "sii",
        "mod_no": "4",
    }


def test_parse_functional_committee_html_normalizes_rows() -> None:
    html = """
    <table>
      <tr><th>公司代號</th><th>公司名稱</th><th>成立日期</th><th>召集人</th><th>委員</th><th>具財務、法務或公司業務所需專長</th><th>運作情形資訊</th></tr>
      <tr><td>2395</td><td>研華</td><td>100/12/20</td><td>王大明</td><td>李小華</td><td>王大明</td><td>每季開會</td></tr>
    </table>
    """

    result = parse_functional_committee_html(html, {"kind": "sii", "committee": "4"})

    assert result.iloc[0]["committee_name"] == "薪資報酬委員會"
    assert result.iloc[0]["stock_id"] == "2395"
    assert result.iloc[0]["convener"] == "王大明"
    assert result.iloc[0]["operation_info"] == "每季開會"


def test_company_governance_structure_form_data_supports_company_filter() -> None:
    form_data = company_governance_structure_form_data(
        {"stock_id": "2395", "kind": "sii"}
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["co_id_1"] == "2395"
    assert form_data["co_id_2"] == "2395"
    assert form_data["inpuType"] == "co_id"


def test_parse_company_governance_structure_html_normalizes_rows() -> None:
    html = """
    <table>
      <tr>
        <th rowspan='2'>公司代號</th><th rowspan='2'>公司名稱</th>
        <th colspan='3'>公司章程</th>
        <th rowspan='2'>董事任期<br>(起)</th><th rowspan='2'>董事任期<br>(迄)</th>
        <th colspan='3'>董監事缺額(解任)情形</th>
        <th rowspan='2'>全體董事席次</th><th rowspan='2'>董事中獨立董事席次</th>
        <th colspan='3'>於中華民國設有戶籍之董事</th>
        <th rowspan='2'>審計委員會設置情形</th>
        <th rowspan='2'>薪資報酬委員會設置情形</th>
        <th rowspan='2'>法律顧問</th>
        <th rowspan='2'>公司專責處理股東建議或糾紛</th>
        <th rowspan='2'>備註</th>
      </tr>
      <tr>
        <th>董事席次</th><th>獨立董事席次</th><th>監察人席次</th>
        <th>董事缺額人數</th><th>獨立董事缺額人數</th><th>監察人缺額人數</th>
        <th>應占全體董事席次比率</th><th>實際選任席次</th><th>占全體董事會席次比率</th>
      </tr>
      <tr>
        <td>2395</td><td>研華</td><td>7~9</td><td>3</td><td>0</td>
        <td>112/05/25</td><td>115/05/24</td><td>0</td><td>0</td><td>0</td>
        <td>9</td><td>3</td><td>-</td><td>-</td><td>-</td>
        <td>有</td><td>有</td><td>宏鑑法律事務所</td><td>股務代理機構</td><td>無</td>
      </tr>
    </table>
    """

    result = parse_company_governance_structure_html(html, {"kind": "sii"})

    assert result.iloc[0]["market"] == "sii"
    assert result.iloc[0]["stock_id"] == "2395"
    assert result.iloc[0]["articles_board_seats"] == "7~9"
    assert result.iloc[0]["articles_independent_director_seats"] == 3
    assert result.iloc[0]["board_seats"] == 9
    assert result.iloc[0]["audit_committee_status"] == "有"
    assert result.iloc[0]["resident_director_required_ratio"] != result.iloc[0]["resident_director_required_ratio"]


def test_sustainability_report_payload_uses_ad_year_and_market_type() -> None:
    payload = sustainability_report_payload(
        {"stock_id": "2395", "kind": "sii", "year": 113}
    )

    assert to_ad_year(113) == 2024
    assert payload == {
        "year": 2024,
        "marketType": 0,
        "industryNameList": [],
        "companyCodeList": ["2395"],
    }


def test_sustainability_report_form_data_uses_mops_redirect_params() -> None:
    form_data = sustainability_report_form_data(
        {"stock_id": "2395", "kind": "sii", "year": 2024}
    )

    assert form_data["TYPEK"] == "sii"
    assert form_data["co_id"] == "2395"
    assert form_data["year"] == 113


def test_normalize_sustainability_report_rows_adds_download_urls() -> None:
    rows = [
        {
            "code": "2395",
            "name": "研華股份有限公司",
            "shortName": "研華",
            "enName": "ADVANTECH Co., Ltd.",
            "enShortName": "Advantech",
            "sector": "電腦及週邊設備業",
            "reason": "屬自願確信/保證者",
            "reportingInterval": "2024/01/01~2024/12/31",
            "complianceNotes": "GRI準則",
            "valiProvider": "台灣檢驗科技股份有限公司",
            "thirdStd": "AA1000",
            "partnerOrganization": "資誠聯合會計師事務所",
            "stdCompliance": "確信準則3000號",
            "accOptionType": "有限確信",
            "twDocLink": "https://example.com/2024ESG.pdf",
            "twFirstReportDownloadId": "0614c31e-29b7-4d43-bdde-b49fc99dc4ba",
            "twCommencementDate": "2025/08/28",
            "twEditReportDownloadId": "00000000-0000-0000-0000-000000000000",
            "enFirstReportDownloadId": "216de564-f484-44dd-bfdb-78436fc01222",
        }
    ]

    result = normalize_sustainability_report_rows(
        rows,
        {"stock_id": "2395", "kind": "sii", "year": 2024},
        source="new",
    )

    assert result.iloc[0]["stock_id"] == "2395"
    assert result.iloc[0]["report_year"] == 2024
    assert result.iloc[0]["tw_report_download_url"] == file_stream_url(
        "0614c31e-29b7-4d43-bdde-b49fc99dc4ba"
    )
    assert pd.isna(result.iloc[0]["tw_revised_report_download_url"])


def test_mops_no_data_markers_match_source_error_pages() -> None:
    assert has_no_data("查無所需資料")
    assert has_no_data("資料庫中查無需求資料")
    assert not has_no_data("<table><tr><td>2330</td></tr></table>")


def test_treasury_stock_buyback_query_form_data_uses_company_id() -> None:
    assert treasury_stock_buyback_query_form_data(
        {"stock_id": "1101", "kind": "sii"}
    )["co_id"] == "1101"


def test_parse_treasury_stock_buyback_list_html_extracts_detail_keys() -> None:
    html = """
    <table class='noBorder'><tr><td class='compName'><b>本資料由　(上市公司)台泥　公司提供</b></td></tr></table>
    <table class='hasBorder'>
      <tr><th>第N次</th><th>董事會決議日期</th><th>&nbsp;</th></tr>
      <tr>
        <td>6</td><td>114/06/30</td>
        <td><form><input name='step' value='11'><input name='TYPEK' value='sii'><input name='buyno' value='6'><input name='co_id' value='1101'></form></td>
      </tr>
    </table>
    """

    result = parse_treasury_stock_buyback_list_html(
        html,
        {"stock_id": "1101", "kind": "sii"},
    )

    assert result.iloc[0]["stock_id"] == "1101"
    assert result.iloc[0]["stock_name"] == "台泥"
    assert result.iloc[0]["buyback_no"] == 6
    assert bool(result.iloc[0]["detail_available"]) is True


def test_parse_treasury_stock_buyback_detail_html_extracts_core_fields() -> None:
    html = """
    <table><tr><td>第6次申請買回</td></tr><tr><td>申報日期：114/06/30</td></tr></table>
    <table>
      <tr><td>1</td><td>公司代號</td><td>1101</td></tr>
      <tr><td>2</td><td>公司名稱</td><td>台泥</td></tr>
      <tr><td>4</td><td>買回股份目的</td><td>轉讓股份予員工</td></tr>
      <tr><td>5</td><td>董事會決議日期</td><td>114/06/30</td></tr>
      <tr><td>12</td><td>買回股份種類</td><td>普通股</td></tr>
      <tr><td>14</td><td>預定買回之期間</td><td>開始日期：114/07/01 結束日期：114/08/01</td></tr>
      <tr><td>15</td><td>預定買回之數量(股)</td><td>10,000,000</td></tr>
      <tr><td>16</td><td>買回區間價格(元)</td><td>最低：17.85 最高：41.50</td></tr>
      <tr><td>17</td><td>買回方式</td><td>自集中交易市場買回</td></tr>
    </table>
    """

    result = parse_treasury_stock_buyback_detail_html(
        html,
        {"stock_id": "1101", "stock_name": "台泥"},
    )

    assert result["report_date"] == "114/06/30"
    assert result["planned_buyback_shares"] == 10000000
    assert result["planned_start_date"] == "114/07/01"
    assert result["price_ceiling"] == 41.5


def test_private_placement_form_data_allows_optional_company_filter() -> None:
    form_data = private_placement_form_data({"kind": "sii", "stock_id": "1316"})

    assert form_data["TYPEK"] == "sii"
    assert form_data["co_id"] == "1316"


def test_parse_private_placement_html_extracts_report_availability() -> None:
    html = """
    <table class='hasBorder'>
      <tr><th>公司代號</th><th>公司名稱</th><th>證券種類</th><th>董事會決議日起兩日內應申報相關資訊</th><th>年度/期別</th><th>實際定價日起二日內應申報相關資訊</th><th>股款或價款繳納完成日起十五日內應申報相關資訊</th><th>私募有價證券資金運用情形季報表(申報年季)</th></tr>
      <tr>
        <td>1316</td><td>上曜</td><td>普通股</td>
        <td><input onclick="document.t116sb01_fm.report_type.value='1_1';document.t116sb01_fm.co_id.value='1316';document.t116sb01_fm.decide_date.value='1140304';document.t116sb01_fm.stock_kind.value='1';" /></td>
        <td>114/1</td>
        <td><input onclick="document.t116sb01_fm.report_type.value='3_1';document.t116sb01_fm.year.value='114';document.t116sb01_fm.seq_no.value='1';" /></td>
        <td></td>
        <td><button onclick="document.t116sb01_fm.ys.value='11401';">11401</button></td>
      </tr>
    </table>
    """

    result = parse_private_placement_html(html, {"kind": "sii"})

    row = result.iloc[0]
    assert row["decision_date"] == "114/03/04"
    assert bool(row["decision_detail_available"]) is True
    assert bool(row["pricing_detail_available"]) is True
    assert row["fund_utilization_periods"] == "11401"


def test_asset_acquisition_disposal_query_form_data_uses_report_month() -> None:
    form_data = asset_acquisition_disposal_query_form_data(
        {"stock_id": "8011", "kind": "sii", "year": 113, "month": 9}
    )

    assert form_data["co_id"] == "8011"
    assert form_data["month"] == "09"


def test_parse_asset_acquisition_disposal_html_returns_company_list() -> None:
    html = """
    <table class='hasBorder'>
      <tr><th>公司代號</th><th>公司名稱</th><th>詳細資料</th></tr>
      <tr><td>8011</td><td>台通</td><td><input type='button' onclick="document.f1.co_id2.value='8011';" /></td></tr>
    </table>
    """

    result = parse_asset_acquisition_disposal_html(
        html,
        {"stock_id": "8011", "kind": "sii", "year": 113, "month": 9},
    )

    assert result.iloc[0]["stock_id"] == "8011"
    assert bool(result.iloc[0]["detail_available"]) is True


def test_asset_acquisition_disposal_financial_form_data_uses_report_month() -> None:
    form_data = asset_acquisition_disposal_financial_query_form_data(
        {"stock_id": "8011", "kind": "sii", "year": 113, "month": 9}
    )

    assert form_data["co_id"] == "8011"
    assert form_data["month"] == "09"


def test_parse_asset_acquisition_disposal_financial_detail_html_normalizes_values() -> None:
    html = """
    <table><tr><td>本資料由　(上市公司) 台通　公司提供</td></tr></table>
    <table>
      <tr><td>截至9月止，公司自行結算「流動與非流動之金融資產」合計金額(Y)(仟元)</td><td>71,407</td></tr>
      <tr><td>Y占最近期財務報告總資產比率(%)</td><td>0.98</td></tr>
      <tr><td>Y占最近期財務報告歸屬於母公司業主之權益比率(%)</td><td>2.39</td></tr>
      <tr><td>最近期財務報告營運資金數額(仟元)</td><td>928,938</td></tr>
      <tr><td>截至9月止，公司以有價證券辦理質權設定之市值(仟元)</td><td>0</td></tr>
    </table>
    """

    result = parse_asset_acquisition_disposal_financial_detail_html(
        html,
        {"stock_id": "8011", "kind": "sii", "year": 113, "month": 9},
    )

    assert result["financial_assets_total"] == 71407.0
    assert result["stock_name"] == "台通"
    assert result["working_capital"] == 928938.0


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
    headers = market_download_headers(
        "https://www.taifex.com.tw/cht/3/futDailyMarketReport"
    )

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
