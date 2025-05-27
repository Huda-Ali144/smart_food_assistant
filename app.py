# smart_pantry_app/app.py

import streamlit as st
st.set_page_config(page_title="🥫 Smart Pantry App", page_icon="🥫")

from pantry import load_pantry, add_item_manual, extract_items_from_receipt, upload_saved_pantry, estimate_expiry, edit_pantry
from recipe_engine import interactive_chat_loop
from notifier import get_soon_expiring, get_expiry_dataframe
from preferences import get_user_preferences
from datetime import date, timedelta
import json
import altair as alt

# Sidebar navigation
st.sidebar.title("📚 Navigation")
page = st.sidebar.radio("Go to", ["Upload & Add Items", "Pantry Overview", "Expiring Soon", "Chat Recipe Bot"])

st.title("🥫 Smart Pantry & Recipe Assistant")

if page == "Upload & Add Items":
    st.header("📤 Upload Pantry or Receipt")
    upload_type = st.radio("Upload Type", ["Upload Receipt Image", "Upload Previous Pantry List (JSON)"])

    if upload_type == "Upload Receipt Image":
        image_file = st.file_uploader("Upload your grocery receipt image", type=["jpg", "jpeg", "png"])
        if image_file and st.button("Extract Items from Receipt"):
            items = extract_items_from_receipt(image_file)
            st.session_state['extracted_items'] = items
            st.success(f"Extracted {len(items)} items. Please review before adding.")

    if 'extracted_items' in st.session_state and st.session_state['extracted_items']:
        st.subheader("📝 Review Extracted Items")
        updated_items = st.data_editor(
            st.session_state['extracted_items'],
            num_rows="dynamic",
            use_container_width=True,
            key="receipt_editor"
        )
        if st.button("✅ Confirm and Add to Pantry"):
            for item in updated_items:
                add_item_manual(
                    item['name'],
                    item.get('purchase_date', ""),
                    item.get('expiry_date', ""),
                    item['quantity'],
                    item['high_priority']
                )
            st.success(f"✅ Added {len(updated_items)} reviewed items to pantry!")
            st.session_state['extracted_items'] = []

    elif upload_type == "Upload Previous Pantry List (JSON)":
        pantry_file = st.file_uploader("Upload saved pantry JSON file", type=["json"])
        if pantry_file and st.button("Import Pantry List"):
            upload_saved_pantry(pantry_file)
            st.success("Pantry list imported!")

    st.header("✍️ Add Pantry Item Manually")
    with st.form("add_item"):
        name = st.text_input("Item Name")
        purchase_date = st.date_input("Purchase Date", value=date.today())
        expiry_choice = st.radio("Do you know the expiry date?", ["Yes", "No"])

        expiry_date = ""
        if expiry_choice == "Yes":
            expiry_date = st.date_input("Expiry Date")
        else:
            food_type = st.text_input("What type of food is it? (e.g., milk, bread, spinach)")
            if food_type:
                estimated = estimate_expiry(purchase_date, food_type)
                if estimated:
                    st.markdown(f"📅 **Estimated Expiry:** {estimated}")
                    use_estimate = st.checkbox("Use suggested expiry?", value=True)
                    if use_estimate:
                        expiry_date = estimated
                    else:
                        expiry_date = st.date_input("Custom Expiry Date")
                else:
                    st.info("No expiry needed or unable to estimate.")
                    expiry_date = ""

        quantity = st.number_input("Quantity", min_value=1, value=1)
        high_priority = st.checkbox("Mark as High Priority")
        submitted = st.form_submit_button("Add Item")

        if submitted and name:
            add_item_manual(name, purchase_date, expiry_date, quantity, high_priority)
            st.success(f"✅ {quantity} x {name} added to pantry!")

elif page == "Pantry Overview":
    st.header("🧺 Your Pantry")
    pantry = load_pantry()
    if pantry:
        st.data_editor(
            pantry,
            key="pantry_editor",
            num_rows="dynamic",
            use_container_width=True
        )
        if st.button("💾 Save Pantry Changes"):
            st.session_state['pantry'] = st.session_state["pantry_editor"]
            st.success("Pantry updated!")

        pantry_json = json.dumps(pantry, indent=2)
        st.download_button("📤 Download Pantry List (JSON)", pantry_json, file_name="pantry.json")
    else:
        st.info("No pantry items yet. Add something under Upload & Add Items.")

elif page == "Expiring Soon":
    st.header("⏰ Items Expiring Soon")
    soon = get_soon_expiring(days=3)
    if soon:
        for item in soon:
            msg = f"⚠️ {item['name']} expires in {item['days_left']} day(s)"
            if item.get("overdue"):
                st.error(f"❌ {item['name']} expired {-item['days_left']} day(s) ago!")
            else:
                st.warning(msg)
    else:
        st.success("Nothing is expiring in the next 3 days.")

    # Calendar Visualization
    from notifier import get_expiry_dataframe
    df = get_expiry_dataframe()
    if not df.empty:
        st.subheader("📅 Expiry Calendar")
        chart = alt.Chart(df).mark_bar().encode(
            x='expiry_date:T',
            y=alt.Y('name:N', sort='-x'),
            color=alt.condition(df['high_priority'], alt.value("crimson"), alt.value("steelblue")),
            tooltip=['name', 'expiry_date', 'quantity']
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)

elif page == "Chat Recipe Bot":
    st.header("🤖 Smart AI Recipe Chat")
    interactive_chat_loop()