from app.services.metrics import build_chart_definitions, extract_metric_series


def _series_map(series):
    return {item.key: item for item in series}


def test_extract_metric_series_prefers_primary_concepts(load_fixture):
    companyfacts = load_fixture("companyfacts_aapl.json")
    series = _series_map(extract_metric_series(companyfacts))

    assert series["revenue"].latest_value == 391000000000
    assert series["revenue"].points[-1].source_concept == "RevenueFromContractWithCustomerExcludingAssessedTax"
    assert series["operating_income"].latest_value == 123000000000
    assert series["total_debt"].latest_value == 104000000000
    assert series["shares_outstanding"].points[-1].value == 15100000000


def test_extract_metric_series_derives_debt_proxy(load_fixture):
    companyfacts = load_fixture("companyfacts_cost.json")
    series = _series_map(extract_metric_series(companyfacts))

    assert series["revenue"].points[-1].source_concept == "SalesRevenueNet"
    assert series["total_debt"].latest_value == 7700000000
    assert series["shares_outstanding"].latest_value is None


def test_chart_builder_suppresses_missing_series(load_fixture):
    companyfacts = load_fixture("companyfacts_dal.json")
    metrics = extract_metric_series(companyfacts)
    charts, warnings = build_chart_definitions(metrics)

    chart_keys = {chart.key for chart in charts}
    assert "revenue_trend" in chart_keys
    assert "cash_vs_debt" in chart_keys
    assert "operating_income_trend" not in chart_keys
    assert warnings == []

