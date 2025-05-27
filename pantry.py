# smart_pantry_app/pantry.py

import streamlit as st
from datetime import datetime, timedelta
from PIL import Image
import easyocr
import json
import numpy as np
import google.generativeai as genai

# ✅ Hardcoded Gemini API Key for local dev
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# In-memory pantry list
if 'pantry' not in st.session_state:
    st.session_state['pantry'] = []

# Editable pantry display
def edit_pantry():
    updated = st.data_editor(
        st.session_state['pantry'],
        use_container_width=True,
        num_rows="dynamic",
        key="pantry_editor"
    )
    if st.button("💾 Save Pantry Changes"):
        st.session_state['pantry'] = updated
        st.success("Pantry updated!")

# Pantry loading
def load_pantry():
    return st.session_state['pantry']

# Manual add
def add_item_manual(name, purchase_date, expiry_date, quantity, high_priority):
    st.session_state['pantry'].append({
        "name": name,
        "purchase_date": str(purchase_date) if purchase_date else "",
        "expiry_date": str(expiry_date) if expiry_date else "",
        "quantity": quantity,
        "high_priority": high_priority
    })

# Delete item from pantry
def delete_item_by_name(item_name):
    st.session_state['pantry'] = [item for item in st.session_state['pantry'] if item['name'].lower() != item_name.lower()]

# Estimate expiry helper
def estimate_expiry(purchase_date, food_type):
    food_type = food_type.lower().strip()
    lifespans = {
        'apples': 21, 'blueberries': 7, 'broccoli': 7, 'cauliflower': 7,
        'chard': 3, 'kale': 3, 'spinach': 3, 'leafy herbs': 3,
        'lemons': 21, 'limes': 21, 'lettuce': 5, 'melon': 5,
        'mushrooms': 7, 'strawberries': 3, 'raspberries': 3,
        'winter squash': 7, 'woody herbs': 21,
        'hard cheese': 180, 'butter': 90, 'cream cheese': 60, 'eggs': 30,
        'heavy cream': 30, 'milk': 7, 'ricotta': 7, 'cottage cheese': 7,
        'sour cream': 21, 'soft cheese': 14, 'tofu': 21, 'yogurt': 14,
        'bacon': 14, 'chicken': 2, 'cold cuts': 14, 'fish': 2,
        'ground meat': 2, 'hot dogs': 14, 'pork': 5, 'shrimp': 2,
        'shellfish': 2, 'steaks': 5,
        'salt': '', 'sugar': '', 'white rice': '', 'vinegar': '',
        'baking soda': '', 'honey': '', 'soy sauce': 365, 'maple syrup': 365
    }
    if food_type in lifespans:
        days = lifespans[food_type]
        if days == '':
            return ""  # Non-expiring item
        expiry = datetime.strptime(str(purchase_date), "%Y-%m-%d").date()
        return str(expiry + timedelta(days=days))
    else:
        try:
            ai_response = model.generate_content(
                f"Roughly how many days is {food_type} safe to store in the fridge? Only return a number."
            )
            days = int(''.join(filter(str.isdigit, ai_response.text)))
            expiry = datetime.strptime(str(purchase_date), "%Y-%m-%d").date()
            return str(expiry + timedelta(days=days))
        except:
            return ""

# Receipt extraction and expiry suggestion
def extract_items_from_receipt(image_file):
    image = Image.open(image_file).convert("RGB")
    image_np = np.array(image)
    reader = easyocr.Reader(['en'], gpu=False)
    raw_text_lines = reader.readtext(image_np, detail=0)
    joined_text = "\n".join(raw_text_lines)

    try:
        ai_response = model.generate_content(
            f"""
You are a helpful assistant.
Given the following receipt OCR text, return only the actual food items purchased, one per line.
Ignore store names, total prices, timestamps, and greetings.

Text:
{joined_text}

List:
"""
        )
        filtered_lines = ai_response.text.strip().split("\n")
    except Exception as e:
        st.warning(f"Gemini filtering failed, using raw text. Error: {e}")
        filtered_lines = raw_text_lines

    items = []
    for line in filtered_lines:
        if line.strip():
            item_name = line.strip()
            expiry = estimate_expiry(datetime.today().date(), item_name)
            items.append({
                "name": item_name,
                "quantity": 1,
                "purchase_date": str(datetime.today().date()),
                "expiry_date": expiry,
                "high_priority": False
            })
    st.session_state['pantry'].extend(items)
    return items

# JSON uploader and auto expiry checker
def upload_saved_pantry(file):
    if file:
        uploaded = json.load(file)
        for item in uploaded:
            name = item.get('name')
            if name:
                purchase_date = item.get("purchase_date", str(datetime.today().date()))
                expiry = item.get("expiry_date") or estimate_expiry(purchase_date, name)
                st.session_state['pantry'].append({
                    "name": name,
                    "purchase_date": purchase_date,
                    "expiry_date": expiry,
                    "quantity": item.get("quantity", 1),
                    "high_priority": item.get("high_priority", False)
                })
