"""Configurable logistic regression probability layer."""

from math import exp

from app.config import Settings


def logistic_regression_probability(
    baseline: float,
    interaction: float,
    symptom: float,
    settings: Settings,
) -> float:
    """Calculate risk probability using configurable logistic regression betas."""

    z_value = (
        settings.logistic_beta_0
        + settings.logistic_beta_baseline * baseline
        + settings.logistic_beta_interaction * interaction
        + settings.logistic_beta_symptom * symptom
    )
    probability = 1 / (1 + exp(-z_value))
    return round(probability, 4)
