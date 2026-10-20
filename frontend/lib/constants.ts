import productCatalog from "../../data/dhc_products.json";
import type {
  ChronicCondition,
  DHCProduct,
  DietHabit,
  HealthGoal,
  Routine,
  SpecialGroup,
  SymptomTag
} from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const ROUTINES: Array<{ key: Routine; label: string }> = [
  { key: "early_sleep", label: "早睡／作息規律" },
  { key: "late_sleep", label: "熬夜／睡眠偏晚" },
  { key: "shift_work", label: "輪班作息" }
];

export const DIET_HABITS: Array<{ key: DietHabit; label: string }> = [
  { key: "eating_out", label: "外食" },
  { key: "vegetarian", label: "素食" },
  { key: "low_carb", label: "低碳" },
  { key: "high_protein", label: "高蛋白" },
  { key: "high_sugar", label: "甜食／含糖飲多" },
  { key: "low_fiber", label: "蔬果纖維少" },
  { key: "irregular_meals", label: "三餐不固定" }
];

export const SPECIAL_GROUPS: Array<{ key: SpecialGroup; label: string }> = [
  { key: "pregnant", label: "孕婦" },
  { key: "trying_to_conceive", label: "備孕中" },
  { key: "breastfeeding", label: "哺乳中" },
  { key: "senior", label: "銀髮族" },
  { key: "teenager", label: "青少年" },
  { key: "chronic_patient", label: "慢性病患" },
  { key: "metabolic_risk", label: "三高族群" },
  { key: "vegetarian", label: "素食者" }
];

export const SYMPTOM_TAGS: Array<{ key: SymptomTag; label: string }> = [
  { key: "sensitive_gut", label: "腸胃敏感" },
  { key: "sleep_disorder", label: "睡眠障礙" },
  { key: "high_stress", label: "壓力大／焦慮" },
  { key: "sedentary_worker", label: "久坐上班族" },
  { key: "frequent_late_nights", label: "經常熬夜" },
  { key: "fatigue", label: "容易疲勞" },
  { key: "poor_focus", label: "專注力不佳" },
  { key: "dry_eyes", label: "眼睛乾澀" },
  { key: "muscle_cramps", label: "肌肉緊繃／抽筋" }
];

export const CHRONIC_CONDITIONS: Array<{
  key: ChronicCondition;
  label: string;
}> = [
  { key: "diabetes", label: "糖尿病" },
  { key: "hypertension", label: "高血壓" },
  { key: "cardiovascular_disease", label: "心血管疾病" },
  { key: "kidney_disease", label: "腎臟疾病" },
  { key: "liver_disease", label: "肝臟疾病" },
  { key: "gastric_ulcer_or_reflux", label: "胃潰瘍／胃食道逆流" },
  { key: "autoimmune_disease", label: "自體免疫疾病" }
];

export const HEALTH_GOALS: Array<{ key: HealthGoal; label: string }> = [
  { key: "immunity", label: "提升免疫力" },
  { key: "sleep", label: "改善睡眠" },
  { key: "energy", label: "增加體力" },
  { key: "brightening_antioxidant", label: "美白抗氧化" },
  { key: "eye_health", label: "保護眼睛" },
  { key: "gut_health", label: "腸胃保健" },
  { key: "fat_loss", label: "減脂" },
  { key: "muscle_gain", label: "增肌" },
  { key: "focus", label: "改善專注力" },
  { key: "women_health", label: "女性保養" },
  { key: "men_health", label: "男性保養" },
  { key: "bone_health", label: "骨骼保健" },
  { key: "cardiovascular_health", label: "心血管保健" }
];

export const DHC_PRODUCTS: DHCProduct[] = productCatalog;
