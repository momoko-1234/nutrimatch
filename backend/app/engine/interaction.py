"""Nutrient interaction scoring."""

from app.config import Settings
from app.engine.baseline import classify_intake_status


def calculate_interaction_score(
    nutrient: str,
    nutrient_values: dict[str, float],
    sex: str,
    settings: Settings,
) -> float:
    """Calculate interaction risk from configured nutrient relationship rules."""

    score = 0.0
    rules = settings.interaction_rules.get(nutrient, [])

    for rule in rules:
        related_nutrient = str(rule["with"])
        related_status = classify_intake_status(
            related_nutrient,
            nutrient_values[related_nutrient],
            sex,
            settings,
        )

        if related_status == "low":
            score += float(rule.get("when_other_low", 0.0))
        if related_status == "high":
            score += float(rule.get("when_other_high", 0.0))

    return round(min(score, settings.interaction_max_score), 4)
