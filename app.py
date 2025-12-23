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

# --- 3. Model Configuration ---
# We are hardcoding the standard name to avoid prefix errors (e.g. 'models/gemini...')
# 'gemini-1.5-flash' is the most stable version for this library.
current_model = "gemini-1.5-flash"

# Sidebar Information
with st.sidebar:
    st.header("System Status")
    st.success("✅ Server Online")
    st.info(f"🤖 Active Model: `{current_model}`")

# --- 4. Main Application Loop ---
uploaded_files = st.file_uploader("Upload Component Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    st.info("ℹ️ Note: A 12-second delay is applied between images to ensure API stability.")
    
    if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
        
        st.divider()
        st.subheader("🔍 Inspection Results")
        
        # Initialize the model
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
                        
                        # Safety Delay
                        time.sleep(12)
                        
                    except Exception as e:
                        # Fallback for 404 or other errors
                        st.error(f"Error: {str(e)}")
                        status = "ERROR"
                        reason = str(e)
                        inspection_results.append({
                            "File Name": file.name,
                            "Status": status,
                            "Details": reason
                        })
                        time.sleep(10)

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