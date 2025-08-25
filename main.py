import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import datetime

# ---- Google Sheets Setup ----
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = (
    "1AvDYFrPQ65RYobb0Ldt5KqZboSFeoy1JMkJdRzkmk18"  # Replace with your Google Sheet ID
)
SHEET_NAME = "sheet"  # Tab name in your sheet

# ---- Load credentials from environment variable ----
# Set this in your system / Streamlit Cloud secrets as: GOOGLE_CREDS
service_account_info = json.loads(os.environ.get("GOOGLE_CREDS"))
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)
client = gspread.authorize(creds)

# Open sheet
try:
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
except gspread.exceptions.WorksheetNotFound:
    # Create worksheet if it doesn't exist
    sh = client.open_by_key(SPREADSHEET_ID)
    sheet = sh.add_worksheet(title=SHEET_NAME, rows="100", cols="20")

# Add headers if sheet is empty
if len(sheet.get_all_values()) == 0:
    sheet.append_row(
        ["Timestamp", "Feedback", "Rating", "Rating Meaning"], value_input_option="RAW"
    )

# ---- Configuration ----
st.set_page_config(
    page_title="LinkedIn Cold DM Generator", page_icon="📧", layout="centered"
)


# ---- Custom CSS ----
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #0077B5, #00A0DC);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 30px;
    }
    .dm-box {
        background: #0f0f0f;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }
    .dm-title {
        color: #0077B5;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .rating-btn {
        width: 100%;
        margin-bottom: 5px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---- Header ----
st.markdown(
    """
<div class="main-header">
    <h1>📧 LinkedIn Cold DM Generator</h1>
    <p>Generate personalized cold DMs from LinkedIn profiles</p>
</div>
""",
    unsafe_allow_html=True,
)


# ---- API Key Input ----
api_key = st.text_input(
    "🔑 Gemini API Key", type="password", help="Enter your Google Gemini API key"
)

if api_key:
    genai.configure(api_key=api_key)
    st.success("✅ API Key configured!")

# ---- Main Form ----
with st.form("dm_generator"):
    col1, col2 = st.columns(2)

    with col1:
        about_section = st.text_area(
            "LinkedIn About Section*",
            height=120,
            placeholder="Paste their LinkedIn About section...",
        )

        headline = st.text_input(
            "Job Title/Headline*",
            placeholder="e.g., Senior Marketing Manager at Tech Corp",
        )

    with col2:
        company = st.text_input("Company Name*", placeholder="e.g., Microsoft")

        tone = st.selectbox(
            "Tone Style",
            ["Professional", "Friendly", "Consultative", "Direct", "Value-First"],
        )

        objective = st.selectbox(
            "Main Goal",
            [
                "Schedule a call",
                "Book a demo",
                "Share insights",
                "Network",
                "Partnership",
            ],
        )

    # Your details
    st.subheader("Your Information")
    col3, col4 = st.columns(2)

    with col3:
        your_name = st.text_input("Your Name", placeholder="John Smith")
        your_company = st.text_input("Your Company", placeholder="ABC Solutions")

    with col4:
        your_role = st.text_input("Your Role", placeholder="Sales Director")
        num_dms = st.slider("Number of DMs", 1, 5, 3)

    generate_btn = st.form_submit_button(
        "🚀 Generate Cold DMs", use_container_width=True
    )

# ---- Generate DMs ----
if generate_btn:
    if not all([about_section, headline, company, api_key]):
        st.error("❌ Please fill in all required fields and API key")
    else:
        with st.spinner("🤖 Creating personalized DMs..."):
            try:
                prompt = f"""
Create {num_dms} personalized LinkedIn cold DMs based on this profile:

PROFILE:
About: {about_section}
Role: {headline}  
Company: {company}

SENDER:
Name: {your_name or "Your Name"}
Company: {your_company or "Your Company"}
Role: {your_role or "Your Role"}

REQUIREMENTS:
- Tone: {tone}
- Goal: {objective}
- Length: 50-80 words each (keep them short, punchy, and scannable)
- Highly personalized using details from their profile
- Natural, conversational, and friendly
- Start with a hook that highlights something impressive about them
- Include one curiosity-driven question to encourage reply
- Avoid overexplaining, marketing fluff, or long paragraphs

Format each DM exactly as:
**DM #1:**
[message content]

**DM #2:**
[message content]

---

Only provide the DMs, no summaries, analyses, or extra text. Keep it ready-to-copy.

"""

                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)

                st.success("✅ DMs Generated!")

                # Display DMs in clean boxes
                dms_content = response.text

                # Split DMs if they're numbered
                if "**DM #" in dms_content:
                    dm_parts = dms_content.split("**DM #")[1:]
                    for i, dm_part in enumerate(dm_parts, 1):
                        dm_text = (
                            dm_part.split(":**", 1)[1].strip()
                            if ":**" in dm_part
                            else dm_part.strip()
                        )
                        dm_text = dm_text.replace("---", "").strip()

                        st.markdown(
                            f"""
                        <div class="dm-box">
                            <div class="dm-title">DM #{i}</div>
                            {dm_text}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                else:
                    # If not numbered, show as one block
                    st.markdown(
                        f"""
                    <div class="dm-box">
                        <div class="dm-title">Generated DMs</div>
                        {dms_content}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                # Copy section
                st.subheader("📋 Copy DMs")
                st.text_area("All DMs (Copy & Paste)", dms_content, height=200)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("Make sure your API key is valid")

# ---- Footer Tips ----
with st.expander("💡 Quick Tips"):
    st.markdown(
        """
    **For Better DMs:**
    - Use specific details from their About section
    - Mention their company or recent achievements  
    - Keep it personal but professional
    - Focus on value, not selling
    """
    )

# ---- Enhanced Feedback Section ----
st.markdown("---")
st.subheader("💬 Give Feedback")

# Predefined Feedback Options
predefined_feedbacks = [
    "This tool is really useful!",
    "Not sure if I would use this regularly.",
    "Needs more features before I can recommend.",
    "Love the concept, easy to understand!",
    "Not helpful for my current workflow.",
]

selected_feedback = st.radio(
    "Choose a feedback or type your own below:", options=predefined_feedbacks
)

custom_feedback = st.text_area("Or write your own feedback here:", height=100)

feedback_text = (
    custom_feedback.strip() if custom_feedback.strip() else selected_feedback
)

# Clickable Rating Buttons
st.write("Rate this tool:")
col1, col2, col3, col4, col5 = st.columns(5)

rating_labels = {
    1: "❌ Bad",
    2: "⚠️ Needs Improvement",
    3: "👍 Okay",
    4: "🌟 Good",
    5: "🔥 Excellent",
}

rating = 3  # default

if col1.button("⭐ 1", use_container_width=True):
    rating = 1
if col2.button("⭐ 2", use_container_width=True):
    rating = 2
if col3.button("⭐ 3", use_container_width=True):
    rating = 3
if col4.button("⭐ 4", use_container_width=True):
    rating = 4
if col5.button("⭐ 5", use_container_width=True):
    rating = 5

st.write(f"Your rating: {rating_labels[rating]} {'⭐' * rating}")

# Submit Feedback
if st.button("Submit Feedback"):
    if feedback_text:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row(
            [timestamp, feedback_text, rating, rating_labels[rating]],
            value_input_option="RAW",
        )
        st.success("✅ Feedback submitted successfully!")
    else:
        st.warning("⚠️ Please provide feedback before submitting.")
