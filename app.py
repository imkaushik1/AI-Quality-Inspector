import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

# Page Setup
st.set_page_config(page_title="AI Quality Inspector", page_icon="🏭", layout="wide")
st.title("🏭 AI Quality Inspector Pro")
st.markdown("### Universal Defect Detection System")

# API Key
with st.sidebar:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Key Connected ✅")
    else:
        api_key = st.text_input("Enter API Key", type="password")

if api_key:
    # 1. Configuration (Sabse Important)
    genai.configure(api_key=api_key)
    
    # 2. Model Setup (Direct Call)
    # Agar ye fail hua, toh server update nahi hua hai.
    model = genai.GenerativeModel("gemini-1.5-flash")

    uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True)

    if uploaded_files and st.button("Start Inspection"):
        results = []
        progress = st.progress(0)
        
        for idx, file in enumerate(uploaded_files):
            progress.progress((idx + 1) / len(uploaded_files))
            try:
                img = Image.open(file)
                # Simple Prompt
                response = model.generate_content(["Is this industrial part defective? Answer strictly 'Status: PASS' or 'Status: FAIL - reason'.", img])
                results.append({"File": file.name, "Analysis": response.text.strip()})
            except Exception as e:
                # Yahan hum asli error dikhayenge taaki chupa na rahe
                st.error(f"Error in {file.name}: {str(e)}")
        
        st.dataframe(pd.DataFrame(results), use_container_width=True)