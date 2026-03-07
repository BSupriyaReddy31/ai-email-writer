import streamlit as st
import google.generativeai as genai
import sqlite3
import os
from dotenv import load_dotenv

# --- PAGE CONFIGURATION ---
# This must be the first Streamlit command
st.set_page_config(page_title="AI Email Pro", page_icon="✉️", layout="wide")

# --- CUSTOM CSS FOR A DEVELOPER DARK THEME ---
custom_css = """
<style>
    /* 1. MAIN APP BACKGROUND - Deep Slate (Dark Mode) */
    .stApp {
        background-color: #0f172a; 
    }

    /* 2. SIDEBAR - Slightly lighter slate for contrast */
    [data-testid="stSidebar"] {
        background-color: #1e293b; 
        border-right: 1px solid #334155;
    }

    /* 3. Global Text Color - Force text to be white/light gray so it's readable */
    .stApp, .stApp p, .stApp label, .stApp h2, .stApp h3, .stApp span {
        color: #f8fafc !important;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Create a striking neon-blue gradient title */
    h1 {
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
    }
    
    /* Style the input areas for dark mode */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
    }
    
    /* Focus glowing effect for inputs */
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 8px rgba(56, 189, 248, 0.4) !important;
    }
    
    /* High-tech primary button */
    .stButton>button {
        background-image: linear-gradient(to right, #38bdf8, #818cf8);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.4);
    }
    
    /* Tabs styling for dark mode */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- SETUP & CONFIGURATION ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# --- SQLITE DATABASE FUNCTIONS ---
def init_db():
    conn = sqlite3.connect('email_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT,
            tone TEXT,
            draft TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(recipient, tone, draft):
    conn = sqlite3.connect('email_database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO email_history (recipient, tone, draft) VALUES (?, ?, ?)", 
                   (recipient, tone, draft))
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
    system_prompt = f"""
    You are an expert executive assistant. Write a professional follow-up email.
    Recipient Name: {recipient}
    Context/Meeting Topic: {context}
    Desired Tone: {tone}
    Key Points to Include: {key_points}
    
    Output ONLY the email subject line and body. Do not include placeholders like [Your Name].
    """
    try:
        response = model.generate_content(system_prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

# --- STREAMLIT UI ---

# Header Section
st.title("✉️ AI Follow-Up Writer")
st.caption("Generate professional, context-aware follow-up emails instantly. Powered by Google Gemini.")
st.divider()

# Main Layout with Tabs
tab1, tab2 = st.tabs(["✨ Create New Draft", "🗄️ Database History"])

with tab1:
    # Use columns to split the input form and the output area
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.subheader("Email Details")
        st.info("Provide the context of your meeting to generate a highly tailored response.")
        
        recipient = st.text_input("Recipient's Name", placeholder="e.g., Jane Doe")
        tone = st.selectbox("Tone", ["Professional", "Friendly & Casual", "Urgent", "Appreciative"])
        context = st.text_area("What was the meeting about?", placeholder="e.g., Discussed the new frontend architecture...", height=120)
        key_points = st.text_area("Key points to include", placeholder="e.g., Attached my portfolio, excited for next steps...", height=120)
        
        st.write("") # Spacer
        generate_btn = st.button("Generate Email Draft", type="primary")

    with col2:
        st.subheader("Your Generated Draft")
        
        if generate_btn:
            if not recipient or not context:
                st.warning("⚠️ Please fill out the recipient name and meeting context.")
            else:
                with st.spinner("🧠 AI is crafting your email..."):
                    draft = generate_email(recipient, context, tone, key_points)
                    save_to_db(recipient, tone, draft)
                    
                    st.success("✅ Email generated and saved successfully!")
                    st.text_area("Review and Copy:", value=draft, height=400, label_visibility="collapsed")
        else:
            # Placeholder when nothing is generated yet
            st.text_area("Review and Copy:", value="Your generated email will appear here...", height=400, disabled=True, label_visibility="collapsed")

with tab2:
    st.subheader("Your Permanent Session History")
    st.caption("All previously generated emails are securely stored in your local SQLite database.")
    
    db_history = fetch_history_from_db()
    
    if not db_history:
        st.info("No emails found in the database. Head over to the 'Create New Draft' tab to generate one!")
    else:
        for i, record in enumerate(db_history):
            with st.expander(f"✉️ To: {record['recipient']} | 🎭 Tone: {record['tone']}"):
                st.text_area(label="Draft", value=record['draft'], height=250, key=f"db_hist_{i}", label_visibility="collapsed")