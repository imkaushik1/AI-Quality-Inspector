import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# 1. Page Config
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")

st.title("🏭 AI Quality Inspector Pro")
st.markdown("### Universal Defect Detection System")
st.caption("Powered by Google Gemini 1.5 Flash (High Capacity Mode)")

# 2. SECURE API KEY HANDLING
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    with st.sidebar:
        st.header("⚙️ Settings")
        st.success("✅ Secure Key Loaded!")
else:
    st.error("🚨 API Key Missing! Add it to Streamlit Secrets.")
    st.stop()

# Configure Google AI
genai.configure(api_key=api_key)

# --- CRITICAL FIX: HARDCODE THE HIGH-LIMIT MODEL ---
# Hum auto-detect hata rahe hain kyunki wo low-limit wala model utha raha tha.
active_model_name = "gemini-1.5-flash"

system_prompt = """
Analyze this industrial image for defects (rust, cracks, damage).
Output format strictly:
Status: PASS
OR
Status: FAIL - [Reason]
"""

uploaded_files = st.file_uploader(
    "Upload Component Images", 
    type=["jpg", "png", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"ℹ️ Optimized Mode: Using {active_model_name} for maximum daily quota.")
    
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
                status_placeholder = st.empty()
                with st.spinner(f"Scanning Item #{index+1}..."):
                    
                    # --- SMART RETRY LOGIC (ZIDDI MODE) ---
                    max_retries = 3
                    ai_output = "Error"
                    
                    for attempt in range(max_retries):
                        try:
                            # AI Call
                            response = model.generate_content([system_prompt, image])
                            ai_output = response.text.strip()
                            break # Agar safal hua to loop todo
                        except Exception as e:
                            error_msg = str(e)
                            if "429" in error_msg:
                                # Agar Quota error aaye to 30 second ruko
                                status_placeholder.warning(f"⚠️ High Traffic. Retrying in 30s... (Attempt {attempt+1}/{max_retries})")
                                time.sleep(30)
                            else:
                                ai_output = f"Error: {error_msg}"
                                break
                    
                    # Result Processing
                    if "Status: PASS" in ai_output:
                        status = "PASS"
                        reason = "✅ No Defects Detected. Component is safe."
                        st.success(f"**STATUS: PASS**\n\n{reason}")
                    elif "Status: FAIL" in ai_output:
                        status = "FAIL"
                        reason = ai_output.split("-")[-1].strip() if "-" in ai_output else ai_output
                        st.error(f"**STATUS: FAIL**\n\n❌ Defect Found: {reason}")
                    else:
                        status = "ERROR"
                        reason = ai_output
                        st.error(f"Analysis Failed: {reason}")
                    
                    results_data.append({
                        "File": uploaded_file.name,
                        "Status": status,
                        "Reason": reason
                    })
                    
                    # Normal Gap
                    time.sleep(2)

        # 4. Final Summary (High Visibility)
        st.divider()
        st.subheader("📋 Final Report Summary")
        if results_data:
            df = pd.DataFrame(results_data)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Items", len(df))
            m2.metric("Passed", len(df[df["Status"] == "PASS"]))
            m3.metric("Defective", len(df[df["Status"] == "FAIL"]))

            # Black Text Fix
            def highlight_row(row):
                if row['Status'] == 'PASS':
                    return ['background-color: #d4edda; color: black'] * len(row)
                elif row['Status'] == 'FAIL':
                    return ['background-color: #f8d7da; color: black'] * len(row)
                else:
                    return ['color: black'] * len(row)

            st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

else:
    st.info("👆 Upload photos to start inspection.")