from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Iterable

from app.models import ChartDefinition, ChartSeriesPoint, MetricPoint, MetricSeries


FLOW_METRICS = {
    "revenue": {
        "label": "Revenue",
        "formatter": "currency",
        "concepts": [
            ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
            ("us-gaap", "SalesRevenueNet"),
            ("us-gaap", "Revenues"),
        ],
    },
    "gross_profit": {
        "label": "Gross Profit",
        "formatter": "currency",
        "concepts": [("us-gaap", "GrossProfit")],
    },
    "operating_income": {
        "label": "Operating Income",
        "formatter": "currency",
        "concepts": [("us-gaap", "OperatingIncomeLoss")],
    },
    "net_income": {
        "label": "Net Income",
        "formatter": "currency",
        "concepts": [("us-gaap", "NetIncomeLoss"), ("us-gaap", "ProfitLoss")],
    },
    "cash_from_operations": {
        "label": "Cash From Operations",
        "formatter": "currency",
        "concepts": [
            ("us-gaap", "NetCashProvidedByUsedInOperatingActivities"),
            ("us-gaap", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"),
        ],
    },
    "capex": {
        "label": "Capital Expenditures",
        "formatter": "currency",
        "concepts": [
            ("us-gaap", "PaymentsToAcquirePropertyPlantAndEquipment"),
            ("us-gaap", "CapitalExpendituresIncurredButNotYetPaid"),
            ("us-gaap", "PropertyPlantAndEquipmentAdditions"),
        ],
    },
}

INSTANT_METRICS = {
    "cash_and_equivalents": {
        "label": "Cash and Equivalents",
        "formatter": "currency",
        "concepts": [
            ("us-gaap", "CashAndCashEquivalentsAtCarryingValue"),
            (
                "us-gaap",
                "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
            ),
        ],
    },
    "shares_outstanding": {
        "label": "Shares Outstanding",
        "formatter": "number",
        "concepts": [
            ("dei", "EntityCommonStockSharesOutstanding"),
            ("us-gaap", "CommonStockSharesOutstanding"),
        ],
    },
}

DIRECT_DEBT_CONCEPTS = [
    ("us-gaap", "LongTermDebtAndCapitalLeaseObligations"),
    ("us-gaap", "LongTermDebtAndFinanceLeaseObligations"),
    ("us-gaap", "LongTermDebtAndCapitalLeaseObligationsCurrentAndNoncurrent"),
    ("us-gaap", "DebtAndCapitalLeaseObligations"),
]

DEBT_COMPONENTS = {
    "noncurrent": [
        ("us-gaap", "LongTermDebtNoncurrent"),
        ("us-gaap", "LongTermDebt"),
    ],
    "current": [
        ("us-gaap", "LongTermDebtCurrent"),
        ("us-gaap", "CurrentPortionOfLongTermDebt"),
    ],
    "short_term": [
        ("us-gaap", "ShortTermBorrowings"),
        ("us-gaap", "CommercialPaper"),
        ("us-gaap", "LinesOfCreditCurrent"),
    ],
}


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _duration_days(entry: dict[str, Any]) -> int | None:
    start = _parse_date(entry.get("start"))
    end = _parse_date(entry.get("end"))
    if not start or not end:
        return None
    return (end - start).days


def _is_ten_k_form(value: str | None) -> bool:
    return bool(value) and value.upper().startswith("10-K")


def _pick_unit_entries(concept_data: dict[str, Any], expected_unit: str) -> list[dict[str, Any]]:
    units = concept_data.get("units", {})
    if expected_unit in units:
        return units[expected_unit]

    for unit_name, entries in units.items():
        if expected_unit == "shares" and "share" in unit_name.lower():
            return entries
    return []


def _select_flow_points(
    facts_root: dict[str, Any],
    concepts: Iterable[tuple[str, str]],
) -> dict[str, MetricPoint]:
    selected: dict[str, MetricPoint] = {}
    for namespace, concept in concepts:
        concept_data = facts_root.get(namespace, {}).get(concept)
        if not concept_data:
            continue

        entries = _pick_unit_entries(concept_data, "USD")
        by_year: dict[str, dict[str, Any]] = {}
        for entry in entries:
            if not _is_ten_k_form(entry.get("form")):
                continue
            if not isinstance(entry.get("val"), (int, float)):
                continue
            duration_days = _duration_days(entry)
            if duration_days is None or not 300 <= duration_days <= 380:
                continue
            fiscal_year = str(entry.get("fy") or _parse_date(entry.get("end")).year)
            existing = by_year.get(fiscal_year)
            if existing is None or entry.get("filed", "") > existing.get("filed", ""):
                by_year[fiscal_year] = entry

        for fiscal_year, entry in by_year.items():
            if fiscal_year in selected:
                continue
            selected[fiscal_year] = MetricPoint(
                fiscal_year=fiscal_year,
                value=float(entry["val"]),
                unit="USD",
                form=entry["form"],
                filed=entry.get("filed", ""),
                frame=entry.get("frame"),
                source_concept=concept,
            )

    return selected


def _select_instant_points(
    facts_root: dict[str, Any],
    concepts: Iterable[tuple[str, str]],
    unit: str,
) -> dict[str, MetricPoint]:
    selected: dict[str, MetricPoint] = {}
    for namespace, concept in concepts:
        concept_data = facts_root.get(namespace, {}).get(concept)
        if not concept_data:
            continue

        entries = _pick_unit_entries(concept_data, unit)
        by_year: dict[str, dict[str, Any]] = {}
        for entry in entries:
            if not _is_ten_k_form(entry.get("form")):
                continue
            if not isinstance(entry.get("val"), (int, float)):
                continue
            end = _parse_date(entry.get("end"))
            if not end:
                continue
            fiscal_year = str(entry.get("fy") or end.year)
            existing = by_year.get(fiscal_year)
            if existing is None or entry.get("filed", "") > existing.get("filed", ""):
                by_year[fiscal_year] = entry

        for fiscal_year, entry in by_year.items():
            if fiscal_year in selected:
                continue
            selected[fiscal_year] = MetricPoint(
                fiscal_year=fiscal_year,
                value=float(entry["val"]),
                unit=unit,
                form=entry["form"],
                filed=entry.get("filed", ""),
                frame=entry.get("frame"),
                source_concept=concept,
            )

    return selected


def _trim_points(points: dict[str, MetricPoint], max_years: int) -> list[MetricPoint]:
    ordered = [points[year] for year in sorted(points.keys())]
    return ordered[-max_years:]


def _build_series(
    key: str,
    label: str,
    formatter: str,
    points: list[MetricPoint],
) -> MetricSeries:
    latest = points[-1] if points else None
    return MetricSeries(
        key=key,
        label=label,
        formatter=formatter,  # type: ignore[arg-type]
        points=points,
        latest_value=latest.value if latest else None,
        latest_fiscal_year=latest.fiscal_year if latest else None,
    )


def _derive_total_debt_series(facts_root: dict[str, Any], max_years: int) -> MetricSeries:
    direct_points = _select_instant_points(facts_root, DIRECT_DEBT_CONCEPTS, "USD")
    if direct_points:
        return _build_series(
            "total_debt",
            "Total Debt",
            "currency",
            _trim_points(direct_points, max_years),
        )

    component_values: dict[str, dict[str, float]] = defaultdict(dict)
    for component_name, concepts in DEBT_COMPONENTS.items():
        points = _select_instant_points(facts_root, concepts, "USD")
        for fiscal_year, point in points.items():
            if point.value is not None:
                component_values[fiscal_year][component_name] = point.value

    combined: dict[str, MetricPoint] = {}
    for fiscal_year, values in component_values.items():
        if not values:
            continue
        if "noncurrent" not in values and "current" not in values and "short_term" not in values:
            continue
        total = sum(values.values())
        combined[fiscal_year] = MetricPoint(
            fiscal_year=fiscal_year,
            value=total,
            unit="USD",
            form="10-K",
            filed="",
            frame=None,
            source_concept="derived_total_debt",
        )

    return _build_series("total_debt", "Total Debt", "currency", _trim_points(combined, max_years))


def extract_metric_series(companyfacts: dict[str, Any], max_years: int = 5) -> list[MetricSeries]:
    facts_root = companyfacts.get("facts", {})
    series: list[MetricSeries] = []

    for key, config in FLOW_METRICS.items():
        points = _trim_points(_select_flow_points(facts_root, config["concepts"]), max_years)
        series.append(_build_series(key, config["label"], config["formatter"], points))

    for key, config in INSTANT_METRICS.items():
        unit = "shares" if key == "shares_outstanding" else "USD"
        points = _trim_points(
            _select_instant_points(facts_root, config["concepts"], unit),
            max_years,
        )
        series.append(_build_series(key, config["label"], config["formatter"], points))

    series.append(_derive_total_debt_series(facts_root, max_years))
    return series


def _series_map(metrics: list[MetricSeries]) -> dict[str, MetricSeries]:
    return {metric.key: metric for metric in metrics}


def _single_metric_chart(
    key: str,
    title: str,
    subtitle: str,
    series: MetricSeries | None,
    kind: str = "line",
) -> ChartDefinition | None:
    if not series or not any(point.value is not None for point in series.points):
        return None

    return ChartDefinition(
        key=key,
        title=title,
        subtitle=subtitle,
        kind=kind,  # type: ignore[arg-type]
        formatter=series.formatter,
        primary_label=series.label,
        series=[
            ChartSeriesPoint(fiscal_year=point.fiscal_year, primary=point.value)
            for point in series.points
        ],
    )


def build_chart_definitions(metrics: list[MetricSeries]) -> tuple[list[ChartDefinition], list[str]]:
    series_map = _series_map(metrics)
    charts: list[ChartDefinition] = []
    warnings: list[str] = []

    revenue_chart = _single_metric_chart(
        "revenue_trend",
        "Revenue Trend",
        "Annual revenue from SEC company facts.",
        series_map.get("revenue"),
    )
    if revenue_chart:
        charts.append(revenue_chart)
    else:
        warnings.append("Revenue could not be normalized from the latest 10-K facts.")

    operating_chart = _single_metric_chart(
        "operating_income_trend",
        "Operating Income Trend",
        "Operating profit by fiscal year when tagged in XBRL.",
        series_map.get("operating_income"),
        kind="bar",
    )
    if operating_chart:
        charts.append(operating_chart)

    net_income_chart = _single_metric_chart(
        "net_income_trend",
        "Net Income Trend",
        "Bottom-line earnings from annual 10-K facts.",
        series_map.get("net_income"),
        kind="bar",
    )
    if net_income_chart:
        charts.append(net_income_chart)

    cfo_chart = _single_metric_chart(
        "cash_from_operations_trend",
        "Cash From Operations Trend",
        "Annual operating cash generation.",
        series_map.get("cash_from_operations"),
    )
    if cfo_chart:
        charts.append(cfo_chart)

    cash_series = series_map.get("cash_and_equivalents")
    debt_series = series_map.get("total_debt")
    if cash_series and debt_series and (cash_series.points or debt_series.points):
        years = sorted(
            {
                point.fiscal_year
                for point in cash_series.points + debt_series.points
            }
        )
        cash_values = {point.fiscal_year: point.value for point in cash_series.points}
        debt_values = {point.fiscal_year: point.value for point in debt_series.points}
        charts.append(
            ChartDefinition(
                key="cash_vs_debt",
                title="Cash vs Debt",
                subtitle="Balance sheet liquidity versus debt proxy.",
                kind="paired_bar",
                formatter="currency",
                primary_label="Cash",
                secondary_label="Debt",
                series=[
                    ChartSeriesPoint(
                        fiscal_year=year,
                        primary=cash_values.get(year),
                        secondary=debt_values.get(year),
                    )
                    for year in years
                ],
            )
        )

    shares_chart = _single_metric_chart(
        "shares_outstanding_trend",
        "Share Count Trend",
        "Dilution or buyback signal when shares are consistently tagged.",
        series_map.get("shares_outstanding"),
    )
    if shares_chart and len(shares_chart.series) >= 2:
        charts.append(shares_chart)

    shares_series = series_map.get("shares_outstanding")
    if shares_series and shares_series.points and not shares_chart:
        warnings.append("Shares outstanding data was too incomplete to chart reliably.")

    return charts[:6], warnings


def summarize_metrics_for_prompt(metrics: list[MetricSeries]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for metric in metrics:
        summary[metric.key] = {
            "label": metric.label,
            "latest_value": metric.latest_value,
            "latest_fiscal_year": metric.latest_fiscal_year,
            "points": [
                {"fiscal_year": point.fiscal_year, "value": point.value}
                for point in metric.points
            ],
        }
    return summary
