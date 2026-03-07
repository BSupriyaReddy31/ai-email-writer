import streamlit as st
import google.generativeai as genai
import sqlite3
import os
from dotenv import load_dotenv

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Email Pro", page_icon="✉️", layout="wide")

# --- CUSTOM CSS ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
    html, body, [class*="css"], h1, h2, h3, .stApp label, .stTabs [data-baseweb="tab"], .stButton>button {
        font-family: 'Outfit', sans-serif !important;
    }
    .stApp {
        background-color: #1a0b2e;
        background-image: radial-gradient(#4d298c 1.5px, transparent 1.5px);
        background-size: 25px 25px;
        color: #ffffff !important; 
    }
    #title-container { text-align: center; padding-bottom: 20px; margin-top: 10px; }
    #title-container h1 {
        font-size: 3.5rem; font-weight: 900;
        background: linear-gradient(90deg, #00f0ff, #ff007f);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 10px rgba(255, 0, 127, 0.4));
    }
    .glowing-card {
        background-color: rgba(36, 15, 77, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 12px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    #details-card { border: 1px solid #00f0ff; }
    #draft-card { border: 1px solid #ff007f; }
    .stTextInput label, .stSelectbox label, .stTextArea label, .stApp p {
        color: #00f0ff !important;
    }
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(17, 5, 36, 0.9) !important;
        color: #00f0ff !important;
        border: 1px solid #4d298c !important;
    }
    .stButton>button {
        background-image: linear-gradient(90deg, #00f0ff, #0051ff);
        color: #ffffff !important; border: none; border-radius: 8px;
        font-weight: 700; width: 100%; padding: 8px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- SETUP & CONFIGURATION ---
load_dotenv()
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 API Key not found!")
else:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('email_database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS email_history (id INTEGER PRIMARY KEY AUTOINCREMENT, recipient TEXT, tone TEXT, draft TEXT)')
    conn.commit()
    conn.close()

def save_to_db(recipient, tone, draft):
    conn = sqlite3.connect('email_database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO email_history (recipient, tone, draft) VALUES (?, ?, ?)", (recipient, tone, draft))
    conn.commit()
    conn.close()

def fetch_history_from_db():
    conn = sqlite3.connect('email_database.db')
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT recipient, tone, draft FROM email_history ORDER BY id DESC")
    records = cursor.fetchall()
    conn.close()
    return records

init_db()

# --- AI LOGIC ---
def generate_email(recipient, context, tone, key_points):
    prompt = f"Write a {tone} follow-up email to {recipient} regarding {context}. Include: {key_points}. Output only the email."
    response = model.generate_content(prompt)
    return response.text

# --- UI ---
st.markdown("<div id='title-container'><h1>AI Follow-Up Writer</h1><p>Generate emails instantly.</p></div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✨ Create New Draft", "🗄️ Database History"])

with tab1:
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("<div class='glowing-card' id='details-card'><h2>Email Details</h2>", unsafe_allow_html=True)
        recipient = st.text_input("Recipient's Name")
        tone = st.selectbox("Tone", ["Professional", "Casual", "Urgent"])
        context = st.text_area("What was the meeting about?", height=120)
        key_points = st.text_area("Key points to include", height=120)
        generate_btn = st.button("Generate Email Draft")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glowing-card' id='draft-card'><h2>Your Generated Draft</h2>", unsafe_allow_html=True)
        if generate_btn:
            if not recipient or not context:
                st.warning("⚠️ Fill out name and context.")
            else:
                try:
                    st.info("🔄 Step 1: Contacting AI...")
                    draft = generate_email(recipient, context, tone, key_points)
                    st.success("✅ Step 2: AI Success!")
                    
                    st.info("🔄 Step 3: Saving to DB...")
                    save_to_db(recipient, tone, draft)
                    st.success("✅ Step 4: Database Success!")
                    
                    st.text_area("Review and Copy:", value=draft, height=400, key="main_result")
                except Exception as e:
                    st.error(f"🚨 ERROR: {str(e)}")
        else:
            st.text_area("Review and Copy:", value="Your generated email will appear here...", height=400, disabled=True, key="placeholder")
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='glowing-card'><h2>History</h2>", unsafe_allow_html=True)
    for record in fetch_history_from_db():
        with st.expander(f"✉️ {record['recipient']}"):
            st.write(record['draft'])
    st.markdown("</div>", unsafe_allow_html=True)
