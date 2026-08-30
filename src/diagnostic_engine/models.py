from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class VarianceInput:
    """Core data contract representing a single financial variance input observation."""

    period_start: date
    period_end: date
    metric_name: str
    actual_value: float
    budget_value: float
    currency: str = "USD"

    @property
    def variance(self) -> float:
        """Calculates the absolute variance (Actual - Budget)."""
        return self.actual_value - self.budget_value

    @property
    def variance_percentage(self) -> float:
        """Calculates the relative variance percentage.

        Returns 0.0 if the budget value is zero to avoid division by zero.
        """
        if self.budget_value == 0.0:
            return 0.0
        return (self.actual_value - self.budget_value) / abs(self.budget_value)