# smart_pantry_app/recipe_engine.py

import streamlit as st
import google.generativeai as genai
import os
from pantry import load_pantry
from preferences import get_user_preferences
from datetime import datetime, date

# ✅ Hardcoded Gemini API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Load Gemini model safely
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Model loading failed: {e}")
    model = None

# Init session state
if "chat_convo" not in st.session_state:
    if model:
        st.session_state.chat_convo = model.start_chat(history=[])
    else:
        st.session_state.chat_convo = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "initial_prompt_sent" not in st.session_state:
    st.session_state.initial_prompt_sent = False

if "latest_recipe_text" not in st.session_state:
    st.session_state.latest_recipe_text = ""

if "latest_ingredients_used" not in st.session_state:
    st.session_state.latest_ingredients_used = []

# Prompt builder

def generate_prompt(preferences):
    pantry_items = load_pantry()
    today = date.today()
    filtered_items = [item for item in pantry_items if item.get('name') and (not item['expiry_date'] or item['expiry_date'] >= str(today))]
    ingredients = ", ".join([item['name'] for item in filtered_items]) or "no usable ingredients"

    allergies = preferences.get("allergies", "")
    diet = preferences.get("diet", "None")
    max_time = preferences.get("max_time", 30)
    cuisine = preferences.get("cuisine", "Any")
    meal_type = preferences.get("meal_type", "Dinner")
    ready_to_shop = preferences.get("ready_to_shop", "No")

    if ready_to_shop == "Yes":
        if ingredients != "no usable ingredients":
            ingredient_note = f"Prefer using my pantry items: {ingredients}, but you can include others I can shop for."
        else:
            ingredient_note = "You can include any common ingredients I can shop for. My pantry is currently empty or unsuitable."
    else:
        ingredient_note = f"Only use the following pantry items: {ingredients}."

    prompt = f"""
You are a helpful cooking assistant.
Suggest a {diet}-friendly {cuisine} {meal_type} recipe that takes under {max_time} minutes.
{ingredient_note}
My allergies are: {allergies}.

Respond conversationally and ask me if I like the suggestion or want a different one.
"""
    return prompt

# Remove ingredients used from pantry

def remove_used_ingredients(ingredients):
    pantry = load_pantry()
    updated_pantry = []
    used_names = set([name.strip().lower() for name in ingredients])
    for item in pantry:
        if item['name'].strip().lower() not in used_names:
            updated_pantry.append(item)
    st.session_state['pantry'] = updated_pantry

# Chat UI

def interactive_chat_loop():
    if not model or not st.session_state.chat_convo:
        st.error("Gemini model not loaded.")
        return

    st.subheader("🍳 Ask Anything About Recipes")

    if st.button("🔄 Reset Chat & Preferences"):
        st.session_state.chat_convo = model.start_chat(history=[])
        st.session_state.chat_history = []
        st.session_state.initial_prompt_sent = False
        st.session_state.latest_recipe_text = ""
        st.session_state.latest_ingredients_used = []
        st.rerun()

    # Show preference UI
    preferences = get_user_preferences()
    system_prompt = generate_prompt(preferences)

    if not st.session_state.initial_prompt_sent:
        st.session_state.chat_convo.send_message(system_prompt)
        st.session_state.initial_prompt_sent = True
        st.chat_message("assistant").write("Thanks! I’ll use your preferences to suggest recipes. Ask away!")

    for role, msg in st.session_state.chat_history:
        st.chat_message(role).write(msg)

    if prompt := st.chat_input("What recipe are you looking for?"):
        st.chat_message("user").write(prompt)
        st.session_state.chat_history.append(("user", prompt))

        try:
            response = st.session_state.chat_convo.send_message(prompt)
            recipe = response.text
            st.chat_message("assistant").write(recipe)
            st.session_state.chat_history.append(("assistant", recipe))
            st.session_state.latest_recipe_text = recipe

            # Extract ingredients from the recipe
            ingredients = [line for line in recipe.split("\n") if any(keyword in line.lower() for keyword in ["ingredient", "- ", ": ", ","])]
            st.session_state.latest_ingredients_used = ingredients

        except Exception as e:
            st.error(f"Error: {e}")

    # Always show recipe actions if available
    if st.session_state.latest_recipe_text:
        st.subheader("📄 Recipe Options")

        st.download_button(
            "💾 Download Recipe",
            st.session_state.latest_recipe_text,
            file_name=f"recipe_{datetime.today().date()}.txt"
        )

        if st.button("🧺 Remove Used Ingredients from Pantry"):
            remove_used_ingredients(st.session_state.latest_ingredients_used)
            st.success("Used ingredients removed from pantry.")
