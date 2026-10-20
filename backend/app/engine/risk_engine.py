"""High-level risk engine orchestration."""

from app.config import get_settings
from app.engine.baseline import calculate_baseline_score, get_nutrient_target
from app.engine.interaction import calculate_interaction_score
from app.engine.ml_layer import logistic_regression_probability
from app.schemas import AnalyzeRequest, NutritionQuestionnaire


QUESTIONNAIRE_SOURCE_TARGETS = {
    "vegetables": ("vegetable_servings", 5.0),
    "fruit": ("fruit_servings", 2.0),
    "protein": ("protein_servings", 3.0),
    "dairy": ("dairy_servings", 2.0),
    "whole_grains": ("whole_grain_servings", 3.0),
    "seafood": ("seafood_servings_per_week", 2.0),
    "nuts_seeds": ("nuts_seeds_servings", 1.0),
    "legumes": ("legume_servings", 1.0),
    "fermented": ("fermented_food_servings", 1.0),
    "water": ("water_liters", 2.0),
    "sunlight": ("sunlight_minutes", 20.0),
    "sleep": ("sleep_hours", 7.5),
    "processed": ("ultra_processed_meals_per_week", 0.0),
    "spices": ("vegetable_servings", 5.0),
    "supplement": ("meals_per_day", 3.0),
}


def calculate_symptom_adjustment(nutrient: str, symptoms: list[str]) -> float:
    """Calculate symptom-based risk adjustment for one nutrient."""

    settings = get_settings()
    score = 0.0

    for symptom in symptoms:
        nutrient_weights = settings.symptom_nutrient_map.get(symptom, {})
        score += nutrient_weights.get(nutrient, 0.0)

    return round(min(score, settings.symptom_max_score), 4)


def calculate_goal_adjustment(nutrient: str, health_goals: list[str]) -> float:
    """Calculate recommendation adjustment from selected health goals."""

    settings = get_settings()
    score = 0.0

    for goal in health_goals:
        nutrient_weights = settings.goal_nutrient_map.get(goal, {})
        score += nutrient_weights.get(nutrient, 0.0)

    return round(min(score, settings.symptom_max_score), 4)


def estimate_intake_from_questionnaire(
    questionnaire: NutritionQuestionnaire,
    sex: str,
    weight_kg: float,
) -> dict[str, float]:
    """Estimate nutrient intake from simple questionnaire indicators."""

    settings = get_settings()
    answers = questionnaire.model_dump()
    estimated_intake: dict[str, float] = {}

    for nutrient, profile in settings.nutrient_profiles.items():
        source = str(profile["source"])
        target_min = get_nutrient_target(nutrient, sex, settings, weight_kg)["min"]
        answer_key, source_target = QUESTIONNAIRE_SOURCE_TARGETS[source]
        answer_value = float(answers[answer_key])

        if source == "processed":
            coverage = min(1.5, 0.7 + answer_value / 10)
        elif source == "supplement":
            coverage = 0.0
        else:
            coverage = min(1.2, answer_value / source_target)

        if nutrient == "protein":
            target_min = max(target_min, round(weight_kg * 0.8, 2))
        if nutrient == "water":
            target_min = max(target_min, round(weight_kg * 0.03, 2))
        if nutrient == "electrolytes":
            exercise_bonus = min(1.0, answers["exercise_days_per_week"] / 7)
            coverage = min(1.2, coverage + exercise_bonus * 0.25)

        estimated_intake[nutrient] = round(target_min * coverage, 4)

    return estimated_intake


def merge_food_and_supplement_intake(
    nutrient_values: dict[str, float],
    supplement_values: dict[str, float],
) -> dict[str, float]:
    """Combine food and supplement intake values by nutrient."""

    return {
        nutrient: round(intake + supplement_values.get(nutrient, 0.0), 4)
        for nutrient, intake in nutrient_values.items()
    }


def build_recommendation(
    nutrient: str,
    total_intake: float,
    sex: str,
    weight_kg: float,
    probability: float,
) -> dict[str, float | str]:
    """Build recommendation content from target gaps and probability."""

    settings = get_settings()
    target = get_nutrient_target(nutrient, sex, settings, weight_kg)

    if total_intake < target["min"]:
        status = "low"
        gap_to_target = round(target["min"] - total_intake, 4)
    elif total_intake > target["max"]:
        status = "high"
        gap_to_target = round(total_intake - target["max"], 4)
    else:
        status = "normal"
        gap_to_target = 0.0

    if probability >= settings.recommendation_high_risk_threshold:
        priority = "high"
    elif probability >= settings.recommendation_medium_risk_threshold:
        priority = "medium"
    else:
        priority = "low"

    return {
        "status": status,
        "priority": priority,
        "target_min": target["min"],
        "target_max": target["max"],
        "gap_to_target": gap_to_target,
        "message": build_recommendation_message(nutrient, status),
    }


def build_recommendation_message(nutrient: str, status: str) -> str:
    """Return human-readable recommendation text for a nutrient."""

    settings = get_settings()
    if nutrient in settings.nutrient_recommendation_copy:
        return settings.nutrient_recommendation_copy[nutrient][status]

    label = str(settings.nutrient_profiles[nutrient]["label"])
    if status == "low":
        return f"Prioritize food patterns or supplements that improve {label} coverage for your selected goals."
    if status == "high":
        return f"Review {label} sources and avoid stacking supplements above the configured target."
    return f"{label} appears adequate based on the questionnaire estimate."


def analyze_nutrition_risk(payload: AnalyzeRequest) -> dict[str, dict[str, object]]:
    """Run the full explainable nutrition risk pipeline."""

    settings = get_settings()
    nutrient_values = (
        payload.nutrients.model_dump()
        if payload.nutrients is not None
        else estimate_intake_from_questionnaire(
            payload.questionnaire,
            payload.sex,
            payload.weight_kg,
        )
    )
    supplement_values = payload.supplements
    total_values = merge_food_and_supplement_intake(nutrient_values, supplement_values)
    result: dict[str, dict[str, float]] = {}

    for nutrient, intake in total_values.items():
        baseline = calculate_baseline_score(
            nutrient,
            intake,
            payload.sex,
            settings,
            payload.weight_kg,
        )
        interaction = calculate_interaction_score(
            nutrient,
            total_values,
            payload.sex,
            settings,
        )
        symptom = calculate_symptom_adjustment(nutrient, payload.symptoms)
        goal = calculate_goal_adjustment(nutrient, payload.health_goals)
        probability = logistic_regression_probability(
            baseline,
            interaction,
            min(symptom + goal, settings.symptom_max_score),
            settings,
        )
        recommendation = build_recommendation(
            nutrient,
            intake,
            payload.sex,
            payload.weight_kg,
            probability,
        )

        result[nutrient] = {
            "food_intake": nutrient_values[nutrient],
            "supplement_intake": supplement_values.get(nutrient, 0.0),
            "total_intake": intake,
            "baseline": baseline,
            "interaction": interaction,
            "symptom": symptom,
            "goal": goal,
            "probability": probability,
            "recommendation": recommendation,
        }

    return result
