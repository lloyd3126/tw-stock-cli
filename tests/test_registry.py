from __future__ import annotations

from importlib import import_module

import pytest

from tw_stock_cli.registry import DATASETS
from tw_stock_cli.registry import get_dataset
from tw_stock_cli.registry import list_datasets
from tw_stock_cli.registry import normalize_roc_year
from tw_stock_cli.registry import require


def test_dataset_catalog_contains_expected_public_datasets() -> None:
    assert len(DATASETS) == 72
    assert set(DATASETS) >= {
        "twse.stock-price",
        "tpex.stock-price",
        "taifex.futures-daily",
        "taifex.fcm-futures-volume-day",
        "mops.month-revenue",
        "mops.income-statement",
        "mops.company-cash-flow",
        "mops.company-equity-changes",
        "mops.company-basic-info",
        "mops.company-governance-structure",
        "mops.asset-acquisition-disposal",
        "mops.asset-acquisition-disposal-financial",
        "mops.annual-report-electronic-book",
        "mops.board-attendance-training",
        "mops.director-supervisor-remuneration",
        "mops.dividend-distribution",
        "mops.employee-benefit-expense",
        "mops.employee-welfare-policy",
        "mops.esg-company-disclosure",
        "mops.ex-dividend-announcement",
        "mops.financial-report-electronic-book",
        "mops.endorsement-guarantee",
        "mops.fund-lending",
        "mops.full-time-employee-salary",
        "mops.functional-committee",
        "mops.independent-director-profile",
        "mops.insider-holding-company-list",
        "mops.insider-holding-detail",
        "mops.insider-pledge-ratio-summary",
        "mops.insider-pledge-summary",
        "mops.insider-shareholding-change",
        "mops.insider-shareholding-detail",
        "mops.insider-transfer-declaration-detail",
        "mops.insider-transfer-declaration-summary",
        "mops.insider-transfer-untransferred-detail",
        "mops.insider-transfer-untransferred-summary",
        "mops.investor-conference",
        "mops.material-info",
        "mops.material-info-detail",
        "mops.major-shareholder-relationship",
        "mops.manager-compensation-distribution",
        "mops.private-placement",
        "mops.related-company-reports",
        "mops.related-party-transaction",
        "mops.related-party-transaction-difference",
        "mops.shareholding-distribution",
        "mops.shareholder-meeting",
        "mops.sustainability-report",
        "mops.treasury-stock-buyback",
    }


def test_dataset_ids_match_dataclass_ids() -> None:
    for dataset_id, dataset in DATASETS.items():
        assert dataset.id == dataset_id


def test_dataset_modules_are_importable_and_expose_crawler() -> None:
    for dataset in DATASETS.values():
        module = import_module(dataset.module)
        assert hasattr(module, "crawler"), dataset.module


def test_column_contract_constants_are_consistent() -> None:
    for dataset in DATASETS.values():
        module = import_module(dataset.module)
        source_columns = getattr(module, "SOURCE_COLUMNS", None)
        output_columns = getattr(module, "OUTPUT_COLUMNS", None)

        if source_columns is not None:
            assert output_columns is not None, dataset.module
            assert len(source_columns) == len(output_columns), dataset.module

        if output_columns is not None:
            assert len(output_columns) == len(set(output_columns)), dataset.module
            assert all("劵" not in column for column in output_columns), dataset.module


def test_dataset_returns_are_consistent_with_column_contracts() -> None:
    for dataset in DATASETS.values():
        module = import_module(dataset.module)
        output_columns = getattr(module, "OUTPUT_COLUMNS", None)
        extra_columns = getattr(module, "EXTRA_COLUMNS", [])
        if output_columns is None:
            continue

        available_columns = {*output_columns, *extra_columns, "date"}
        assert set(dataset.returns) <= available_columns, dataset.id
        assert all("劵" not in column for column in dataset.returns), dataset.id


def test_list_datasets_is_sorted_and_filterable_by_group() -> None:
    datasets = list_datasets()
    twse_datasets = list_datasets("twse")

    assert [dataset.id for dataset in datasets] == sorted(DATASETS)
    assert twse_datasets
    assert all(dataset.group == "twse" for dataset in twse_datasets)


def test_get_dataset_reports_unknown_dataset() -> None:
    with pytest.raises(KeyError, match="Unknown dataset"):
        get_dataset("unknown.dataset")


def test_require_rejects_missing_values() -> None:
    with pytest.raises(ValueError, match="Missing required parameter: date"):
        require({"date": ""}, "date")


def test_normalize_roc_year_accepts_roc_and_ad_years() -> None:
    assert normalize_roc_year(115) == 115
    assert normalize_roc_year(2026) == 115
