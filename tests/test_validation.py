from datetime import date
import pytest

# Assuming your module is named input_validator.py
# Adjust import path as needed
from diagnostic-engine.validation import validate_and_coerce_input


@pytest.fixture
def valid_raw_data():
    return {
        "period_start": "2023-01-01",
        "period_end": "2023-01-31",
        "metric_name": "Revenue",
        "actual_value": 150000.50,
        "budget_value": "140000.00",
        "currency": "EUR",
    }


def test_validate_and_coerce_input_success_with_strings(valid_raw_data):
    result = validate_and_coerce_input(valid_raw_data)

    assert result.period_start == date(2023, 1, 1)
    assert result.period_end == date(2023, 1, 31)
    assert result.metric_name == "Revenue"
    assert result.actual_value == 150000.50
    assert result.budget_value == 140000.00
    assert result.currency == "EUR"


def test_validate_and_coerce_input_success_with_date_objects(valid_raw_data):
    valid_raw_data["period_start"] = date(2023, 1, 1)
    valid_raw_data["period_end"] = date(2023, 1, 31)

    result = validate_and_coerce_input(valid_raw_data)

    assert result.period_start == date(2023, 1, 1)
    assert result.period_end == date(2023, 1, 31)


def test_validate_and_coerce_input_default_currency(valid_raw_data):
    del valid_raw_data["currency"]
    result = validate_and_coerce_input(valid_raw_data)

    assert result.currency == "USD"


@pytest.mark.parametrize(
    "missing_field",
    ["period_start", "period_end", "metric_name", "actual_value", "budget_value"],
)
def test_missing_required_fields(valid_raw_data, missing_field):
    del valid_raw_data[missing_field]
    with pytest.raises(TypeError, match=f"Missing required field or null value: '{missing_field}'"):
        validate_and_coerce_input(valid_raw_data)


@pytest.mark.parametrize(
    "null_field",
    ["period_start", "period_end", "metric_name", "actual_value", "budget_value"],
)
def test_null_required_fields(valid_raw_data, null_field):
    valid_raw_data[null_field] = None
    with pytest.raises(TypeError, match=f"Missing required field or null value: '{null_field}'"):
        validate_and_coerce_input(valid_raw_data)


@pytest.mark.parametrize("invalid_date", ["01-01-2023", "2023/01/01", 12345, True, [2023, 1, 1]])
def test_invalid_date_format_or_type(valid_raw_data, invalid_date):
    valid_raw_data["period_start"] = invalid_date
    with pytest.raises(TypeError, match="Invalid format or type for date fields"):
        validate_and_coerce_input(valid_raw_data)


def test_period_start_after_period_end(valid_raw_data):
    valid_raw_data["period_start"] = "2023-02-01"
    valid_raw_data["period_end"] = "2023-01-01"
    with pytest.raises(ValueError, match="Period start date .* cannot be after period end date"):
        validate_and_coerce_input(valid_raw_data)


@pytest.mark.parametrize("invalid_metric", [123, "", "   ", False, []])
def test_invalid_metric_name(valid_raw_data, invalid_metric):
    valid_raw_data["metric_name"] = invalid_metric
    with pytest.raises(TypeError, match="Field 'metric_name' must be a non-empty string."):
        validate_and_coerce_input(valid_raw_data)


@pytest.mark.parametrize("invalid_number", ["invalid_float", [100], {"val": 10}])
def test_non_coercible_numeric_values(valid_raw_data, invalid_number):
    valid_raw_data["actual_value"] = invalid_number
    with pytest.raises(TypeError, match="must be float-coercible"):
        validate_and_coerce_input(valid_raw_data)


@pytest.mark.parametrize("non_finite_val", [float("inf"), float("-inf"), float("nan")])
def test_non_finite_numeric_values(valid_raw_data, non_finite_val):
    valid_raw_data["actual_value"] = non_finite_val
    with pytest.raises(ValueError, match="must be finite"):
        validate_and_coerce_input(valid_raw_data)


def test_invalid_currency_type(valid_raw_data):
    valid_raw_data["currency"] = 123
    with pytest.raises(TypeError, match="Field 'currency' must be a string."):
        validate_and_coerce_input(valid_raw_data)
