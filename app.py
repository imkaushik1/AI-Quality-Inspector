import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# 1. Page Config
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")
st.title("🏭 AI Quality Inspector Pro")

# 2. AUTH CHECK
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"Config Error: {e}")
        st.stop()
else:
    st.error("🚨 API Key Missing! Add GOOGLE_API_KEY to Secrets.")
    st.stop()

# --- SMART MODEL FILTER (NO 2.5 ALLOWED) ---
def get_safe_model():
    try:
        # Step 1: Get all available models
        all_models = list(genai.list_models())
        model_names = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        # Sidebar Debugging (Dekhne ke liye server par kya hai)
        with st.sidebar:
            st.write("📋 Server List:")
            st.code(model_names)

        # Step 2: INTELLIGENT FILTERING
        # Hum specifically '2.5' ko avoid karenge kyunki uski limit kam hai
        
        # Priority 1: Gemini 1.5 Flash (Best Balance)
        for m in model_names:
            if "gemini-1.5-flash" in m and "2.5" not in m:
                return m
        
        # Priority 2: Gemini 1.5 Pro
        for m in model_names:
            if "gemini-1.5-pro" in m and "2.5" not in m:
                return m

        # Priority 3: Gemini Pro Vision (Old Reliable)
        for m in model_names:
            if "vision" in m:
                return m

        # Fallback: Jo bhi mile (majboori mein)
        return model_names[0] if model_names else "models/gemini-1.5-flash"

    except Exception as e:
        return "models/gemini-1.5-flash"

# Active Model Set karo
active_model_name = get_safe_model()
st.sidebar.info(f"🚀 Using Model: `{active_model_name}`")

# 3. Main Logic
system_prompt = """
Analyze this industrial image for defects (rust, cracks, damage).
Output format strictly:
Status: PASS
OR
Status: FAIL - [Reason]
"""

uploaded_files = st.file_uploader("Upload Component Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    # Note to user
    st.info("ℹ️ Running in Safe Mode (12s delay) to ensure free tier stability.")
    
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
                    try:
                        # Call AI
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
                            st.warning(f"⚠️ Issue: {reason}")
                        
                        # --- CRITICAL DELAY ---
                        # 429 Error se bachne ke liye 12 second rukna hi padega
                        time.sleep(12) 

                    except Exception as e:
                        real_error = str(e)
                        # Agar quota error aaye tab bhi rukna padega
                        if "429" in real_error:
                            st.warning("⚠️ High Traffic (Quota Limit). Pausing for 20s...")
                            time.sleep(20)
                            status = "SKIPPED"
                            reason = "Quota Exceeded (Try again)"
                        else:
                            st.error(f"🛑 Error: {real_error}")
                            status = "CRASH"
                            reason = real_error

                    results_data.append({"File": uploaded_file.name, "Status": status, "Reason": reason})

        if results_data:
            st.divider()
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True)