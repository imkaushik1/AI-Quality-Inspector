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
# Check if the API key is available in Streamlit Secrets
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("🚨 Error: API Key not found. Please add GOOGLE_API_KEY to Streamlit Secrets.")
    st.stop()

# --- 3. Model Selection Logic ---
# Function to find a stable model and avoid experimental ones with low quotas
def select_stable_model():
    try:
        # Get list of models from Google
        all_models = genai.list_models()
        
        for m in all_models:
            if 'generateContent' in m.supported_generation_methods:
                name = m.name
                # We specifically look for '1.5-flash' and avoid '2.5' to prevent rate limit errors
                if "gemini-1.5-flash" in name and "2.5" not in name:
                    return name
        
        return "models/gemini-1.5-flash" # Default fallback
    except:
        return "models/gemini-1.5-flash"

current_model = select_stable_model()

# Sidebar Information
with st.sidebar:
    st.header("System Status")
    st.success("✅ Server Online")
    st.info(f"🤖 Active Model: `{current_model}`")

# --- 4. Main Application Loop ---
uploaded_files = st.file_uploader("Upload Component Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    st.info("ℹ️ Note: A 12-second delay is applied between images to ensure API stability on the free tier.")
    
    if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
        
        st.divider()
        st.subheader("🔍 Inspection Results")
        
        # Initialize model
        model = genai.GenerativeModel(current_model)
        inspection_results = []
        
        # Process each uploaded file
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
                        
                        # logic to parse the result
                        if "Status: PASS" in text:
                            status = "PASS"
                            reason = "✅ No defects detected. Component is safe."
                            st.success(f"**STATUS: PASS**")
                            st.caption(reason)
                            
                        elif "Status: FAIL" in text:
                            status = "FAIL"
                            # Extracting the reason string
                            reason = text.split("-")[-1].strip() if "-" in text else text
                            st.error(f"**STATUS: FAIL**")
                            st.markdown(f"**Defect:** {reason}")
                            
                        else:
                            status = "REVIEW"
                            reason = text
                            st.warning(f"⚠️ Manual Review Needed: {text}")
                            
                        # Save result to list
                        inspection_results.append({
                            "File Name": file.name,
                            "Status": status,
                            "Details": reason
                        })
                        
                        # Safety Delay (Prevents 429 Quota Error)
                        time.sleep(12)
                        
                    except Exception as e:
                        st.error(f"Processing Error: {str(e)}")
                        # Extended wait if an error occurs
                        time.sleep(20)

        # --- 5. Final Report Generation ---
        if inspection_results:
            st.divider()
            st.subheader("📋 Final Report Summary")
            
            # Create a DataFrame
            df = pd.DataFrame(inspection_results)
            
            # Simple styling function for the table
            def highlight_status(row):
                if row['Status'] == 'PASS':
                    return ['background-color: #d1e7dd; color: black'] * len(row) # Green
                elif row['Status'] == 'FAIL':
                    return ['background-color: #f8d7da; color: black'] * len(row) # Red
                else:
                    return ['color: black'] * len(row)

            # Display the styled table
            st.dataframe(df.style.apply(highlight_status, axis=1), use_container_width=True)