import streamlit as st
import google.generativeai as genai
import os
import urllib.parse 
from dotenv import load_dotenv

# --- PAGE CONFIGURATION (must be first) ---
st.set_page_config(page_title="AI Email Pro", page_icon="✉️", layout="wide")

# --- SESSION STATE MEMORY (TEMPORARY STORAGE) ---
# This holds data ONLY while the tab is open. If they close the app, it's wiped clean!
if "current_draft" not in st.session_state:
    st.session_state.current_draft = ""
if "current_target_email" not in st.session_state:
    st.session_state.current_target_email = ""
if "email_history" not in st.session_state:
    st.session_state.email_history = [] # This replaces the SQLite database!

# --- CUSTOM CSS FOR THE NEON PURPLE/CYAN THEME ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
    html, body, [class*="css"], h1, h2, h3, .stApp label, .stTabs [data-baseweb="tab"], .stButton>button, .stLinkButton>a {
        font-family: 'Outfit', sans-serif !important;
    }
    .stApp {
        background-color: #1a0b2e; background-image: radial-gradient(#4d298c 1.5px, transparent 1.5px);
        background-size: 25px 25px; color: #ffffff !important; 
    }
    [data-testid="stSidebar"] {
        background-color: #110524; border-right: 2px solid #00f0ff; box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
    }
    #title-container { text-align: center; padding-bottom: 20px; margin-top: 10px; }
    #title-container h1 {
        font-size: 3.5rem; font-weight: 900; background: linear-gradient(90deg, #00f0ff, #ff007f);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem; letter-spacing: 1px; filter: drop-shadow(0 0 10px rgba(255, 0, 127, 0.4));
    }
    #title-container p { color: #bfa6e8; font-size: 1.1rem; margin-top: 0; font-weight: 300; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    .glowing-card {
        background-color: rgba(36, 15, 77, 0.85); backdrop-filter: blur(10px);
        border-radius: 12px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    #details-card { border: 1px solid #00f0ff; box-shadow: 0 0 15px rgba(0, 240, 255, 0.15); }
    #draft-card { border: 1px solid #ff007f; box-shadow: 0 0 15px rgba(255, 0, 127, 0.15); }
    .glowing-card h2 { font-size: 1.6rem; color: #ffffff !important; margin-bottom: 1rem; font-weight: 700; }

    .stTextInput label, .stSelectbox label, .stTextArea label, .stApp p { color: #00f0ff !important; font-size: 1rem !important; }
    [data-testid="stNotification"] { background-color: rgba(0, 240, 255, 0.1) !important; border: 1px solid #00f0ff !important; }
    [data-testid="stNotification"] p { color: #ffffff !important; }

    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(17, 5, 36, 0.9) !important; color: #ffffff !important; 
        border-radius: 8px !important; border: 1px solid #4d298c !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus { border-color: #00f0ff !important; box-shadow: 0 0 0 2px rgba(0, 240, 255, 0.3) !important; }

    .stButton>button, .stLinkButton>a {
        background-image: linear-gradient(90deg, #00f0ff, #0051ff); color: #ffffff !important; border: none;
        border-radius: 8px; font-weight: 700; font-size: 1.1rem; width: 100%; padding: 8px; margin-top: 10px;
        transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0, 240, 255, 0.4); text-align: center; text-decoration: none;
    }
    .stButton>button:hover, .stLinkButton>a:hover {
        background-image: linear-gradient(90deg, #0051ff, #00f0ff); transform: scale(1.02); box-shadow: 0 6px 20px rgba(0, 240, 255, 0.6);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; background-color: rgba(36, 15, 77, 0.6); border-radius: 12px; padding: 5px;
        margin-bottom: 25px; border: 1px solid #4d298c;
    }
    .stTabs [data-baseweb="tab"] { color: #bfa6e8 !important; padding: 10px 20px; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #00f0ff !important; border-bottom: 3px solid #00f0ff; background-color: rgba(0, 240, 255, 0.1); border-radius: 8px 8px 0 0;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- SETUP & CONFIGURATION ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

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

# --- STRUCTURAL LAYOUT ---
st.markdown("""
    <div id='title-container'>
        <h1>AI Follow-Up Writer</h1>
        <p>Generate context-aware follow-up emails instantly. Powered by AI.</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✨ Create New Draft", "🗄️ Current Session History"])

with tab1:
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("<div class='glowing-card' id='details-card'><h2>Email Details</h2>", unsafe_allow_html=True)
        st.info("Provide the context of your meeting to generate a highly tailored response.")
        
        recipient = st.text_input("Recipient's Name", placeholder="e.g., Jane Doe")
        target_email = st.text_input("Recipient's Email Address (Optional)", placeholder="e.g., jane@company.com")
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
                    
                    # 1. Update the current draft display
                    st.session_state.current_draft = draft
                    st.session_state.current_target_email = target_email
                    
                    # 2. Add to the temporary session history (inserting at the top of the list)
                    st.session_state.email_history.insert(0, {
                        "recipient": recipient,
                        "tone": tone,
                        "draft": draft
                    })

        if st.session_state.current_draft:
            st.success("✅ Email generated successfully!")
            st.text_area("Review and Copy:", value=st.session_state.current_draft, height=350, label_visibility="collapsed")
            
            st.divider()
            if st.session_state.current_target_email:
                safe_subject = urllib.parse.quote(f"Follow up regarding our meeting")
                safe_body = urllib.parse.quote(st.session_state.current_draft)
                mailto_link = f"mailto:{st.session_state.current_target_email}?subject={safe_subject}&body={safe_body}"
                st.link_button("🚀 Open in My Email App", mailto_link)
            else:
                st.info("💡 Tip: Enter a 'Recipient Email Address' on the left to unlock the 1-click send button!")
                
        else:
            st.text_area("Review and Copy:", value="Your generated email will appear here...", height=450, disabled=True, label_visibility="collapsed")
        
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='glowing-card' style='border: 1px solid #4d298c;'><h2>Current Session History</h2>", unsafe_allow_html=True)
    st.caption("These emails are saved temporarily. They will be securely erased when you close this window.")
    
    if not st.session_state.email_history:
        st.info("No emails generated yet. Head over to the 'Create New Draft' tab to generate one!")
    else:
        for i, record in enumerate(st.session_state.email_history):
            with st.expander(f"✉️ To: {record['recipient']} | 🎭 Tone: {record['tone']}"):
                st.text_area(label="Draft", value=record['draft'], height=250, key=f"session_hist_{i}", label_visibility="collapsed")
    
    st.markdown("</div>", unsafe_allow_html=True)
