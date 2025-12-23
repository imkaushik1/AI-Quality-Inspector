import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# 1. Page Config
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")

st.title("🏭 AI Quality Inspector Pro")
st.markdown("### Universal Defect Detection System")
st.caption("Powered by Google Gemini AI (Secure Mode)")

# 2. SECURE API KEY HANDLING (No Hardcoding!)
# Ye code ab sirf Streamlit Secrets check karega.
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    # Agar Secrets me key nahi mili to ye error aayega
    st.error("🚨 API Key Missing! Please add GOOGLE_API_KEY to Streamlit Secrets.")
    st.stop()

# --- MODEL DIAGNOSTICS & SELECTION ---
def get_working_model():
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except:
        pass

    # Sidebar Status
    with st.sidebar:
        st.header("⚙️ System Status")
        st.success("✅ Secure Server Connected")
    
    # Priority Selection (Avoid 2.5 Flash due to low quota)
    target_models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro"
    ]

    for target in target_models:
        for available in available_models:
            if target in available and "2.5" not in available:
                return available
                
    return "gemini-1.5-flash" # Fallback

# 3. Main Logic
active_model_name = get_working_model()

# Sidebar Info
with st.sidebar:
    st.info(f"🤖 Active Model: {active_model_name}")

system_prompt = """
Analyze this industrial image for defects (rust, cracks, damage).
Output format strictly:
Status: PASS
OR
Status: FAIL - [Reason]
"""

uploaded_files = st.file_uploader("Upload Component Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    st.info(f"ℹ️ Analyzing with {active_model_name}. Speed optimized for stability.")
    
    if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
        st.divider()
        st.subheader("🔍 Real-Time Analysis")
        model = genai.GenerativeModel(active_model_name)
        results_data = []
        
        for index, uploaded_file in enumerate(uploaded_files):
            col1, col2 = st.columns([1, 2])
            image = Image.open(uploaded_file)
            
            with col1:
                st.image(image, caption=f"Item #{index+1}", use_container_width=True)
            
            with col2:
                with st.spinner(f"Scanning Item #{index+1}..."):
                    ai_output = "Error"
                    # Retry Logic
                    for attempt in range(3):
                        try:
                            response = model.generate_content([system_prompt, image])
                            ai_output = response.text.strip()
                            break 
                        except Exception as e:
                            error_msg = str(e)
                            if "429" in error_msg:
                                time.sleep(20) # Quota wait
                            elif "403" in error_msg:
                                ai_output = "API Key Error (Check Secrets)"
                                break
                            else:
                                time.sleep(5)
                    
                    # Parsing
                    if "Status: PASS" in ai_output:
                        status = "PASS"
                        reason = "✅ No Defects Detected."
                        st.success(f"**PASS**")
                    elif "Status: FAIL" in ai_output:
                        status = "FAIL"
                        reason = ai_output.split("-")[-1].strip() if "-" in ai_output else ai_output
                        st.error(f"**FAIL**: {reason}")
                    else:
                        status = "ERROR"
                        reason = ai_output
                        st.warning(f"⚠️ Analysis Issue: {reason}")
                    
                    results_data.append({"File": uploaded_file.name, "Status": status, "Reason": reason})
                    time.sleep(10) # Safe Delay

        # Final Report
        st.divider()
        if results_data:
            df = pd.DataFrame(results_data)
            def highlight_row(row):
                if row['Status'] == 'PASS': return ['background-color: #d4edda; color: black'] * len(row)
                elif row['Status'] == 'FAIL': return ['background-color: #f8d7da; color: black'] * len(row)
                else: return ['color: black'] * len(row)
            st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)