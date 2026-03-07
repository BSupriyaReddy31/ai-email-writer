import streamlit as st
import google.generativeai as genai
import sqlite3
import os
from dotenv import load_dotenv

# --- PAGE CONFIGURATION (must be first) ---
st.set_page_config(page_title="AI Email Pro", page_icon="✉️", layout="wide")

# --- CUSTOM CSS FOR THE NEON PURPLE/CYAN THEME ---
custom_css = """
<style>
    /* Import Modern Tech Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
    
    /* Apply futuristic font to heading elements */
    html, body, [class*="css"], h1, h2, h3, .stApp label, .stTabs [data-baseweb="tab"], .stButton>button {
        font-family: 'Outfit', sans-serif !important;
    }

    /* 1. MAIN APP BACKGROUND - Deep Violet with Dotted Pattern */
    .stApp {
        background-color: #1a0b2e;
        background-image: radial-gradient(#4d298c 1.5px, transparent 1.5px);
        background-size: 25px 25px;
        color: #ffffff !important; 
    }

    /* 2. SIDEBAR - Darker Purple with Neon Cyan Border */
    [data-testid="stSidebar"] {
        background-color: #110524; 
        border-right: 2px solid #00f0ff;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
    }

    /* 3. CENTERED TITLE & SUBTITLE with Cyan/Pink Glow */
    #title-container {
        text-align: center;
        padding-bottom: 30px;
        margin-top: 20px;
    }

    #title-container h1 {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f0ff, #ff007f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: 1px;
        filter: drop-shadow(0 0 10px rgba(255, 0, 127, 0.4));
    }
    
    #title-container p {
        color: #bfa6e8;
        font-size: 1.2rem;
        margin-top: 0;
        font-weight: 300;
    }

    /* Hide standard streamlit things */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 4. GLOWING CARDS FOR MAIN PANELS - Translucent Purple */
    .glowing-card {
        background-color: rgba(36, 15, 77, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    /* Cyan glow card (for Details) */
    #details-card {
        border: 1px solid #00f0ff;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
    }
    #details-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.3);
    }

    /* Pink glow card (for Draft) */
    #draft-card {
        border: 1px solid #ff007f;
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.15);
    }
    #draft-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 25px rgba(255, 0, 127, 0.3);
    }
    
    /* Subtitles within cards */
    .glowing-card h2 {
        font-size: 1.8rem;
        color: #ffffff !important;
        margin-bottom: 1.5rem;
        font-weight: 700;
    }

    /* 5. INPUT BOXES & SELECTORS - Deep dark interior */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(17, 5, 36, 0.9) !important;
        color: #00f0ff !important; /* Cyan text when typing */
        border-radius: 8px !important;
        border: 1px solid #4d298c !important;
    }
    
    /* Glowing Focus Ring */
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 0 2px rgba(0, 240, 255, 0.3) !important;
    }

    /* 6. NEON GRADIENT BUTTON */
    .stButton>button {
        background-image: linear-gradient(90deg, #00f0ff, #0051ff);
        color: #ffffff !important;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.1rem;
        width: 100%;
        padding: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 240, 255, 0.4);
    }
    
    .stButton>button:hover {
        background-image: linear-gradient(90deg, #0051ff, #00f0ff);
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 240, 255, 0.6);
    }
    
    /* 7. REFINING TABS FOR NEON MODE */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: rgba(36, 15, 77, 0.6);
        border-radius: 12px;
        padding: 5px;
        margin-bottom: 25px;
        border: 1px solid #4d298c;
    }
    .stTabs [data-baseweb="tab"] {
        color: #bfa6e8 !important;
        padding: 10px 20px;
    }
    /* Active Tab */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #00f0ff !important;
        border-bottom: 3px solid #00f0ff;
        background-color: rgba(0, 240, 255, 0.1);
        border-radius: 8px 8px 0 0;
    }

    /* Styling the decorative rings */
    .deco-card {
        background-color: rgba(36, 15, 77, 0.85);
        border-radius: 16px;
        border: 1px solid #4d298c;
        padding: 15px;
        text-align: center;
        height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .deco-value {
        font-size: 2.2rem;
        font-weight: 900;
        margin-bottom: -5px;
        color: #ffffff;
    }
    .deco-label {
        font-size: 0.85rem;
        color: #bfa6e8;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    .deco-ring {
        height: 80px; width: 80px; margin: 0 auto;
        border-radius: 50%;
        border: 8px solid #2a115c;
        position: relative;
    }
    
    #ring-context {
        color: #00f0ff;
        border-top-color: #00f0ff;
        border-right-color: #00f0ff;
        filter: drop-shadow(0 0 8px rgba(0, 240, 255, 0.5));
    }
    #ring-confidence {
        color: #ff007f;
        border-top-color: #ff007f;
        filter: drop-shadow(0 0 8px rgba(255, 0, 127, 0.5));
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

# 1. CENTERED HEADER SECTION
st.markdown("""
    <div id='title-container'>
        <h1>AI Follow-Up Writer</h1>
        <p>Generate context-aware follow-up emails instantly. Powered by AI.</p>
    </div>
""", unsafe_allow_html=True)

# 2. TOP DECORATIVE ROW (Neon Vibe)
st.markdown("""
    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px;'>
        <div class='deco-card' style='position: relative;'>
            <div class='deco-ring' id='ring-context'>
                <div class='deco-value' style='position: absolute; top: 18px; left: 15px;'>95%</div>
            </div>
            <div class='deco-label'>Model Context Accuracy</div>
        </div>
        <div class='deco-card' style='position: relative;'>
            <div class='deco-ring' id='ring-confidence'>
                <div class='deco-value' style='position: absolute; top: 18px; left: 15px;'>75%</div>
            </div>
            <div class='deco-label'>Draft Confidence</div>
        </div>
        <div class='deco-card'>
            <div class='deco-value' style='color: #00f0ff;'>UI/UX</div>
            <div class='deco-label'>Optimized Interface</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 3. MAIN INTERFACE ROW
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
        
        st.write("") 
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
                    st.text_area("Review and Copy:", value=draft, height=480, label_visibility="collapsed")
        else:
            st.text_area("Review and Copy:", value="Your generated email will appear here...", height=480, disabled=True, label_visibility="collapsed")
        
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
