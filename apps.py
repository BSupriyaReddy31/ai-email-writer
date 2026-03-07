import streamlit as st
import google.generativeai as genai
import sqlite3
import os
from dotenv import load_dotenv

# --- PAGE CONFIGURATION (must be first) ---
st.set_page_config(page_title="AI Email Pro", page_icon="✉️", layout="wide")

# --- CUSTOM CSS FOR THE FULL image_3.png DESIGN ---
# This block overwrites Streamlit's default look and structure.
custom_css = """
<style>
    /* Import Futuristic/Tech Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap');
    
    /* Apply futuristic font to heading elements */
    h1, h2, h3, .stApp label, .stTabs [data-baseweb="tab"], .stButton>button {
        font-family: 'Chakra Petch', sans-serif !important;
    }

    /* 1. MAIN APP BACKGROUND - Deep Dark Cosmic Blue with texture */
    .stApp {
        background-color: #0a0f1e;
        background-image: radial-gradient(#1e293b 1.5px, transparent 1.5px);
        background-size: 30px 30px;
        color: #f8fafc !important; /* Ensure all text is light */
    }

    /* 2. SIDEBAR - Dark Slate Grey with Glowing Border */
    [data-testid="stSidebar"] {
        background-color: #111827; 
        border-right: 2px solid #334155;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }

    /* 3. CENTERED TITLE & SUBTITLE with Glowing Effect */
    #title-container {
        text-align: center;
        padding-bottom: 30px;
    }

    #title-container h1 {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #38bdf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        /* Glowing Outline Effect */
        -webkit-text-stroke: 1px #818cf8;
        filter: drop-shadow(0 0 8px rgba(129, 140, 248, 0.6));
    }
    
    #title-container p {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-top: 0;
    }

    /* Hide standard streamlit things */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 4. GLOWING CARDS FOR MAIN PANELS */
    .glowing-card {
        background-color: #1f2937;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        transition: transform 0.3s ease;
    }
    
    /* Cyan glow card (for Details) */
    #details-card {
        border: 2px solid #38bdf8;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }
    #details-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.5);
    }

    /* Purple glow card (for Draft) */
    #draft-card {
        border: 2px solid #c084fc;
        box-shadow: 0 0 10px rgba(192, 132, 252, 0.3);
    }
    #draft-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(192, 132, 252, 0.5);
    }
    
    /* Subtitles within cards */
    .glowing-card h2 {
        font-size: 1.8rem;
        color: #f8fafc !important;
        margin-bottom: 1.5rem;
    }

    /* 5. INPUT BOXES & SELECTORS IN DARK MODE */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #111827 !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Glowing Focus Ring */
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.3) !important;
    }

    /* 6. GLOWING RED BUTTON WITH MODERN GRADIENT */
    .stButton>button {
        background-image: linear-gradient(135deg, #ef4444, #f87171);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        width: 100%;
        transition: all 0.3s ease;
        filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.4));
    }
    
    .stButton>button:hover {
        background-image: linear-gradient(135deg, #f87171, #ef4444);
        transform: scale(1.02);
        filter: drop-shadow(0 0 20px rgba(239, 68, 68, 0.7));
    }
    
    /* 7. REFINING TABS FOR DARK MODE */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: #111827;
        border-radius: 8px;
        padding: 5px;
        margin-bottom: 25px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #cbd5e1 !important;
        padding: 10px 15px;
    }
    /* Active Tab */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom: 3px solid #38bdf8;
        filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.3));
    }

    /* Styling the decorative rings (using dummy containers) */
    .deco-card {
        background-color: #111827;
        border-radius: 12px;
        border: 1px solid #334155;
        padding: 15px;
        text-align: center;
        height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .deco-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: -5px;
    }
    .deco-label {
        font-size: 0.8rem;
        color: #94a3b8;
    }
    .deco-ring {
        height: 80px; width: 80px; margin: 0 auto;
        border-radius: 50%;
        border: 8px solid #334155;
        position: relative;
    }
    
    #ring-context {
        color: #38bdf8;
        border-top-color: #38bdf8;
        border-right-color: #38bdf8;
        filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.5));
    }
    #ring-confidence {
        color: #c084fc;
        border-top-color: #c084fc;
        filter: drop-shadow(0 0 8px rgba(192, 132, 252, 0.5));
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

# 1. CENTERED HEADER SECTION (Locked dead-center with custom HTML)
st.markdown("""
    <div id='title-container'>
        <h1>✉️ AI Follow-Up Writer</h1>
        <p>Generate professional, context-aware follow-up emails instantly. Powered by Google Gemini.</p>
    </div>
    <hr style='border: 1px solid #334155; margin-bottom: 40px;'>
""", unsafe_allow_html=True)

# 2. TOP DECORATIVE ROW (To mimic the image, using dummy containers for styling)
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
            <div class='deco-value'>22%</div>
            <div class='deco-label'>Pothole Apps Mentioned</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 3. MAIN INTERFACE ROW
# Content is wrapped in columns and glowing cards.
tab1, tab2 = st.tabs(["✨ Create New Draft", "🗄️ Database History"])

with tab1:
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        # Wrapping elements to apply card CSS and glowing ID
        st.markdown("<div class='glowing-card' id='details-card'><h2>Email Details</h2>", unsafe_allow_html=True)
        st.info("Provide the context of your meeting to generate a highly tailored response.")
        
        recipient = st.text_input("Recipient's Name", placeholder="e.g., Jane Doe")
        tone = st.selectbox("Tone", ["Professional", "Friendly & Casual", "Urgent", "Appreciative"])
        context = st.text_area("What was the meeting about?", placeholder="e.g., Discussed the new frontend architecture...", height=120)
        key_points = st.text_area("Key points to include", placeholder="e.g., Attached my portfolio, excited for next steps...", height=120)
        
        st.write("") # Spacer
        generate_btn = st.button("Generate Email Draft", type="primary")
        # Closing div for card container
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Wrapping elements in card CSS
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
            # Placeholder when nothing is generated yet
            st.text_area("Review and Copy:", value="Your generated email will appear here...", height=480, disabled=True, label_visibility="collapsed")
        
        # Closing div for card container
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='glowing-card' id='history-card'><h2>Your Permanent History</h2>", unsafe_allow_html=True)
    st.caption("All previously generated emails are securely stored in your local SQLite database.")
    
    db_history = fetch_history_from_db()
    
    if not db_history:
        st.info("No emails found in the database. Head over to the 'Create New Draft' tab to generate one!")
    else:
        for i, record in enumerate(db_history):
            with st.expander(f"✉️ To: {record['recipient']} | 🎭 Tone: {record['tone']}"):
                st.text_area(label="Draft", value=record['draft'], height=250, key=f"db_hist_{i}", label_visibility="collapsed")
    
    # Closing div for card container
    st.markdown("</div>", unsafe_allow_html=True)
