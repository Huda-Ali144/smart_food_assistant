# smart_pantry_app/preferences.py

import streamlit as st

def get_user_preferences():
    st.header("🧠 Set Your Food Preferences")

    with st.expander("Customize Recipe Filters"):
        cuisine = st.selectbox("Preferred Cuisine", ["Any", "Indian", "Italian", "Mexican", "Asian", "Middle Eastern"])
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        diet = st.text_input("Dietary Preference (e.g., Vegetarian, Halal, Keto, etc.)", value="None")
        allergies = st.text_input("Allergies (comma-separated, e.g., peanuts, dairy)", value="")
        max_time = st.number_input("Max Time to Cook (minutes)", min_value=5, max_value=240, value=30)
        ready_to_shop = st.radio("Are you ready to shop for ingredients if needed?", ["Yes", "No"])

    return {
        "cuisine": cuisine,
        "meal_type": meal_type,
        "diet": diet,
        "allergies": allergies,
        "max_time": max_time,
        "ready_to_shop": ready_to_shop
    }
