import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time
import sys

# --- 1. Page Configuration ---
st.set_page_config(page_title="Quality Inspector AI", page_icon="🏭", layout="wide")
st.title("🏭 Quality Inspector AI")
st.write("Upload images of mechanical parts to inspect for defects (Rust, Cracks, etc.)")

# --- 2. API Key Authentication ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("🚨 Error: API Key not found. Please add GOOGLE_API_KEY to Streamlit Secrets.")
    st.stop()

# --- 3. THE NUCLEAR MODEL SELECTOR ---
def get_any_working_model():
    """
    Ye function server se list mangta hai aur '1.0-pro' (Text only) ko chhod kar
    jo bhi pehla model mile, use utha leta hai.
    """
    try:
        available_models = list(genai.list_models())
        vision_models = []
        
        # Filter logic: Hame wo model chahiye jo Image dekh sake
        for m in available_models:
            if 'generateContent' in m.supported_generation_methods:
                # 1.0-pro text only hai, use avoid karo
                if "1.0-pro" not in m.name:
                    vision_models.append(m.name)
        
        # Debugging: Sidebar me dikhao kya mila
        with st.sidebar:
            st.write("📋 Server Models List:")
            st.code(vision_models)

        # Selection Strategy
        # Pehle koshish karo Flash dhoondne ki
        for m in vision_models:
            if "flash" in m and "1.5" in m: return m
        
        # Phir Pro dhoondho
        for m in vision_models:
            if "pro" in m and "1.5" in m: return m
            
        # Phir Vision dhoondho (Old)
        for m in vision_models:
            if "vision" in m: return m
            
        # Agar kuch na mile, to list ka pehla utha lo
        if vision_models:
            return vision_models[0]
            
        return "models/gemini-1.5-flash" # Absolute Fail
        
    except Exception as e:
        st.sidebar.error(f"List Error: {e}")
        return "models/gemini-1.5-flash"

# Automatically find the best model name
current_model = get_any_working_model()

# Sidebar Information (Debugging Info)
with st.sidebar:
    st.header("System Diagnostics")
    st.success("✅ Server Online")
    st.text(f"Lib Version: {genai.__version__}") # Check version
    st.info(f"🤖 Selected Model: `{current_model}`")

# --- 4. Main Application Loop ---
uploaded_files = st.file_uploader("Upload Component Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    st.info("ℹ️ Processing with dynamic model selection.")
    
    if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
        
        st.divider()
        st.subheader("🔍 Inspection Results")
        
        # Initialize the model with the EXACT name found
        model = genai.GenerativeModel(current_model)
        inspection_results = []
        
        for file in uploaded_files:
            col1, col2 = st.columns([1, 2])
            img = Image.open(file)
            col1.image(img, caption=file.name, use_container_width=True)
            
            with col2:
                with st.spinner("Analyzing component..."):
                    try:
                        prompt = """
                        Analyze this industrial image for defects (rust, cracks, damage).
                        Output strictly in this format:
                        Status: PASS
                        OR
                        Status: FAIL - [Reason]
                        """
                        
                        response = model.generate_content([prompt, img])
                        text = response.text.strip()
                        
                        if "Status: PASS" in text:
                            status = "PASS"
                            reason = "✅ No defects detected. Component is safe."
                            st.success(f"**STATUS: PASS**")
                            st.caption(reason)
                        elif "Status: FAIL" in text:
                            status = "FAIL"
                            reason = text.split("-")[-1].strip() if "-" in text else text
                            st.error(f"**STATUS: FAIL**")
                            st.markdown(f"**Defect:** {reason}")
                        else:
                            status = "REVIEW"
                            reason = text
                            st.warning(f"⚠️ Manual Review Needed: {text}")
                            
                        inspection_results.append({
                            "File Name": file.name,
                            "Status": status,
                            "Details": reason
                        })
                        time.sleep(10)
                        
                    except Exception as e:
                        st.error(f"Processing Failed: {str(e)}")
                        inspection_results.append({
                            "File Name": file.name,
                            "Status": "ERROR",
                            "Details": str(e)
                        })
                        time.sleep(5)

        if inspection_results:
            st.divider()
            df = pd.DataFrame(inspection_results)
            def highlight_status(row):
                if row['Status'] == 'PASS': return ['background-color: #d1e7dd; color: black'] * len(row)
                elif row['Status'] == 'FAIL': return ['background-color: #f8d7da; color: black'] * len(row)
                else: return ['color: black'] * len(row)
            st.dataframe(df.style.apply(highlight_status, axis=1), use_container_width=True)