"""Baseline nutrition risk scoring."""

from app.config import Settings


def calculate_baseline_score(
    nutrient: str,
    intake: float,
    sex: str,
    settings: Settings,
    weight_kg: float | None = None,
) -> float:
    """Calculate deficiency or excess risk against configured nutrient targets."""

    target = get_nutrient_target(nutrient, sex, settings, weight_kg)
    minimum = target["min"]
    maximum = target["max"]

    if intake < minimum:
        deficiency_gap = (minimum - intake) / minimum
        score = deficiency_gap * settings.baseline_deficiency_weight
    elif intake > maximum:
        excess_gap = (intake - maximum) / maximum
        score = excess_gap * settings.baseline_excess_weight
    else:
        score = 0.0

    return round(min(score, settings.baseline_max_score), 4)


def classify_intake_status(nutrient: str, intake: float, sex: str, settings: Settings) -> str:
    """Classify intake as low, normal, or high for interaction logic."""

    target = get_nutrient_target(nutrient, sex, settings)
    if intake < target["min"]:
        return "low"
    if intake > target["max"]:
        return "high"
    return "normal"


def get_nutrient_target(
    nutrient: str,
    sex: str,
    settings: Settings,
    weight_kg: float | None = None,
) -> dict[str, float]:
    """Return nutrient targets, applying weight-based rules when configured."""

    if nutrient in settings.nutrient_targets:
        target = dict(settings.nutrient_targets[nutrient][sex])
    else:
        profile = settings.nutrient_profiles[nutrient]
        target = {"min": float(profile["min"]), "max": float(profile["max"])}

    if nutrient == "omega_3" and weight_kg is not None:
        target["min"] = max(
            target["min"],
            round(weight_kg * settings.omega_3_weight_factor_g_per_kg, 2),
        )

    return target
