🥫 Smart Pantry & Recipe Assistant

An intelligent food management app that helps you reduce waste, plan meals, and get personalized AI-powered recipe suggestions — all from your pantry and grocery receipts.

🌐 **Live App**: [CookMate AI on Streamlit](https://cookmate-ai.streamlit.app/)

🌟 Features

✅ **OCR Receipt Scanning** – Upload images of grocery receipts to auto-extract items using EasyOCR and Gemini AI.

✅ **Expiry Estimation** – Get suggested expiry dates using USDA guidelines and AI for unknown items.

✅ **Editable Pantry** – Add, edit, or delete pantry items manually or from receipts.

✅ **Smart Suggestions** – Get recipe ideas tailored to your ingredients, cuisine preferences, allergies, and dietary needs.

✅ **AI Recipe Chatbot** – Chat with a Gemini-powered assistant that understands your pantry, filters, and offers alternatives.

✅ **Download & Export** – Export your pantry or recipe, download missing ingredients as a shopping list.

✅ **Auto Inventory Update** – Automatically remove used items from your pantry after cooking.

🔧 How to Run Locally

1. **Clone this repo**
```bash
git clone https://github.com/YOUR_USERNAME/smart-pantry-assistant.git
cd smart-pantry-assistant
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up secrets**
Create a file `.streamlit/secrets.toml` with your Gemini API key:
```toml
GEMINI_API_KEY = "your_google_gemini_api_key"
```

4. **Run the app**
```bash
streamlit run app.py
```

🧠 Tech Stack
- Python
- Streamlit
- EasyOCR
- Google Gemini API
- USDA Guidelines for expiry estimation

## 🙋‍♀️ Author
Built by [Huda Bhayani] – open to collaborations and improvements!

## 📄 License
MIT