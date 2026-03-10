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
                st.text_area(label="Draft", value=record['draft'], height=250, key=f"session_hist_{i}", label_visibility="collapsed")
    
    st.markdown("</div>", unsafe_allow_html=True)
