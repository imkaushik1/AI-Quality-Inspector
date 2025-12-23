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

# --- 3. High-Capacity Model Selector ---
def select_best_model():
    """
    Scans the server list and prioritizes models with HIGH free quotas.
    Avoids '2.5' models because they have very low daily limits.
    """
    try:
        all_models = list(genai.list_models())
        available_names = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        # --- PRIORITY LIST (Based on your server log) ---
        
        # Priority 1: Gemini 2.0 Flash (Stable, High Speed)
        for m in available_names:
            if "gemini-2.0-flash" in m and "exp" not in m and "lite" not in m:
                return m
        
        # Priority 2: Gemini Flash Latest (Alias for the best stable flash)
        for m in available_names:
            if "gemini-flash-latest" in m:
                return m

        # Priority 3: Gemini 1.5 Flash (If available)
        for m in available_names:
            if "gemini-1.5-flash" in m:
                return m
                
        # Priority 4: Gemini 2.0 Flash Lite (Good Backup)
        for m in available_names:
            if "gemini-2.0-flash-lite" in m:
                return m

        # Emergency Fallback: If nothing else, take whatever is first, but warn user
        return available_names[0] if available_names else "models/gemini-1.5-flash"

    except Exception as e:
        return "models/gemini-1.5-flash"

# Run selector
current_model = select_best_model()

# Sidebar Information
with st.sidebar:
    st.header("System Status")
    st.success("✅ Server Online")
    st.info(f"🤖 Active Model: `{current_model}`")
    
    if "2.5" in current_model:
        st.warning("⚠️ Warning: Using v2.5 (Low Quota). Inspection might stop after 20 images.")

# --- 4. Main Application Loop ---
uploaded_files = st.file_uploader("Upload Component Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    st.info("ℹ️ Note: Processing speed is optimized to prevent API errors.")
    
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
                            st.warning