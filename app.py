import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# --- 1. Page Configuration ---
st.set_page_config(page_title="Quality Inspector AI", page_icon="🏭", layout="wide")
st.title("🏭 Quality Inspector AI")
st.markdown("### Automated Defect Detection System")
st.write("Upload images of mechanical parts to inspect for defects (Rust, Cracks, etc.)")

# --- 2. API Key Authentication ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("🚨 Error: API Key not found. Please add GOOGLE_API_KEY to Streamlit Secrets.")
    st.stop()

# --- 3. Smart Model Selection (Fix for 404 Error) ---
# This function asks the server what is available instead of guessing
def get_working_model_name():
    try:
        # Get the actual list from Google
        models = genai.list_models()
        
        # Look for a vision model (prioritize 1.5-flash, avoid 2.5)
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                model_name = m.name
                
                # We prefer 'flash' because it's fast, but we avoid '2.5' due to limits
                if "flash" in model_name and "1.5" in model_name:
                    return model_name
        
        # If 1.5 flash isn't found, grab the first available vision model (backup)
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                if "vision" in m.name or "pro" in m.name:
                    return m.name
                    
        return "models/gemini-1.5-flash" # Absolute fallback
    except:
        return "models/gemini-1.5-flash"

current_model = get_working_model_name()

# Sidebar Information
with st.sidebar:
    st.header("System Status")
    st.success("✅ Server Online")
    st.info(f"🤖 Connected Model: `{current_model}`")

# --- 4. Main Application Loop ---
uploaded_files = st.file_uploader("Upload Component Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    st.info("ℹ️ Note: A 12-second delay is applied between images to ensure API stability.")
    
    if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
        
        st.divider()
        st.subheader("🔍 Inspection Results")
        
        # Initialize the model using the EXACT name found above
        model = genai.GenerativeModel(current_model)
        inspection_results = []
        
        for file in uploaded_files:
            col1, col2 = st.columns([1, 2])
            
            # Display Image
            img = Image.open(file)
            col1.image(img, caption=file.name, use_container_width=True)
            
            with col2:
                with st.spinner("Analyzing component..."):
                    try:
                        # Prompt Engineering
                        prompt = """
                        Analyze this industrial image for defects (rust, cracks, damage).
                        Output strictly in this format:
                        Status: PASS
                        OR
                        Status: FAIL - [Reason]
                        """
                        
                        # AI Request
                        response = model.generate_content([prompt, img])
                        text = response.text.strip()
                        
                        # Logic to parse the result
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
                            
                        # Save result
                        inspection_results.append({
                            "File Name": file.name,
                            "Status": status,
                            "Details": reason
                        })
                        
                        # Safety Delay (Prevents 429 Error)
                        time.sleep(12)
                        
                    except Exception as e:
                        st.error(f"Processing Error: {str(e)}")
                        time.sleep(20)

        # --- 5. Final Report ---
        if inspection_results:
            st.divider()
            st.subheader("📋 Final Report Summary")
            
            df = pd.DataFrame(inspection_results)
            
            def highlight_status(row):
                if row['Status'] == 'PASS':
                    return ['background-color: #d1e7dd; color: black'] * len(row)
                elif row['Status'] == 'FAIL':
                    return ['background-color: #f8d7da; color: black'] * len(row)
                else:
                    return ['color: black'] * len(row)

            st.dataframe(df.style.apply(highlight_status, axis=1), use_container_width=True)