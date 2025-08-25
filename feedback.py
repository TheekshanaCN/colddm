import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# ---- Google Sheets Setup ----
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1AvDYFrPQ65RYobb0Ldt5KqZboSFeoy1JMkJdRzkmk18"
SHEET_NAME = "sheet"

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
client = gspread.authorize(creds)

sh = client.open_by_key(SPREADSHEET_ID)
try:
    sheet = sh.worksheet(SHEET_NAME)
except gspread.exceptions.WorksheetNotFound:
    sheet = sh.add_worksheet(title=SHEET_NAME, rows="100", cols="20")

# ---- Add headers if sheet is empty ----
if len(sheet.get_all_values()) == 0:
    sheet.append_row(
        ["Timestamp", "Feedback", "Rating", "Rating Meaning"], 
        value_input_option="RAW"
    )

# ---- Streamlit UI ----
st.title("💬 Feedback Form (MVP Test)")

# ---- Predefined Feedback Options ----
predefined_feedbacks = [
    "This SaaS idea is really useful!",
    "Not sure if I would use this.",
    "Needs more features before I can recommend.",
    "Love the concept, easy to understand!",
    "Not helpful for my current workflow."
]

selected_feedback = st.radio(
    "Choose a feedback or type your own below:",
    options=predefined_feedbacks
)

custom_feedback = st.text_area("Or write your own feedback here:")

feedback_text = custom_feedback.strip() if custom_feedback.strip() else selected_feedback

# ---- Clickable Rating Buttons ----
st.write("Rate this MVP:")
col1, col2, col3, col4, col5 = st.columns(5)

rating_labels = {
    1: "❌ Bad",
    2: "⚠️ Needs Improvement",
    3: "👍 Okay",
    4: "🌟 Good",
    5: "🔥 Excellent"
}

rating = 3  # default

if col1.button("⭐ 1"):
    rating = 1
if col2.button("⭐ 2"):
    rating = 2
if col3.button("⭐ 3"):
    rating = 3
if col4.button("⭐ 4"):
    rating = 4
if col5.button("⭐ 5"):
    rating = 5

st.write(f"Your rating: {rating_labels[rating]} {'⭐' * rating}")

# ---- Submit Feedback ----
if st.button("Submit Feedback"):
    if feedback_text:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, feedback_text, rating, rating_labels[rating]], value_input_option="RAW")
        st.success("✅ Feedback submitted successfully!")
    else:
        st.warning("⚠️ Please provide feedback before submitting.")
