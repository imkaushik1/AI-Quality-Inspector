import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Quality Inspector", page_icon="🏭")

st.title("🏭 AI Quality Inspector (Stable)")

# 1. API Key Setup
# Humne wapis simple input box rakha hai taaki errors kam ho
api_key = st.text_input("Enter Google API Key", type="password")

if api_key:
    # 2. Configuration
    genai.configure(api_key=api_key)
    
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        st.image(uploaded_file, caption="Inspecting...", width=300)
        
        if st.button("Check Defects"):
            try:
                # --- YE HAI MAIN CHANGE ---
                # Hum 'flash' use nahi karenge, wo naya hai aur error de raha hai.
                # Hum 'gemini-pro-vision' use karenge jo old server par bhi chalta hai.
                model = genai.GenerativeModel("gemini-pro-vision")
                
                # Request bhejo
                response = model.generate_content(["Check this industrial part for defects (rust, crack). Answer with PASS or FAIL and reason.", Image.open(uploaded_file)])
                
                # Result dikhao
                st.success("Result:")
                st.write(response.text)
                
            except Exception as e:
                # Agar ye bhi fail hua to error dikhayega
                st.error(f"Error details: {e}")