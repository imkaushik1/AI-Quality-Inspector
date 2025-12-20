import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Title
st.title("🏭 AI Quality Inspector (Fresh Start)")

# 2. API Key Box
api_key = st.text_input("Enter Google API Key", type="password")

# 3. Main Logic
if api_key:
    # Setup
    genai.configure(api_key=api_key)
    
    # Upload Image
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", width=300)
        
        if st.button("Check Quality"):
            try:
                # Sabse latest model try karte hain
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Simple Prompt
                response = model.generate_content(["Is this industrial part defective? Answer Yes/No and give a reason.", Image.open(uploaded_file)])
                
                # Result Dikhana
                st.success("Analysis Complete:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Error aaya: {e}")