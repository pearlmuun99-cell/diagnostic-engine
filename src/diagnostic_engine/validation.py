from datetime import date, datetime
from math import isfinite
from typing import Any, Dict

from diagnostic_engine.models import VarianceInput


def validate_and_coerce_input(raw_data: Dict[str, Any]) -> VarianceInput:
    """Validates structural fields, checks for nulls, and coerces types into a VarianceInput.

    Raises:
        TypeError: If a field is missing or cannot be coerced into its target type.
        ValueError: If dates are logically inverted or numeric values are non-finite.
    """
    required_fields = [
        "period_start",
        "period_end",
        "metric_name",
        "actual_value",
        "budget_value",
    ]

    for field in required_fields:
        if field not in raw_data or raw_data[field] is None:
            raise TypeError(f"Missing required field or null value: '{field}'")

    try:
        if isinstance(raw_data["period_start"], str):
            p_start = datetime.strptime(
                raw_data["period_start"],
                "%Y-%m-%d",
            ).date()
        elif isinstance(raw_data["period_start"], date):
            p_start = raw_data["period_start"]
        else:
            raise TypeError

        if isinstance(raw_data["period_end"], str):
            p_end = datetime.strptime(
                raw_data["period_end"],
                "%Y-%m-%d",
            ).date()
        elif isinstance(raw_data["period_end"], date):
            p_end = raw_data["period_end"]
        else:
            raise TypeError
    except (ValueError, TypeError):
        raise TypeError(
            "Invalid format or type for date fields. "
            "Expected YYYY-MM-DD string or date object."
        )

    if p_start > p_end:
        raise ValueError(
            f"Period start date ({p_start}) cannot be after period end date ({p_end})."
        )

    if (
        not isinstance(raw_data["metric_name"], str)
        or not raw_data["metric_name"].strip()
    ):
        raise TypeError("Field 'metric_name' must be a non-empty string.")

    try:
        actual = float(raw_data["actual_value"])
        budget = float(raw_data["budget_value"])
    except (ValueError, TypeError):
        raise TypeError(
            "Numerical values 'actual_value' and 'budget_value' "
            "must be float-coercible."
        )

    if not isfinite(actual) or not isfinite(budget):
        raise ValueError(
            "Numerical values 'actual_value' and 'budget_value' "
            "must be finite."
        )

    currency = raw_data.get("currency", "USD")

    if not isinstance(currency, str):
        raise TypeError("Field 'currency' must be a string.")

    return VarianceInput(
        period_start=p_start,
        period_end=p_end,
        metric_name=raw_data["metric_name"],
        actual_value=actual,
        budget_value=budget,
        currency=currency,
    )