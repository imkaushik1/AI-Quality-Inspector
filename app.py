import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# 1. Page Config
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")
st.title("🏭 AI Quality Inspector Pro")

# 2. AUTHENTICATION & CONNECTION TEST
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"Configuration Error: {e}")
        st.stop()
else:
    st.error("🚨 Secrets Missing! Add GOOGLE_API_KEY to Secrets.")
    st.stop()

# --- THE MODEL HUNTER (Final Fix) ---
def get_valid_model():
    """
    Ye function andhe mein teer nahi chalayega.
    Ye server se list mangega aur valid model return karega.
    """
    try:
        # Step 1: List mangao
        all_models = list(genai.list_models())
        
        # Step 2: Filter karo (Sirf wo jo image dekh sakein)
        vision_models = []
        for m in all_models:
            if 'generateContent' in m.supported_generation_methods:
                vision_models.append(m.name)
        
        # Sidebar me list dikhao (Debugging ke liye)
        with st.sidebar:
            st.write("📋 Available Models on Server:")
            st.code(vision_models)

        # Step 3: Best Model Pick karo (Priority Wise)
        # Hum exact naam match karenge jo list me aaya hai
        
        # Priority 1: 1.5 Flash (Stable)
        for m in vision_models:
            if "gemini-1.5-flash" in m and "001" in m: # Prefer specific version
                return m
        for m in vision_models:
            if "gemini-1.5-flash" in m and "latest" in m:
                return m
        for m in vision_models:
            if "gemini-1.5-flash" in m:
                return m
                
        # Priority 2: Pro Vision (Backup)
        for m in vision_models:
            if "gemini-pro-vision" in m:
                return m

        # Emergency: Agar upar wala kuch na mile, to pehla valid model utha lo
        # (Lekin 2.5 se bacho agar ho sake)
        if vision_models:
            return vision_models[0]
            
        return "models/gemini-1.5-flash" # Absolute fallback
        
    except Exception as e:
        st.sidebar.error(f"List Error: {e}")
        return "gemini-1.5-flash"

# Active Model Set karo
active_model_name = get_valid_model()
st.sidebar.success(f"✅ Connected using: `{active_model_name}`")

# 3. Main Logic
system_prompt = """
Analyze this industrial image for defects (rust, cracks, damage).
Output format strictly:
Status: PASS
OR
Status: FAIL - [Reason]
"""

uploaded_files = st.file_uploader("Upload Component Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
        st.divider()
        st.subheader("🔍 Real-Time Analysis")
        
        # Model Initialize with VALID name
        model = genai.GenerativeModel(active_model_name)
        results_data = []
        
        for index, uploaded_file in enumerate(uploaded_files):
            col1, col2 = st.columns([1, 2])
            image = Image.open(uploaded_file)
            
            with col1:
                st.image(image, caption=f"Item #{index+1}", use_container_width=True)
            
            with col2:
                with st.spinner(f"Scanning Item #{index+1}..."):
                    try:
                        response = model.generate_content([system_prompt, image])
                        ai_output = response.text.strip()
                        
                        if "Status: PASS" in ai_output:
                            status = "PASS"
                            reason = "✅ No Defects Detected."
                            st.success(f"**PASS**")
                        elif "Status: FAIL" in ai_output:
                            status = "FAIL"
                            reason = ai_output.split("-")[-1].strip() if "-" in ai_output else ai_output
                            st.error(f"**FAIL**: {reason}")
                        else:
                            status = "ERROR"
                            reason = ai_output
                            st.warning(f"⚠️ Result: {reason}")

                    except Exception as e:
                        real_error = str(e)
                        st.error(f"🛑 Error: {real_error}")
                        status = "CRASH"
                        reason = real_error

                    results_data.append({"File": uploaded_file.name, "Status": status, "Reason": reason})
                    time.sleep(5) 

        if results_data:
            st.divider()
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True)