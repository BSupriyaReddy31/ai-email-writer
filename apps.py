import streamlit as st
import google.generativeai as genai
import os
import urllib.parse 
from dotenv import load_dotenv

# --- PAGE CONFIGURATION (must be first) ---
st.set_page_config(page_title="AI Email Pro", page_icon="✉️", layout="wide")

# --- SESSION STATE MEMORY (TEMPORARY STORAGE) ---
if "current_draft" not in st.session_state:
    st.session_state.current_draft = ""
if "email_history" not in st.session_state:
    st.session_state.email_history = [] 

# --- CUSTOM CSS FOR THE CLEAN/PROFESSIONAL THEME ---
custom_css = """
<style>
   @import url('https://fonts.googleapis.com/css2?family=Lora:wght@300;500;700;900&display=swap');
    html, body, [class*="css"], h1, h2, h3, .stApp label, .stTabs [data-baseweb="tab"], .stButton>button, .stLinkButton>a {
        font-family: 'Lora', sans-serif !important;
    }
    .stApp {
        background-color: #f8f9fa; 
        color: #1f2937 !important; 
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff; border-right: 1px solid #e5e7eb;
    }
    #title-container { text-align: center; padding-bottom: 20px; margin-top: 10px; }
    #title-container h1 {
        font-size: 3.5rem; font-weight: 800; color: #111827;
        margin-bottom: 0.2rem; letter-spacing: -0.5px;
    }
    #title-container p { color: #6b7280; font-size: 1.1rem; margin-top: 0; font-weight: 400; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    .glowing-card {
        background-color: #ffffff;
        border-radius: 12px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e5e7eb;
    }
    .glowing-card h2 { font-size: 1.6rem; color: #111827 !important; margin-bottom: 1rem; font-weight: 700; }

    .stTextInput label, .stSelectbox label, .stTextArea label, .stApp p { color: #111827 !important; font-size: 1.05rem !important; font-weight: 500; }
    [data-testid="stNotification"] { background-color: #eff6ff !important; border: 1px solid #bfdbfe !important; }
    [data-testid="stNotification"] p { color: #1e40af !important; }

    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #f9fafb !important; color: #1f2937 !important; 
        border-radius: 8px !important; border: 1px solid #d1d5db !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus { border-color: #2563eb !important; box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important; }

    .stButton>button, .stLinkButton>a {
        background-color: #e2edfb; color: #ffffff !important; border: none;
        border-radius: 8px; font-weight: 600; font-size: 1.1rem; width: 100%; padding: 10px; margin-top: 10px;
        transition: all 0.2s ease; text-align: center; text-decoration: none;
    }
    .stButton>button:hover, .stLinkButton>a:hover {
        background-color: #ADD8E6; transform: translateY(-1px); box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; background-color: #ffffff; border-radius: 12px; padding: 5px;
        margin-bottom: 25px; border: 1px solid #e5e7eb;
    }
    .stTabs [data-baseweb="tab"] { color: #6b7280 !important; padding: 10px 20px; font-weight: 500; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #2563eb !important; border-bottom: 3px solid #2563eb; background-color: #eff6ff; border-radius: 8px 8px 0 0;
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

if api_key:
    genai.configure(api_key=api_key)
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
        
        # This input is now live and directly controls the button!
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
                    
                    if draft.startswith("An error occurred:"):
                        st.error(f"🚨 API Issue: {draft}")
                    else:
                        st.session_state.current_draft = draft
                        st.session_state.email_history.insert(0, {
                            "recipient": recipient,
                            "tone": tone,
                            "draft": draft
                        })

        if st.session_state.current_draft:
            st.success("✅ Email generated successfully!")
            st.text_area("Review and Copy:", value=st.session_state.current_draft, height=350, label_visibility="collapsed")
            
            st.divider()
            
            # --- THE FIX: We check 'target_email' directly instead of session state ---
            if target_email:
                safe_subject = urllib.parse.quote(f"Follow up regarding our meeting")
                safe_body = urllib.parse.quote(st.session_state.current_draft)
                mailto_link = f"mailto:{target_email}?subject={safe_subject}&body={safe_body}"
                st.link_button("🚀 Open in My Email App", mailto_link)
            else:
                st.info("💡 Tip: Enter a 'Recipient Email Address' on the left and hit Enter to unlock the 1-click send button!")
                
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
                st.markdown(label="Draft", value=record['draft'], height=250, key=f"session_hist_{i}", label_visibility="collapsed")
    
    st.markdown("</div>", unsafe_allow_html=True)
