export type Sex = "male" | "female" | "other";
export type Routine = "early_sleep" | "late_sleep" | "shift_work";

export type DietHabit =
  | "eating_out"
  | "vegetarian"
  | "low_carb"
  | "high_protein"
  | "high_sugar"
  | "low_fiber"
  | "irregular_meals";

export type SpecialGroup =
  | "pregnant"
  | "trying_to_conceive"
  | "breastfeeding"
  | "senior"
  | "teenager"
  | "chronic_patient"
  | "metabolic_risk"
  | "vegetarian";

export type SymptomTag =
  | "sensitive_gut"
  | "sleep_disorder"
  | "high_stress"
  | "sedentary_worker"
  | "frequent_late_nights"
  | "fatigue"
  | "poor_focus"
  | "dry_eyes"
  | "muscle_cramps";

export type ChronicCondition =
  | "diabetes"
  | "hypertension"
  | "cardiovascular_disease"
  | "kidney_disease"
  | "liver_disease"
  | "gastric_ulcer_or_reflux"
  | "autoimmune_disease";

export type HealthGoal =
  | "immunity"
  | "sleep"
  | "energy"
  | "brightening_antioxidant"
  | "eye_health"
  | "gut_health"
  | "fat_loss"
  | "muscle_gain"
  | "focus"
  | "women_health"
  | "men_health"
  | "bone_health"
  | "cardiovascular_health";

export type BasicProfile = {
  age: number;
  sex: Sex;
  height_cm: number;
  weight_kg: number;
  routine: Routine;
  diet_habits: DietHabit[];
  exercise_frequency_per_week: number;
  water_liters_per_day: number;
};

export type SupplementUse = {
  product_id: string;
};

export type AnalyzeRequest = {
  profile: BasicProfile;
  special_groups: SpecialGroup[];
  symptom_tags: SymptomTag[];
  chronic_conditions: ChronicCondition[];
  health_goals: HealthGoal[];
  current_supplements: SupplementUse[];
  use_ollama?: boolean;
};

export type DHCProduct = {
  id: string;
  name: string;
  category: string;
  nutrients: string[];
  functions: string[];
  suitableFor: string[];
  avoidFor: string[];
  intakeTiming: string;
  dosage: string;
  caution: string;
  imageUrl?: string | null;
  productUrl?: string | null;
};

export type NutrientAdvice = {
  nutrient: string;
  whyNeeded: string;
  foodSources: string[];
  recommendedSupplements: string[];
  intakeTiming: string;
  caution?: string | null;
  score: number;
};

export type SupplementReview = {
  productId: string;
  productName: string;
  comment: string;
  caution?: string | null;
};

export type AnalyzeResponse = {
  profileDescription: string;
  nutrientRecommendations: NutrientAdvice[];
  currentSupplementReview: SupplementReview[];
  coveredNutrients: string[];
  safetyNotes: string[];
  matchedProducts: DHCProduct[];
  localAI?: {
    status: "disabled" | "success" | "unavailable";
    model: string | null;
    explanation: string | null;
    message: string | null;
  };
};
