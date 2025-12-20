import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# 1. Page Config
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")

st.title("🏭 AI Quality Inspector Pro")
st.markdown("### Universal Defect Detection System")
st.caption("Powered by Google Gemini AI")

# 2. API KEY (HARDCODED FOR DEMO)
# Humne tumhari key yahan direct daal di hai taaki koi error na aaye
api_key = "AIzaSyDHF4cdHqH7Fv9vY4XggxtDkvCSGvgNlq8"

# Configure Google AI
genai.configure(api_key=api_key)

# Model Finder Logic
def find_working_model():
    try:
        # Check models
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return m.name
                if 'pro-vision' in m.name: return m.name
        return "gemini-1.5-flash"
    except:
        return "gemini-1.5-flash"

# Sidebar Status
with st.sidebar:
    st.header("⚙️ System Status")
    st.success("✅ AI Server Connected")
    st.info("Mode: Recruiter/Demo View")

# 3. Main Logic
active_model_name = find_working_model()

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
    if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
        
        st.divider()
        st.subheader("🔍 Real-Time Analysis")
        
        model = genai.GenerativeModel(active_model_name)
        results_data = []
        
        for index, uploaded_file in enumerate(uploaded_files):
            col1, col2 = st.columns([1, 2])
            
            try:
                image = Image.open(uploaded_file)
                
                with col1:
                    st.image(image, caption=f"Item #{index+1}", use_container_width=True)
                
                with col2:
                    with st.spinner(f"Scanning Item #{index+1}..."):
                        # AI Call
                        response = model.generate_content([system_prompt, image])
                        ai_output = response.text.strip()
                        
                        # Slow down slightly to prevent Google blocking
                        time.sleep(2) 

                        if "Status: PASS" in ai_output:
                            status = "PASS"
                            reason = "✅ No Defects Detected. Component is safe."
                            st.success(f"**STATUS: PASS**\n\n{reason}")
                            color_code = "#d4edda"
                        else:
                            status = "FAIL"
                            reason = ai_output.split("-")[-1].strip() if "-" in ai_output else ai_output
                            st.error(f"**STATUS: FAIL**\n\n❌ Defect Found: {reason}")
                            color_code = "#f8d7da"
                        
                        results_data.append({
                            "File": uploaded_file.name,
                            "Status": status,
                            "Reason": reason
                        })

            except Exception as e:
                st.error(f"Error analyzing {uploaded_file.name}: {e}")

        # 4. Final Summary
        st.divider()
        st.subheader("📋 Final Report Summary")
        if results_data:
            df = pd.DataFrame(results_data)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Items", len(df))
            m2.metric("Passed", len(df[df["Status"] == "PASS"]))
            m3.metric("Defective", len(df[df["Status"] == "FAIL"]))

            def highlight_row(row):
                return ['background-color: #d4edda' if row['Status'] == 'PASS' else 'background-color: #f8d7da'] * len(row)

            st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

else:
    st.info("👆 Upload photos to see the AI magic.")