import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="AI Inspector", page_icon="🏭", layout="wide")
st.title("🏭 AI Quality Inspector")
st.markdown("### Powered by Google Gemini")

# 2. Sidebar - Authentication & Auto-Detection
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key Input
    api_key = st.text_input("Enter Google API Key", type="password")
    
    # List to store found models
    available_model_names = []
    
    if api_key:
        try:
            # Configure API
            genai.configure(api_key=api_key)
            
            # 🔍 AUTO-DETECT: Google se pucho kya available hai
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Clean up name (remove 'models/' prefix)
                    name = m.name.replace("models/", "")
                    available_model_names.append(name)
            
            st.success(f"✅ Found {len(available_model_names)} Models!")
            
        except Exception as e:
            st.error(f"Key Error: {e}")

    st.divider()
    
    # 3. Dynamic Model Selector
    if available_model_names:
        selected_model = st.selectbox(
            "Select AI Model (Auto-Detected):",
            available_model_names,
            index=0
        )
    else:
        # Fallback agar key nahi daali
        selected_model = "gemini-pro"
        st.info("⚠️ Enter Key to see valid models")

# 4. Main Logic
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Part", use_column_width=True)
    
    if st.button("🔍 Run Inspection", type="primary"):
        if not api_key:
            st.error("⚠️ API Key daalo!")
        else:
            try:
                with st.spinner(f"Analyzing with {selected_model}..."):
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(selected_model)
                    
                    prompt = """
                    Act as a Senior QA Engineer. Analyze this mechanical part.
                    Report format:
                    1. **Defect Name**: (e.g., Rust, Crack, or None)
                    2. **Severity**: (Low/Medium/High)
                    3. **Action**: (Accept/Reject/Rework)
                    4. **Explanation**: One line technical reason.
                    """
                    
                    response = model.generate_content([prompt, image])
                    st.success("Inspection Complete!")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"Error: {e}")