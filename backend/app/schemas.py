"""Pydantic schemas for NutriMatch personalized nutrition advice."""

from typing import Literal

from pydantic import BaseModel, Field


Sex = Literal["male", "female", "other"]
Routine = Literal["early_sleep", "late_sleep", "shift_work"]
DietHabit = Literal[
    "eating_out",
    "vegetarian",
    "low_carb",
    "high_protein",
    "high_sugar",
    "low_fiber",
    "irregular_meals",
]
SpecialGroup = Literal[
    "pregnant",
    "trying_to_conceive",
    "breastfeeding",
    "senior",
    "teenager",
    "chronic_patient",
    "metabolic_risk",
    "vegetarian",
]
SymptomTag = Literal[
    "sensitive_gut",
    "sleep_disorder",
    "high_stress",
    "sedentary_worker",
    "frequent_late_nights",
    "fatigue",
    "poor_focus",
    "dry_eyes",
    "muscle_cramps",
]
ChronicCondition = Literal[
    "diabetes",
    "hypertension",
    "cardiovascular_disease",
    "kidney_disease",
    "liver_disease",
    "gastric_ulcer_or_reflux",
    "autoimmune_disease",
]
HealthGoal = Literal[
    "immunity",
    "sleep",
    "energy",
    "brightening_antioxidant",
    "eye_health",
    "gut_health",
    "fat_loss",
    "muscle_gain",
    "focus",
    "women_health",
    "men_health",
    "bone_health",
    "cardiovascular_health",
]


class BasicProfile(BaseModel):
    """User demographic and lifestyle information."""

    age: int = Field(..., ge=1, le=120)
    sex: Sex
    height_cm: float = Field(..., ge=80, le=230)
    weight_kg: float = Field(..., ge=20, le=300)
    routine: Routine
    diet_habits: list[DietHabit] = Field(default_factory=list)
    exercise_frequency_per_week: int = Field(0, ge=0, le=14)
    water_liters_per_day: float = Field(1.5, ge=0, le=8)


class NutritionQuestionnaire(BaseModel):
    """Legacy questionnaire shape kept for older engine modules."""

    meals_per_day: float = Field(3, ge=0, le=8)
    vegetable_servings: float = Field(2, ge=0, le=15)
    fruit_servings: float = Field(1, ge=0, le=10)
    protein_servings: float = Field(2, ge=0, le=10)
    dairy_servings: float = Field(1, ge=0, le=8)
    whole_grain_servings: float = Field(1, ge=0, le=10)
    seafood_servings_per_week: float = Field(1, ge=0, le=14)
    nuts_seeds_servings: float = Field(0, ge=0, le=8)
    legume_servings: float = Field(0, ge=0, le=8)
    fermented_food_servings: float = Field(0, ge=0, le=8)
    water_liters: float = Field(1.5, ge=0, le=8)
    sunlight_minutes: float = Field(10, ge=0, le=240)
    exercise_days_per_week: float = Field(2, ge=0, le=7)
    sleep_hours: float = Field(7, ge=0, le=14)
    ultra_processed_meals_per_week: float = Field(3, ge=0, le=30)
    alcohol_drinks_per_week: float = Field(0, ge=0, le=40)


class SupplementUse(BaseModel):
    """A currently used DHC supplement and use pattern."""

    product_id: str


class AnalyzeRequest(BaseModel):
    """Request body for personalized nutrition advice."""

    profile: BasicProfile
    special_groups: list[SpecialGroup] = Field(default_factory=list)
    symptom_tags: list[SymptomTag] = Field(default_factory=list)
    chronic_conditions: list[ChronicCondition] = Field(default_factory=list)
    health_goals: list[HealthGoal] = Field(default_factory=list)
    current_supplements: list[SupplementUse] = Field(default_factory=list)
    use_ollama: bool = False


class DHCProduct(BaseModel):
    """DHC product record used by the recommendation engine."""

    id: str
    name: str
    category: str
    nutrients: list[str]
    functions: list[str]
    suitableFor: list[str]
    avoidFor: list[str]
    intakeTiming: str
    dosage: str
    caution: str
    imageUrl: str | None = None
    productUrl: str | None = None


class NutrientAdvice(BaseModel):
    """A personalized nutrient recommendation."""

    nutrient: str
    whyNeeded: str
    foodSources: list[str]
    recommendedSupplements: list[str]
    intakeTiming: str
    caution: str | None = None
    score: float


class SupplementReview(BaseModel):
    """Review of a supplement the user already takes."""

    productId: str
    productName: str
    comment: str
    caution: str | None = None


class LocalAIAnalysis(BaseModel):
    status: Literal["disabled", "success", "unavailable"] = "disabled"
    model: str | None = None
    explanation: str | None = None
    message: str | None = None


class AnalyzeResponse(BaseModel):
    """Personalized nutrition advice response."""

    profileDescription: str
    nutrientRecommendations: list[NutrientAdvice]
    currentSupplementReview: list[SupplementReview]
    coveredNutrients: list[str] = Field(default_factory=list)
    safetyNotes: list[str]
    matchedProducts: list[DHCProduct]
    localAI: LocalAIAnalysis = Field(default_factory=LocalAIAnalysis)
