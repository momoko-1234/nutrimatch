"""Personalized nutrition recommendation logic."""

from app.schemas import AnalyzeRequest, AnalyzeResponse, NutrientAdvice, SupplementReview
from app.services.dhc_catalog import get_product_by_id, load_dhc_products


NUTRIENT_RULES: dict[str, dict[str, object]] = {
    "B Complex": {
        "goals": ["energy", "focus"],
        "groups": ["frequent_late_nights", "high_stress", "sedentary_worker"],
        "diet": ["eating_out", "irregular_meals"],
        "foods": ["全穀類", "雞蛋", "瘦肉", "豆類", "深綠色蔬菜"],
        "timing": "早餐後或午餐後",
        "caution": "避免和其他高劑量 B 群產品重複堆疊。",
    },
    "Magnesium": {
        "goals": ["sleep", "muscle_gain"],
        "groups": ["sleep_disorder", "high_stress", "frequent_late_nights", "muscle_cramps"],
        "diet": ["eating_out", "low_carb"],
        "foods": ["南瓜籽", "杏仁", "菠菜", "黑巧克力", "香蕉"],
        "timing": "晚餐後或睡前",
        "caution": "腎臟疾病者不建議自行補充高劑量鎂。",
    },
    "Omega-3": {
        "goals": ["cardiovascular_health", "focus"],
        "groups": ["metabolic_risk", "high_stress", "sedentary_worker"],
        "diet": ["eating_out", "low_fiber"],
        "foods": ["鮭魚", "鯖魚", "沙丁魚", "亞麻仁籽", "核桃"],
        "timing": "飯後補充吸收較佳",
        "caution": "使用抗凝血藥或近期手術者請先詢問醫師。",
    },
    "Vitamin D": {
        "goals": ["immunity", "bone_health"],
        "groups": ["sedentary_worker", "senior", "frequent_late_nights"],
        "diet": ["vegetarian"],
        "foods": ["日曬", "鮭魚", "蛋黃", "強化乳品", "菇類"],
        "timing": "含油脂餐後",
        "caution": "腎臟疾病、高血鈣或已補充高劑量維他命D者請先確認。",
    },
    "Vitamin C": {
        "goals": ["immunity", "brightening_antioxidant"],
        "groups": ["high_stress", "frequent_late_nights"],
        "diet": ["eating_out", "low_fiber"],
        "foods": ["芭樂", "奇異果", "柑橘", "甜椒", "花椰菜"],
        "timing": "飯後，可分次",
        "caution": "腎臟疾病或結石風險者請留意劑量。",
    },
    "Zinc": {
        "goals": ["immunity", "men_health"],
        "groups": ["vegetarian", "high_stress"],
        "diet": ["vegetarian", "high_sugar"],
        "foods": ["牡蠣", "牛肉", "南瓜籽", "豆類", "堅果"],
        "timing": "飯後，避免空腹",
        "caution": "避免長期高劑量鋅影響銅與鐵平衡。",
    },
    "Iron": {
        "goals": ["energy", "women_health"],
        "groups": ["vegetarian", "teenager", "trying_to_conceive", "fatigue"],
        "diet": ["vegetarian"],
        "foods": ["紅肉", "蛤蜊", "豆類", "菠菜", "黑芝麻"],
        "timing": "飯後或搭配維他命C食物",
        "caution": "男性、肝病、胃潰瘍或鐵質過量風險者不建議自行補充。",
    },
    "Calcium": {
        "goals": ["bone_health"],
        "groups": ["senior", "teenager", "breastfeeding"],
        "diet": ["vegetarian", "low_carb"],
        "foods": ["牛奶", "優格", "豆腐", "小魚乾", "芝麻"],
        "timing": "餐後，與高劑量鐵錯開",
        "caution": "腎臟疾病或高血鈣者請先諮詢醫師。",
    },
    "Lutein": {
        "goals": ["eye_health"],
        "groups": ["sedentary_worker", "frequent_late_nights", "dry_eyes"],
        "diet": [],
        "foods": ["菠菜", "羽衣甘藍", "蛋黃", "玉米", "南瓜"],
        "timing": "含油脂餐後",
        "caution": None,
    },
    "Probiotics": {
        "goals": ["gut_health", "immunity"],
        "groups": ["sensitive_gut"],
        "diet": ["eating_out", "low_fiber", "high_sugar"],
        "foods": ["優格", "優酪乳", "泡菜", "味噌", "納豆"],
        "timing": "早餐前後或睡前，依產品標示",
        "caution": "免疫低下或重大疾病治療中者請先諮詢醫師。",
    },
    "CoQ10": {
        "goals": ["energy", "cardiovascular_health"],
        "groups": ["senior", "metabolic_risk", "fatigue"],
        "diet": [],
        "foods": ["魚類", "牛肉", "雞肉", "花生", "花椰菜"],
        "timing": "含油脂餐後",
        "caution": "使用抗凝血藥或心血管藥物者請先詢問醫師。",
    },
    "Collagen": {
        "goals": ["brightening_antioxidant", "women_health"],
        "groups": [],
        "diet": ["low_carb"],
        "foods": ["魚皮", "雞湯", "蛋白質食物", "維他命C水果"],
        "timing": "晚間或餐後皆可",
        "caution": "對魚類或明膠來源過敏者需確認來源。",
    },
    "DHA": {
        "goals": ["focus", "eye_health"],
        "groups": ["teenager", "senior", "sedentary_worker", "poor_focus"],
        "diet": [],
        "foods": ["鮭魚", "鯖魚", "秋刀魚", "藻油"],
        "timing": "飯後",
        "caution": "魚類過敏或抗凝血藥使用者請先確認。",
    },
}

NUTRIENT_TO_DHC_PRODUCT_IDS = {
    "B Complex": ["dhc-b-complex"],
    "Omega-3": ["dhc-fish-oil"],
    "Vitamin D": ["dhc-vitamin-d"],
    "Vitamin C": ["dhc-vitamin-c"],
    "Lutein": ["dhc-lutein", "dhc-blueberry"],
    "Probiotics": ["dhc-probiotics"],
    "Zinc": ["dhc-zinc"],
    "Iron": ["dhc-iron"],
    "Calcium": ["dhc-calcium-magnesium"],
    "CoQ10": ["dhc-coq10"],
    "Collagen": ["dhc-collagen"],
    "DHA": ["dhc-dha"],
}

PRODUCT_COVERAGE = {
    "dhc-b-complex": {"B Complex"},
    "dhc-fish-oil": {"Omega-3"},
    "dhc-dha": {"DHA", "Omega-3"},
    "dhc-vitamin-d": {"Vitamin D"},
    "dhc-vitamin-c": {"Vitamin C"},
    "dhc-lutein": {"Lutein"},
    "dhc-blueberry": {"Lutein"},
    "dhc-probiotics": {"Probiotics"},
    "dhc-zinc": {"Zinc"},
    "dhc-iron": {"Iron"},
    "dhc-calcium-magnesium": {"Calcium", "Magnesium"},
    "dhc-coq10": {"CoQ10"},
    "dhc-collagen": {"Collagen"},
    "dhc-multivitamin": {"B Complex", "Vitamin C", "Vitamin D"},
}

GENERIC_SUPPLEMENT_OPTIONS = {
    "Magnesium": ["甘胺酸鎂或檸檬酸鎂補充品"],
    "Calcium": ["鈣鎂複方或鈣+D配方"],
    "CoQ10": ["泛醌或還原型Q10補充品"],
    "Collagen": ["膠原蛋白胜肽搭配維他命C"],
    "Probiotics": ["多菌株益生菌或發酵食品"],
}

CHRONIC_CAUTION_NOTES = {
    "diabetes": "糖尿病族群請留意含糖配方與血糖監測，補充品不可取代飲食與藥物管理。",
    "hypertension": "高血壓族群需留意含鈉、刺激性或可能影響血壓的配方。",
    "cardiovascular_disease": "心血管疾病或使用抗凝血藥者，魚油、Q10、薑黃等產品請先詢問醫師。",
    "kidney_disease": "腎臟疾病者需避免自行補充高劑量礦物質、蛋白質或脂溶性維生素。",
    "liver_disease": "肝臟疾病者不建議自行使用護肝草本或高劑量脂溶性營養素。",
    "gastric_ulcer_or_reflux": "胃潰瘍或胃食道逆流族群，鐵、魚油、薑黃等可能刺激腸胃的產品需謹慎。",
    "autoimmune_disease": "自體免疫疾病或免疫調節治療中，益生菌、蜂王乳、胎盤素等請先諮詢專業人員。",
}

LABELS = {
    "eating_out": "外食比例高",
    "vegetarian": "素食",
    "low_carb": "低碳飲食",
    "high_protein": "高蛋白飲食",
    "high_sugar": "甜食或含糖飲較多",
    "low_fiber": "蔬果纖維偏少",
    "irregular_meals": "三餐不固定",
    "chronic_patient": "慢性病患",
    "metabolic_risk": "三高風險",
    "sensitive_gut": "腸胃敏感",
    "sleep_disorder": "睡眠障礙",
    "high_stress": "壓力偏高／焦慮",
    "sedentary_worker": "久坐上班族",
    "frequent_late_nights": "經常熬夜",
    "fatigue": "容易疲勞",
    "poor_focus": "專注力不佳",
    "dry_eyes": "眼睛乾澀",
    "muscle_cramps": "肌肉緊繃或抽筋",
    "senior": "銀髮族",
    "teenager": "青少年",
    "pregnant": "孕婦",
    "trying_to_conceive": "備孕中",
    "breastfeeding": "哺乳中",
}


def build_personalized_advice(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Build a personalized nutrition advice response."""

    covered_nutrients = get_covered_nutrients(payload)
    scored_advice = [
        build_nutrient_advice(nutrient, rule, payload)
        for nutrient, rule in NUTRIENT_RULES.items()
    ]
    scored_advice = [
        apply_supplement_coverage(advice, covered_nutrients)
        for advice in scored_advice
    ]
    nutrient_recommendations = sorted(scored_advice, key=lambda item: item.score, reverse=True)[:8]

    selected_products = [
        product
        for supplement in payload.current_supplements
        if (product := get_product_by_id(supplement.product_id)) is not None
    ]
    matched_products = dedupe_products(
        [
            product
            for advice in nutrient_recommendations
            for product in load_dhc_products()
            if product.name in advice.recommendedSupplements
        ]
    )

    return AnalyzeResponse(
        profileDescription=build_profile_description(payload, nutrient_recommendations),
        nutrientRecommendations=nutrient_recommendations,
        currentSupplementReview=build_supplement_reviews(payload),
        coveredNutrients=sorted(covered_nutrients),
        safetyNotes=build_safety_notes(payload, selected_products),
        matchedProducts=matched_products,
    )


def build_nutrient_advice(nutrient: str, rule: dict[str, object], payload: AnalyzeRequest) -> NutrientAdvice:
    """Score one nutrient and convert it to display-ready advice."""

    score = 0.15
    reasons: list[str] = []
    goals = set(payload.health_goals)
    groups = set(payload.special_groups) | set(payload.symptom_tags)
    diets = set(payload.profile.diet_habits)

    matched_goals = goals & set(rule["goals"])
    matched_groups = groups & set(rule["groups"])
    matched_diets = diets & set(rule["diet"])

    score += 0.28 * len(matched_goals)
    score += 0.2 * len(matched_groups)
    score += 0.16 * len(matched_diets)

    if payload.profile.routine in {"late_sleep", "shift_work"} and nutrient in {"B Complex", "Magnesium", "Omega-3", "Vitamin D"}:
        score += 0.18
        reasons.append("作息偏晚或輪班會提高能量代謝、睡眠調節與抗壓營養素的需求")
    if payload.profile.water_liters_per_day < 1.5 and nutrient in {"Magnesium", "Probiotics"}:
        score += 0.08
        reasons.append("飲水量偏低時，腸胃節律與疲勞感較容易受影響")
    if payload.profile.exercise_frequency_per_week >= 4 and nutrient in {"Magnesium", "Omega-3", "Calcium"}:
        score += 0.1
        reasons.append("運動頻率較高時，肌肉放鬆、骨骼與修復營養需要更穩定")
    if payload.profile.age >= 55 and nutrient in {"Vitamin D", "Calcium", "CoQ10", "DHA"}:
        score += 0.16
        reasons.append("熟齡族群更需要留意骨骼、心血管與認知支持")

    reasons.extend(build_match_reasons(matched_goals, matched_groups, matched_diets))
    if not reasons:
        reasons.append("依目前問卷資料，此營養素可作為基礎保養的補強選項")

    return NutrientAdvice(
        nutrient=nutrient,
        whyNeeded="；".join(reasons[:3]) + "。",
        foodSources=list(rule["foods"]),
        recommendedSupplements=find_recommended_product_names(nutrient),
        intakeTiming=str(rule["timing"]),
        caution=rule["caution"],
        score=round(min(score, 1.0), 4),
    )


def get_covered_nutrients(payload: AnalyzeRequest) -> set[str]:
    """Return nutrient advice keys already covered by selected supplements."""

    covered: set[str] = set()
    for supplement in payload.current_supplements:
        covered.update(PRODUCT_COVERAGE.get(supplement.product_id, set()))
    return covered


def apply_supplement_coverage(advice: NutrientAdvice, covered_nutrients: set[str]) -> NutrientAdvice:
    """Lower priority when the user's daily supplement stack already covers the nutrient."""

    if advice.nutrient not in covered_nutrients:
        return advice

    adjusted_score = round(max(0.05, advice.score * 0.45), 4)
    coverage_note = "你已在個人化保健品管理中加入相關 DHC 品項，因此此營養素視為部分覆蓋，優先級已下調。"
    return advice.model_copy(
        update={
            "score": adjusted_score,
            "whyNeeded": f"{advice.whyNeeded}{coverage_note}",
            "recommendedSupplements": [
                item for item in advice.recommendedSupplements if not item.startswith("DHC")
            ] or ["目前已由你的日常保健品部分覆蓋，先檢查飲食與重複補充"],
        }
    )


def build_match_reasons(goals: set[str], groups: set[str], diets: set[str]) -> list[str]:
    """Build short reason fragments from matched inputs."""

    reasons: list[str] = []
    if goals:
        reasons.append("你的健康目標與此營養素的功能方向高度相關")
    if "high_stress" in groups or "sleep_disorder" in groups:
        reasons.append("壓力與睡眠狀態可能讓恢復與神經調節營養需求上升")
    if "sedentary_worker" in groups:
        reasons.append("久坐與長時間用眼族群需要更留意循環、眼睛與代謝支持")
    if "vegetarian" in groups or "vegetarian" in diets:
        reasons.append("素食飲食較容易需要留意特定礦物質與脂溶性營養素")
    if "eating_out" in diets:
        reasons.append("外食比例高時，蔬果、好油脂與微量營養素較容易不穩定")
    return reasons


def find_recommended_product_names(nutrient: str) -> list[str]:
    """Find recommended supplement names without forcing every item to DHC."""

    product_ids = set(NUTRIENT_TO_DHC_PRODUCT_IDS.get(nutrient, []))
    names = [product.name for product in load_dhc_products() if product.id in product_ids]
    if names:
        return names
    return GENERIC_SUPPLEMENT_OPTIONS.get(nutrient, [])


def build_profile_description(payload: AnalyzeRequest, recommendations: list[NutrientAdvice]) -> str:
    """Create a natural language summary without diagnostic wording."""

    routine_text = {
        "early_sleep": "作息相對規律",
        "late_sleep": "有熬夜或睡眠偏晚的情況",
        "shift_work": "屬於輪班作息",
    }[payload.profile.routine]
    diet_text = join_labels(payload.profile.diet_habits) if payload.profile.diet_habits else "飲食型態未見明顯限制"
    group_text = join_labels(payload.special_groups) if payload.special_groups else "未勾選特殊族群"
    symptom_text = join_labels(payload.symptom_tags) if payload.symptom_tags else "未勾選明顯症狀或生活狀態"
    top_names = "、".join(advice.nutrient for advice in recommendations[:3])

    return (
        f"依照你的問卷，目前呈現「{routine_text}」且飲食特徵包含 {diet_text}；"
        f"特殊族群標記為 {group_text}，症狀與生活狀態包含 {symptom_text}。整體來看，系統會優先留意 {top_names}。"
        "這些建議偏向日常營養支持與保養規劃，不代表疾病診斷；若你同時有慢性病或正在用藥，建議把補充品清單帶給醫師或營養師確認。"
    )


def join_labels(values: list[str]) -> str:
    """Convert internal enum values to readable Chinese labels."""

    return "、".join(LABELS.get(value, value) for value in values)


def build_supplement_reviews(payload: AnalyzeRequest) -> list[SupplementReview]:
    """Review the user's currently used DHC products."""

    reviews: list[SupplementReview] = []
    avoid_terms = set(payload.special_groups) | set(payload.chronic_conditions)

    for supplement in payload.current_supplements:
        product = get_product_by_id(supplement.product_id)
        if product is None:
            continue

        overlap = avoid_terms & set(product.avoidFor)
        caution = (
            f"你勾選的族群或慢性狀態與此產品注意事項重疊：{', '.join(sorted(overlap))}。"
            if overlap
            else product.caution
        )
        reviews.append(
            SupplementReview(
                productId=product.id,
                productName=product.name,
                comment=(
                    f"此品項資料庫建議量為「{product.dosage}」。"
                    f"分析時會把它視為你日常補充品的一部分，並檢查是否與其他產品重複補到 {', '.join(product.nutrients[:3])}。"
                ),
                caution=caution,
            )
        )

    return reviews


def build_safety_notes(payload: AnalyzeRequest, selected_products: list) -> list[str]:
    """Build safety notes from chronic conditions and selected products."""

    notes = [
        CHRONIC_CAUTION_NOTES[condition]
        for condition in payload.chronic_conditions
        if condition in CHRONIC_CAUTION_NOTES
    ]
    if {"pregnant", "breastfeeding", "trying_to_conceive"} & set(payload.special_groups):
        notes.append("孕期、備孕與哺乳期補充品劑量需更保守，請優先確認葉酸、鐵、DHA、維生素D等核心項目，草本與荷爾蒙相關產品不建議自行使用。")

    avoid_terms = set(payload.special_groups) | set(payload.chronic_conditions)
    for product in selected_products:
        overlap = avoid_terms & set(product.avoidFor)
        if overlap:
            notes.append(f"{product.name} 的 avoidFor 與你的狀態重疊：{', '.join(sorted(overlap))}。")

    return dedupe_strings(notes)


def dedupe_products(products: list) -> list:
    """Remove duplicate products while preserving order."""

    seen = set()
    unique_products = []
    for product in products:
        if product.id not in seen:
            seen.add(product.id)
            unique_products.append(product)
    return unique_products


def dedupe_strings(items: list[str]) -> list[str]:
    """Remove duplicate strings while preserving order."""

    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
