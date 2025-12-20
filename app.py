import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Quality Inspector", page_icon="🏭")
st.title("🏭 AI Quality Inspector (Auto-Fix Mode)")

api_key = st.text_input("Enter Google API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    # --- DIAGNOSTIC STEP (Ye error fix karega) ---
    st.info("🔄 Connecting to Google Server to find available models...")
    
    try:
        # 1. Server se poocho ki kaunse models available hain
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # 2. List mein se sabse best model dhundo
        selected_model_name = None
        
        # Priority 1: Gemini 1.5 Flash (Latest)
        for m in available_models:
            if "gemini-1.5-flash" in m:
                selected_model_name = m
                break
        
        # Priority 2: Gemini Pro Vision (Old Reliable)
        if not selected_model_name:
            for m in available_models:
                if "vision" in m:
                    selected_model_name = m
                    break
                    
        # Priority 3: Jo bhi pehla mile (Fallback)
        if not selected_model_name and available_models:
            selected_model_name = available_models[0]
            
        if selected_model_name:
            st.success(f"✅ Connected! Using Model: **{selected_model_name}**")
            model = genai.GenerativeModel(selected_model_name)
            
            # --- UPLOAD & CHECK ---
            uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
            if uploaded_file:
                st.image(uploaded_file, width=300)
                if st.button("Check Quality"):
                    try:
                        response = model.generate_content(["Check for defects. Answer PASS or FAIL.", Image.open(uploaded_file)])
                        st.write(response.text)
                    except Exception as inner_e:
                        st.error(f"Analysis Error: {inner_e}")
        else:
            st.error("❌ No compatible models found attached to this API Key.")
            st.write("Available List:", available_models)

    except Exception as e:
        st.error(f"Connection Error: {e}")
        st.help("Try creating a NEW API Key from Google AI Studio.")