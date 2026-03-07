import streamlit as st
import google.generativeai as genai
import sqlite3
import os
from dotenv import load_dotenv

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Email Pro", page_icon="✉️", layout="wide")

# --- CUSTOM CSS FOR A PREMIUM LIGHT THEME ---
custom_css = """
<style>
    /* Import a sleek, modern web font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* Apply the new font to everything */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* 1. MAIN APP BACKGROUND - Clean off-white */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* 2. SIDEBAR - Pure white with a subtle border */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Center the title and give it a premium blue-to-purple gradient */
    h1 {
        text-align: center;
        font-weight: 800;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* Clean up the input boxes */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Blue focus ring when typing */
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
    }
    
    /* Modern, solid blue button */
    .stButton>button {
        background-color: #2563eb;
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #1d4ed8;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- SETUP & CONFIGURATION ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# --- SQLITE DATABASE FUNCTIONS ---
# (Keep your init_db, save_to_db, and fetch_history_from_db functions exactly the same here)
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
# (Keep your generate_email function exactly the same here)
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

# We use HTML here to perfectly center the headers
st.markdown("""
    <div style='text-align: center; padding-bottom: 20px;'>
        <h1>✉️ AI Follow-Up Writer</h1>
        <p style='color: #64748b; font-size: 1.1rem; margin-top: -10px;'>Generate professional, context-aware follow-up emails instantly.</p>
    </div>
    <hr style='border: 1px solid #e2e8f0; margin-bottom: 30px;'>
""", unsafe_allow_html=True)

# Main Layout with Tabs
tab1, tab2 = st.tabs(["✨ Create New Draft", "🗄️ Database History"])

# (Keep the rest of your tab1, tab2, and sidebar code exactly the same below this!)
# Main Layout with Tabs


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
