"""Streamlit testing UI for the personalized NutriMatch API."""

import requests
import streamlit as st


API_URL = "http://localhost:8000/api/analyze"


def main() -> None:
    """Render a small manual test UI for the personalized nutrition API."""

    st.set_page_config(page_title="NutriMatch Personalized Test UI", layout="wide")
    st.title("NutriMatch Personalized Nutrition Test UI")

    col_a, col_b = st.columns(2)
    with col_a:
        age = st.number_input("Age", min_value=1, max_value=120, value=34)
        sex = st.selectbox("Sex", ["female", "male", "other"])
        height_cm = st.number_input("Height cm", min_value=80.0, max_value=230.0, value=165.0)
        weight_kg = st.number_input("Weight kg", min_value=20.0, max_value=300.0, value=58.0)
    with col_b:
        routine = st.selectbox("Routine", ["early_sleep", "late_sleep", "shift_work"])
        exercise = st.number_input("Exercise per week", min_value=0, max_value=14, value=2)
        water = st.number_input("Water L/day", min_value=0.0, max_value=8.0, value=1.5)

    diet_habits = st.multiselect(
        "Diet habits",
        ["eating_out", "vegetarian", "low_carb", "high_protein", "high_sugar", "low_fiber", "irregular_meals"],
        ["eating_out"],
    )
    special_groups = st.multiselect(
        "Special groups",
        [
            "pregnant",
            "trying_to_conceive",
            "breastfeeding",
            "senior",
            "teenager",
            "chronic_patient",
            "metabolic_risk",
            "vegetarian",
        ],
    )
    symptom_tags = st.multiselect(
        "Symptoms and lifestyle states",
        [
            "sensitive_gut",
            "sleep_disorder",
            "high_stress",
            "sedentary_worker",
            "frequent_late_nights",
            "fatigue",
            "poor_focus",
            "dry_eyes",
            "muscle_cramps",
        ],
        ["high_stress", "frequent_late_nights"],
    )
    chronic_conditions = []
    if "chronic_patient" in special_groups:
        chronic_conditions = st.multiselect(
            "Chronic conditions",
            [
                "diabetes",
                "hypertension",
                "cardiovascular_disease",
                "kidney_disease",
                "liver_disease",
                "gastric_ulcer_or_reflux",
                "autoimmune_disease",
            ],
        )

    health_goals = st.multiselect(
        "Health goals",
        [
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
        ],
        ["energy", "sleep", "immunity"],
    )

    current_supplements = st.multiselect(
        "Current DHC supplements",
        ["dhc-b-complex", "dhc-fish-oil", "dhc-lutein", "dhc-vitamin-c", "dhc-calcium-magnesium"],
    )

    if st.button("Analyze"):
        payload = {
            "profile": {
                "age": age,
                "sex": sex,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "routine": routine,
                "diet_habits": diet_habits,
                "exercise_frequency_per_week": exercise,
                "water_liters_per_day": water,
            },
            "special_groups": special_groups,
            "symptom_tags": symptom_tags,
            "chronic_conditions": chronic_conditions,
            "health_goals": health_goals,
            "current_supplements": [
                {
                    "product_id": product_id,
                }
                for product_id in current_supplements
            ],
        }
        response = requests.post(API_URL, json=payload, timeout=15)
        response.raise_for_status()
        st.json(response.json())


if __name__ == "__main__":
    main()
