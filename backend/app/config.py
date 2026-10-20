"""Application configuration and model parameters."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


Sex = Literal["male", "female"]


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "NutriMatch API"
    app_env: str = "development"
    backend_cors_origins: str = "http://localhost:3000"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_timeout_seconds: float = Field(120, gt=0, le=600)

    logistic_beta_0: float = -1.2
    logistic_beta_baseline: float = 2.4
    logistic_beta_interaction: float = 1.1
    logistic_beta_symptom: float = 1.6

    baseline_deficiency_weight: float = 1.0
    baseline_excess_weight: float = 0.85
    baseline_max_score: float = 1.0
    interaction_max_score: float = 1.0
    symptom_max_score: float = 1.0

    symptom_default_weight: float = 0.08
    default_weight_kg: float = 60.0
    omega_3_weight_factor_g_per_kg: float = 0.02
    recommendation_high_risk_threshold: float = 0.5
    recommendation_medium_risk_threshold: float = 0.35

    nutrient_targets: dict[str, dict[str, dict[str, float]]] = Field(
        default_factory=lambda: {
            "vitamin_a": {
                "male": {"min": 900.0, "max": 3000.0},
                "female": {"min": 700.0, "max": 3000.0},
            },
            "zinc": {
                "male": {"min": 11.0, "max": 40.0},
                "female": {"min": 8.0, "max": 40.0},
            },
            "iron": {
                "male": {"min": 8.0, "max": 45.0},
                "female": {"min": 18.0, "max": 45.0},
            },
            "magnesium": {
                "male": {"min": 420.0, "max": 700.0},
                "female": {"min": 320.0, "max": 700.0},
            },
            "vitamin_b6": {
                "male": {"min": 1.3, "max": 100.0},
                "female": {"min": 1.3, "max": 100.0},
            },
            "omega_3": {
                "male": {"min": 1.6, "max": 5.0},
                "female": {"min": 1.1, "max": 5.0},
            },
            "vitamin_d": {
                "male": {"min": 15.0, "max": 100.0},
                "female": {"min": 15.0, "max": 100.0},
            },
        }
    )

    interaction_rules: dict[str, list[dict[str, float | str]]] = Field(
        default_factory=lambda: {
            "iron": [
                {"with": "zinc", "when_other_high": 0.03},
                {"with": "magnesium", "when_other_low": 0.04},
            ],
            "zinc": [
                {"with": "iron", "when_other_high": 0.03},
                {"with": "vitamin_a", "when_other_low": 0.05},
            ],
            "vitamin_a": [
                {"with": "zinc", "when_other_low": 0.05},
                {"with": "vitamin_d", "when_other_high": 0.02},
            ],
            "magnesium": [
                {"with": "vitamin_d", "when_other_low": 0.04},
                {"with": "vitamin_b6", "when_other_low": 0.03},
            ],
            "vitamin_b6": [
                {"with": "magnesium", "when_other_low": 0.03},
                {"with": "omega_3", "when_other_low": 0.03},
            ],
            "omega_3": [
                {"with": "vitamin_d", "when_other_low": 0.03},
                {"with": "vitamin_b6", "when_other_low": 0.03},
            ],
            "vitamin_d": [
                {"with": "magnesium", "when_other_low": 0.05},
                {"with": "vitamin_a", "when_other_high": 0.02},
            ],
        }
    )

    symptom_nutrient_map: dict[str, dict[str, float]] = Field(
        default_factory=lambda: {
            "fatigue": {"iron": 0.12, "vitamin_d": 0.1, "magnesium": 0.08},
            "hair_loss": {"zinc": 0.1, "iron": 0.08, "vitamin_d": 0.06},
            "low_immunity": {"zinc": 0.12, "vitamin_a": 0.08, "vitamin_d": 0.08},
            "muscle_cramps": {"magnesium": 0.14, "vitamin_d": 0.06},
            "dry_eyes": {"vitamin_a": 0.12, "omega_3": 0.08},
            "mood_changes": {"vitamin_b6": 0.1, "omega_3": 0.08, "vitamin_d": 0.06},
            "joint_discomfort": {"omega_3": 0.1, "vitamin_d": 0.08},
        }
    )

    goal_nutrient_map: dict[str, dict[str, float]] = Field(
        default_factory=lambda: {
            "energy": {
                "iron": 0.1,
                "vitamin_b12": 0.08,
                "vitamin_b6": 0.06,
                "magnesium": 0.06,
                "coq10": 0.05,
            },
            "immunity": {
                "vitamin_c": 0.1,
                "zinc": 0.08,
                "vitamin_d": 0.08,
                "selenium": 0.06,
                "probiotics": 0.05,
            },
            "bone_health": {
                "calcium": 0.1,
                "vitamin_d": 0.1,
                "vitamin_k": 0.07,
                "magnesium": 0.06,
                "boron": 0.04,
            },
            "muscle_performance": {
                "protein": 0.1,
                "creatine": 0.08,
                "magnesium": 0.06,
                "potassium": 0.06,
                "electrolytes": 0.05,
            },
            "heart_health": {
                "omega_3": 0.1,
                "fiber": 0.08,
                "potassium": 0.06,
                "coq10": 0.05,
                "polyphenols": 0.05,
            },
            "gut_health": {
                "fiber": 0.1,
                "probiotics": 0.08,
                "prebiotics": 0.08,
                "glutamine": 0.05,
                "zinc": 0.04,
            },
            "skin_hair": {
                "collagen": 0.08,
                "vitamin_c": 0.08,
                "biotin": 0.07,
                "zinc": 0.06,
                "silicon": 0.04,
            },
            "mood_sleep": {
                "magnesium": 0.08,
                "omega_3": 0.06,
                "vitamin_b6": 0.06,
                "melatonin": 0.06,
                "taurine": 0.04,
            },
            "weight_management": {
                "protein": 0.08,
                "fiber": 0.08,
                "chromium": 0.05,
                "green_tea_extract": 0.04,
                "carnitine": 0.04,
            },
        }
    )

    nutrient_profiles: dict[str, dict[str, object]] = Field(
        default_factory=lambda: {
            "vitamin_a": {"label": "Vitamin A", "unit": "mcg RAE", "min": 700.0, "max": 3000.0, "source": "vegetables", "goals": ["immunity", "skin_hair"]},
            "vitamin_c": {"label": "Vitamin C", "unit": "mg", "min": 90.0, "max": 2000.0, "source": "fruit", "goals": ["immunity", "skin_hair"]},
            "vitamin_d": {"label": "Vitamin D", "unit": "mcg", "min": 15.0, "max": 100.0, "source": "sunlight", "goals": ["bone_health", "immunity", "mood_sleep"]},
            "vitamin_e": {"label": "Vitamin E", "unit": "mg", "min": 15.0, "max": 1000.0, "source": "nuts_seeds", "goals": ["heart_health", "skin_hair"]},
            "vitamin_k": {"label": "Vitamin K", "unit": "mcg", "min": 100.0, "max": 1000.0, "source": "vegetables", "goals": ["bone_health"]},
            "thiamin_b1": {"label": "Thiamin B1", "unit": "mg", "min": 1.2, "max": 50.0, "source": "whole_grains", "goals": ["energy"]},
            "riboflavin_b2": {"label": "Riboflavin B2", "unit": "mg", "min": 1.3, "max": 50.0, "source": "dairy", "goals": ["energy", "skin_hair"]},
            "niacin_b3": {"label": "Niacin B3", "unit": "mg", "min": 16.0, "max": 35.0, "source": "protein", "goals": ["energy"]},
            "pantothenic_acid_b5": {"label": "Pantothenic Acid B5", "unit": "mg", "min": 5.0, "max": 200.0, "source": "protein", "goals": ["energy"]},
            "vitamin_b6": {"label": "Vitamin B6", "unit": "mg", "min": 1.3, "max": 100.0, "source": "protein", "goals": ["energy", "mood_sleep"]},
            "biotin": {"label": "Biotin", "unit": "mcg", "min": 30.0, "max": 1000.0, "source": "protein", "goals": ["skin_hair"]},
            "folate_b9": {"label": "Folate B9", "unit": "mcg DFE", "min": 400.0, "max": 1000.0, "source": "legumes", "goals": ["energy"]},
            "vitamin_b12": {"label": "Vitamin B12", "unit": "mcg", "min": 2.4, "max": 100.0, "source": "protein", "goals": ["energy", "mood_sleep"]},
            "calcium": {"label": "Calcium", "unit": "mg", "min": 1000.0, "max": 2500.0, "source": "dairy", "goals": ["bone_health"]},
            "magnesium": {"label": "Magnesium", "unit": "mg", "min": 320.0, "max": 700.0, "source": "nuts_seeds", "goals": ["mood_sleep", "muscle_performance"]},
            "iron": {"label": "Iron", "unit": "mg", "min": 18.0, "max": 45.0, "source": "protein", "goals": ["energy"]},
            "zinc": {"label": "Zinc", "unit": "mg", "min": 8.0, "max": 40.0, "source": "protein", "goals": ["immunity", "skin_hair"]},
            "selenium": {"label": "Selenium", "unit": "mcg", "min": 55.0, "max": 400.0, "source": "protein", "goals": ["immunity"]},
            "copper": {"label": "Copper", "unit": "mg", "min": 0.9, "max": 10.0, "source": "nuts_seeds", "goals": ["skin_hair"]},
            "manganese": {"label": "Manganese", "unit": "mg", "min": 2.0, "max": 11.0, "source": "whole_grains", "goals": ["bone_health"]},
            "iodine": {"label": "Iodine", "unit": "mcg", "min": 150.0, "max": 1100.0, "source": "seafood", "goals": ["energy"]},
            "chromium": {"label": "Chromium", "unit": "mcg", "min": 35.0, "max": 1000.0, "source": "whole_grains", "goals": ["weight_management"]},
            "molybdenum": {"label": "Molybdenum", "unit": "mcg", "min": 45.0, "max": 2000.0, "source": "legumes", "goals": ["energy"]},
            "potassium": {"label": "Potassium", "unit": "mg", "min": 2600.0, "max": 5000.0, "source": "vegetables", "goals": ["heart_health", "muscle_performance"]},
            "sodium": {"label": "Sodium", "unit": "mg", "min": 500.0, "max": 2300.0, "source": "processed", "goals": ["muscle_performance"]},
            "chloride": {"label": "Chloride", "unit": "mg", "min": 2300.0, "max": 3600.0, "source": "processed", "goals": ["muscle_performance"]},
            "phosphorus": {"label": "Phosphorus", "unit": "mg", "min": 700.0, "max": 4000.0, "source": "protein", "goals": ["bone_health"]},
            "omega_3": {"label": "Omega-3", "unit": "g", "min": 1.1, "max": 5.0, "source": "seafood", "goals": ["heart_health", "mood_sleep"]},
            "omega_6": {"label": "Omega-6", "unit": "g", "min": 12.0, "max": 30.0, "source": "nuts_seeds", "goals": ["heart_health"]},
            "protein": {"label": "Protein", "unit": "g", "min": 50.0, "max": 200.0, "source": "protein", "goals": ["muscle_performance", "weight_management"]},
            "fiber": {"label": "Fiber", "unit": "g", "min": 28.0, "max": 70.0, "source": "vegetables", "goals": ["gut_health", "heart_health", "weight_management"]},
            "water": {"label": "Water", "unit": "L", "min": 2.0, "max": 6.0, "source": "water", "goals": ["energy", "muscle_performance"]},
            "choline": {"label": "Choline", "unit": "mg", "min": 425.0, "max": 3500.0, "source": "protein", "goals": ["energy"]},
            "coq10": {"label": "CoQ10", "unit": "mg", "min": 30.0, "max": 300.0, "source": "protein", "goals": ["energy", "heart_health"]},
            "collagen": {"label": "Collagen Peptides", "unit": "g", "min": 5.0, "max": 20.0, "source": "protein", "goals": ["skin_hair"]},
            "creatine": {"label": "Creatine", "unit": "g", "min": 3.0, "max": 10.0, "source": "protein", "goals": ["muscle_performance"]},
            "taurine": {"label": "Taurine", "unit": "mg", "min": 500.0, "max": 3000.0, "source": "protein", "goals": ["mood_sleep", "heart_health"]},
            "carnitine": {"label": "L-Carnitine", "unit": "mg", "min": 500.0, "max": 3000.0, "source": "protein", "goals": ["weight_management", "energy"]},
            "probiotics": {"label": "Probiotics", "unit": "servings", "min": 1.0, "max": 4.0, "source": "fermented", "goals": ["gut_health", "immunity"]},
            "prebiotics": {"label": "Prebiotics", "unit": "g", "min": 5.0, "max": 20.0, "source": "legumes", "goals": ["gut_health"]},
            "polyphenols": {"label": "Polyphenols", "unit": "mg", "min": 500.0, "max": 2000.0, "source": "fruit", "goals": ["heart_health"]},
            "curcumin": {"label": "Curcumin", "unit": "mg", "min": 250.0, "max": 1500.0, "source": "spices", "goals": ["joint_health"]},
            "lutein": {"label": "Lutein", "unit": "mg", "min": 6.0, "max": 20.0, "source": "vegetables", "goals": ["skin_hair"]},
            "zeaxanthin": {"label": "Zeaxanthin", "unit": "mg", "min": 2.0, "max": 10.0, "source": "vegetables", "goals": ["skin_hair"]},
            "lycopene": {"label": "Lycopene", "unit": "mg", "min": 8.0, "max": 30.0, "source": "fruit", "goals": ["heart_health", "skin_hair"]},
            "anthocyanins": {"label": "Anthocyanins", "unit": "mg", "min": 50.0, "max": 500.0, "source": "fruit", "goals": ["heart_health"]},
            "glucosamine": {"label": "Glucosamine", "unit": "mg", "min": 1500.0, "max": 3000.0, "source": "supplement", "goals": ["joint_health"]},
            "msm": {"label": "MSM", "unit": "mg", "min": 1000.0, "max": 3000.0, "source": "supplement", "goals": ["joint_health"]},
            "ashwagandha": {"label": "Ashwagandha", "unit": "mg", "min": 300.0, "max": 1000.0, "source": "supplement", "goals": ["mood_sleep"]},
            "melatonin": {"label": "Melatonin", "unit": "mg", "min": 0.5, "max": 5.0, "source": "sleep", "goals": ["mood_sleep"]},
            "electrolytes": {"label": "Electrolytes", "unit": "score", "min": 1.0, "max": 5.0, "source": "water", "goals": ["muscle_performance"]},
            "boron": {"label": "Boron", "unit": "mg", "min": 1.0, "max": 20.0, "source": "fruit", "goals": ["bone_health"]},
            "silicon": {"label": "Silicon", "unit": "mg", "min": 10.0, "max": 50.0, "source": "whole_grains", "goals": ["skin_hair", "bone_health"]},
            "glutamine": {"label": "L-Glutamine", "unit": "g", "min": 5.0, "max": 20.0, "source": "protein", "goals": ["gut_health", "muscle_performance"]},
            "green_tea_extract": {"label": "Green Tea Extract", "unit": "mg", "min": 250.0, "max": 800.0, "source": "fruit", "goals": ["weight_management"]},
        }
    )

    nutrient_recommendation_copy: dict[str, dict[str, str]] = Field(
        default_factory=lambda: {
            "vitamin_a": {
                "low": "Increase vitamin A rich foods such as carrots, sweet potatoes, leafy greens, eggs, and dairy.",
                "normal": "Current vitamin A intake is within the configured target range.",
                "high": "Reduce high-dose vitamin A supplements and retinol-heavy sources unless supervised.",
            },
            "zinc": {
                "low": "Consider zinc sources such as seafood, beef, pumpkin seeds, beans, and fortified grains.",
                "normal": "Current zinc intake is within the configured target range.",
                "high": "Avoid stacking multiple zinc supplements because excess zinc may affect copper and iron balance.",
            },
            "iron": {
                "low": "Prioritize iron sources such as lean meat, seafood, beans, spinach, and vitamin C paired meals.",
                "normal": "Current iron intake is within the configured target range.",
                "high": "Avoid additional iron supplementation unless a clinician confirms it is needed.",
            },
            "magnesium": {
                "low": "Increase magnesium sources such as nuts, seeds, legumes, whole grains, and dark leafy greens.",
                "normal": "Current magnesium intake is within the configured target range.",
                "high": "Review magnesium-containing supplements or laxatives if intake is above target.",
            },
            "vitamin_b6": {
                "low": "Consider vitamin B6 sources such as poultry, fish, potatoes, chickpeas, and bananas.",
                "normal": "Current vitamin B6 intake is within the configured target range.",
                "high": "Avoid high-dose vitamin B6 supplements unless specifically supervised.",
            },
            "omega_3": {
                "low": "Increase omega-3 intake from fatty fish, algae oil, chia, flax, walnuts, or EPA/DHA supplements.",
                "normal": "Current omega-3 intake is within the configured target range.",
                "high": "Review high-dose omega-3 supplementation, especially if using anticoagulant medication.",
            },
            "vitamin_d": {
                "low": "Consider vitamin D from sunlight exposure, fortified foods, fatty fish, eggs, or supplements.",
                "normal": "Current vitamin D intake is within the configured target range.",
                "high": "Avoid adding vitamin D supplements until intake and lab values are reviewed.",
            },
        }
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
