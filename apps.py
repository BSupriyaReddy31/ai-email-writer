import streamlit as st
import google.generativeai as genai
import sqlite3
import os
from dotenv import load_dotenv

# --- PAGE CONFIGURATION (must be first) ---
st.set_page_config(page_title="AI Email Pro", page_icon="✉️", layout="wide")

# --- CUSTOM CSS FOR THE VISILY PASTEL THEME ---
custom_css = """
<style>
    /* Import Clean Modern SaaS Font (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], h1, h2, h3, .stApp label, .stTabs [data-baseweb="tab"], .stButton>button {
        font-family: 'Inter', sans-serif !important;
    }

    /* 1. MAIN APP BACKGROUND - Soft Lilac / Pastel Purple */
    .stApp {
        background-color: #debafe; /* Exact match from the image */
        color: #261c2c !important; 
    }

    /* 2. SIDEBAR - Clean White */
    [data-testid="stSidebar"] {
        background-color: #ffffff; 
        border-right: 1px solid #c8a3e8;
    }

    /* 3. CENTERED TITLE - Dark Text */
    #title-container {
        text-align: center;
        padding-bottom: 20px;
        margin-top: 10px;
    }

    #title-container h1 {
        font-size: 3.5rem;
        font-weight: 700;
        color: #30153e; /* Deep Violet */
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }
    
    #title-container p {
        color: #4a3b52;
        font-size: 1.1rem;
        margin-top: 0;
        font-weight: 400;
    }

    /* Hide standard streamlit things */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 4. CARDS - Clean SaaS Style */
    .glowing-card {
        border-radius: 12px;
        padding: 25px; 
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(48, 21, 62, 0.08);
        transition: transform 0.2s ease;
    }
    
    /* White card (for Details) */
    #details-card {
        background-color: #ffffff;
        border: 1px solid #f0e6fc;
    }

    /* Deep Violet card (for Draft) - Matches the dark banner in your image */
    #draft-card {
        background-color: #30153e; /* Exact match from the banner */
        border: none;
    }
    
    /* Subtitles within cards */
    #details-card h2 {
        font-size: 1.6rem;
        color: #30153e !important;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    #draft-card h2 {
        font-size: 1.6rem;
        color: #fcfaff !important; /* Off-white for contrast */
        margin-bottom: 1rem;
        font-weight: 700;
    }

    /* 5. FIX TEXT VISIBILITY */
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #4a3b52 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }

    /* Fix the st.info box */
    [data-testid="stNotification"] {
        background-color: #fcfaff !important;
        border-left: 4px solid #592eff !important;
    }
    [data-testid="stNotification"] p {
        color: #4a3b52 !important;
    }

    /* 6. INPUT BOXES & SELECTORS - Clean White */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #261c2c !important; 
        border-radius: 8px !important;
        border: 1px solid #d3bcf2 !important;
    }
    
    /* Input box style specifically for the Dark Draft side */
    #draft-card .stTextArea textarea {
        background-color: #432257 !important;
        color: #ffffff !important;
        border: 1px solid #5d3578 !important;
    }
    
    /* Focus Ring */
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #592eff !important;
        box-shadow: 0 0 0 2px rgba(89, 46, 255, 0.2) !important;
    }

    /* 7. VISILY BLUE BUTTON */
    .stButton>button {
        background-color: #592eff; /* Exact match from the Visily button */
        color: #ffffff !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1rem;
        width: 100%;
        padding: 8px;
        margin-top: 10px;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #4620d4;
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(89, 46, 255, 0.3);
    }
    
    /* 8. REFINING TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
        border-bottom: 1px solid #c8a3e8;
        padding-bottom: 0;
        margin-bottom: 25px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #4a3b52 !important;
        padding: 10px 10px;
        background-color: transparent;
        border: none;
    }
    /* Active Tab */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #592eff !important;
        border-bottom: 3px solid #592eff;
        font-weight: 600;
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

# --- UPDATED STRUCTURAL LAYOUT ---

# 1. CENTERED HEADER SECTION (Decorative rings removed!)
st.markdown("""
    <div id='title-container'>
        <h1>AI Follow-Up Writer</h1>
        <p>Generate context-aware follow-up emails instantly. Powered by AI.</p>
    </div>
""", unsafe_allow_html=True)

# 2. MAIN INTERFACE ROW
tab1, tab2 = st.tabs(["✨ Create New Draft", "🗄️ Database History"])

with tab1:
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("<div class='glowing-card' id='details-card'><h2>Email Details</h2>", unsafe_allow_html=True)
        st.info("Provide the context of your meeting to generate a highly tailored response.")
        
        recipient = st.text_input("Recipient's Name", placeholder="e.g., Jane Doe")
        tone = st.selectbox("Tone", ["Professional", "Friendly & Casual", "Urgent", "Appreciative"])
        context = st.text_area("What was the meeting about?", placeholder="e.g., Discussed the new frontend architecture...", height=120)
        key_points = st.text_area("Key points to include", placeholder="e.g., Attached my portfolio, excited for next steps...", height=120)
        
        generate_btn = st.button("Generate Email Draft", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glowing-card' id='draft-card'><h2>Your Generated Draft</h2>", unsafe_allow_html=True)
        
        if generate_btn:
            if not recipient or not context:
                st.warning("⚠️ Please fill out the recipient name and meeting context.")
            else:
                with st.spinner("🧠 AI is crafting your email..."):
                    draft = generate_email(recipient, context, tone, key_points)
                    save_to_db(recipient, tone, draft)
                    
                    st.success("✅ Email generated and saved successfully!")
                    st.text_area("Review and Copy:", value=draft, height=450, label_visibility="collapsed")
        else:
            st.text_area("Review and Copy:", value="Your generated email will appear here...", height=450, disabled=True, label_visibility="collapsed")
        
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='glowing-card' style='border: 1px solid #4d298c;'><h2>Your Permanent History</h2>", unsafe_allow_html=True)
    st.caption("All previously generated emails are securely stored in your local SQLite database.")
    
    db_history = fetch_history_from_db()
    
    if not db_history:
        st.info("No emails found in the database. Head over to the 'Create New Draft' tab to generate one!")
    else:
        for i, record in enumerate(db_history):
            with st.expander(f"✉️ To: {record['recipient']} | 🎭 Tone: {record['tone']}"):
                st.text_area(label="Draft", value=record['draft'], height=250, key=f"db_hist_{i}", label_visibility="collapsed")
    
    st.markdown("</div>", unsafe_allow_html=True)







