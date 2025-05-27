# smart_pantry_app/notifier.py

from datetime import datetime, timedelta
import streamlit as st
import pandas as pd

# Uses pantry already stored in session state

def get_soon_expiring(days=3):
    today = datetime.today().date()
    soon_items = []

    for item in st.session_state.get('pantry', []):
        try:
            expiry = datetime.strptime(item['expiry_date'], "%Y-%m-%d").date()
            days_left = (expiry - today).days
            if 0 <= days_left <= days:
                item['days_left'] = days_left
                soon_items.append(item)
            elif days_left < 0:
                item['days_left'] = days_left
                item['overdue'] = True
                soon_items.append(item)
        except Exception:
            continue  # Skip malformed dates

    # Sort by nearest expiry
    soon_items.sort(key=lambda x: x.get('days_left', 999))
    return soon_items


# 🆕 For visualizing expiration dates as a calendar-style timeline
def get_expiry_dataframe():
    data = []
    for item in st.session_state.get('pantry', []):
        try:
            expiry_date = datetime.strptime(item['expiry_date'], "%Y-%m-%d").date()
            data.append({
                "name": item.get("name", "Unknown"),
                "expiry_date": expiry_date,
                "quantity": item.get("quantity", 1),
                "high_priority": item.get("high_priority", False)
            })
        except Exception:
            continue  # skip items without valid dates

    return pd.DataFrame(data)