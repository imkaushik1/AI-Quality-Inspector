import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# 1. Page Config
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")
st.title("🏭 AI Quality Inspector Pro")

# 2. STRICT AUTH CHECK (Startup Test)
# Ye code start hote hi check karega ki Key kaam kar rahi hai ya nahi
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    try:
        genai.configure(api_key=api_key)
        # Turant ek choti call karke dekho ki connection zinda hai
        models = list(genai.list_models())
        st.sidebar.success(f"✅ Secure Connection Active")
    except Exception as e:
        st.sidebar.error("❌ Key Connection Failed!")
        st.error(f"CRITICAL ERROR: API Key kaam nahi kar rahi. Details: {str(e)}")
        st.stop()
else:
    st.error("🚨 API Key Missing! Secrets me key add karo.")
    st.stop()

# 3. Model Setup
def get_best_model():
    return "gemini-1.5-flash"

active_model_name = get_best_model()

system_prompt = """
Analyze this industrial image for defects (rust, cracks, damage).
Output format strictly:
Status: PASS
OR
Status: FAIL - [Reason]
"""

uploaded_files = st.file_uploader("Upload Component Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
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
                    
                    # --- THE X-RAY LOGIC ---
                    try:
                        # Direct call - koi retry chupaone wala logic nahi
                        response = model.generate_content([system_prompt, image])
                        ai_output = response.text.strip()
                        
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
                            st.warning(f"⚠️ Format Issue: {reason}")

                    except Exception as e:
                        # YAHAN ASLI ERROR DIKHEGA
                        real_error = str(e)
                        st.error(f"🛑 TECHNICAL ERROR: {real_error}")
                        status = "CRASH"
                        reason = real_error

                    results_data.append({"File": uploaded_file.name, "Status": status, "Reason": reason})
                    time.sleep(5) 

        # Summary Table
        if results_data:
            st.divider()
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True)