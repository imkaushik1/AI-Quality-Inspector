import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# 1. Page Config
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")

st.title("🏭 AI Quality Inspector Pro")
st.markdown("### Universal Defect Detection System")
st.caption("Powered by Google Gemini AI")

# 2. SECURE API KEY HANDLING
# Ab hum key code me nahi likhenge. Hum Secrets se mangenge.
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    # Sidebar me confirm karenge ki key mil gayi
    with st.sidebar:
        st.header("⚙️ Settings")
        st.success("✅ Secure Key Loaded!")
else:
    # Agar Secrets me key nahi mili, to error dikhayega
    st.error("🚨 API Key Missing! Please add it to Streamlit Secrets.")
    st.stop() # App yahin ruk jayega

# Configure Google AI
genai.configure(api_key=api_key)

# Model Finder
def find_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return m.name
                if 'pro-vision' in m.name: return m.name
        return "gemini-1.5-flash"
    except:
        return "gemini-1.5-flash"

# 3. Main Logic
active_model_name = find_working_model()

system_prompt = """
Analyze this industrial image for defects (rust, cracks, damage).
Output format strictly:
Status: PASS
OR
Status: FAIL - [Reason]
"""

uploaded_files = st.file_uploader(
    "Upload Component Images", 
    type=["jpg", "png", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"ℹ️ Secure Mode: Processing speed is optimized for Free Tier (15s delay per item).")
    
    if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
        
        st.divider()
        st.subheader("🔍 Real-Time Analysis")
        
        model = genai.GenerativeModel(active_model_name)
        results_data = []
        
        for index, uploaded_file in enumerate(uploaded_files):
            col1, col2 = st.columns([1, 2])
            
            try:
                image = Image.open(uploaded_file)
                
                with col1:
                    st.image(image, caption=f"Item #{index+1}", use_container_width=True)
                
                with col2:
                    with st.spinner(f"Scanning Item #{index+1}..."):
                        
                        response = model.generate_content([system_prompt, image])
                        ai_output = response.text.strip()
                        
                        # 15s Delay to prevent 429 Error
                        time.sleep(15) 

                        if "Status: PASS" in ai_output:
                            status = "PASS"
                            reason = "✅ No Defects Detected. Component is safe."
                            st.success(f"**STATUS: PASS**\n\n{reason}")
                        else:
                            status = "FAIL"
                            reason = ai_output.split("-")[-1].strip() if "-" in ai_output else ai_output
                            st.error(f"**STATUS: FAIL**\n\n❌ Defect Found: {reason}")
                        
                        results_data.append({
                            "File": uploaded_file.name,
                            "Status": status,
                            "Reason": reason
                        })

            except Exception as e:
                st.error(f"Error analyzing {uploaded_file.name}: {e}")
                time.sleep(15)

        # 4. Final Summary (VISIBILITY FIX INCLUDED)
        st.divider()
        st.subheader("📋 Final Report Summary")
        if results_data:
            df = pd.DataFrame(results_data)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Items", len(df))
            m2.metric("Passed", len(df[df["Status"] == "PASS"]))
            m3.metric("Defective", len(df[df["Status"] == "FAIL"]))

            # --- CSS STYLING FIX (BLACK TEXT) ---
            def highlight_row(row):
                if row['Status'] == 'PASS':
                    return ['background-color: #d4edda; color: black'] * len(row)
                else:
                    return ['background-color: #f8d7da; color: black'] * len(row)

            st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

else:
    st.info("👆 Upload photos to start inspection.")