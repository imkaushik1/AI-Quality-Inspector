import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

# 1. Page Config (Professional UI)
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")

st.title("🏭 AI Quality Inspector Pro")
st.markdown("### Universal Defect Detection System (Auto-Pilot)")
st.caption("Powered by Google Gemini AI")

# 2. API Key Handling
with st.sidebar:
    st.header("⚙️ Settings")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Connected to Server Key")
    else:
        api_key = st.text_input("Enter Google API Key", type="password")

# --- SMART MODEL FINDER ---
def find_working_model():
    """Google se puchta hai ki kaunsa model zinda hai."""
    try:
        for m in genai.list_models():
            # Hame wo model chahiye jo content generate kare (vision/flash)
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return m.name
                if 'pro-vision' in m.name: return m.name
                if 'gemini-1.5' in m.name: return m.name
        return "gemini-1.5-flash" # Default fallback
    except:
        return "gemini-1.5-flash"

# 3. Main Logic
if api_key:
    genai.configure(api_key=api_key)
    
    # Auto-select the best available model
    active_model_name = find_working_model()
    # Sidebar me dikhayega kaunsa model use ho raha hai
    with st.sidebar:
        st.info(f"🤖 Active Model: {active_model_name}")

    # System Prompt
    system_prompt = """
    Analyze this industrial image for defects (rust, cracks, damage).
    Output format strictly:
    Status: PASS
    OR
    Status: FAIL - [Reason]
    """

    # 4. Upload Section
    uploaded_files = st.file_uploader(
        "Upload Component Images (Batch Mode)", 
        type=["jpg", "png", "jpeg"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.divider()
        st.subheader("🔍 Inspection Results")
        
        results_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
            model = genai.GenerativeModel(active_model_name)
            
            for index, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Inspecting Item {index + 1}/{len(uploaded_files)}...")
                progress_bar.progress((index + 1) / len(uploaded_files))
                
                try:
                    image = Image.open(uploaded_file)
                    # Universal Call (Safe for all models)
                    response = model.generate_content([system_prompt, image])
                    ai_output = response.text.strip()
                    
                    if "Status: PASS" in ai_output:
                        status = "PASS"
                        reason = "Clean Component"
                    else:
                        status = "FAIL"
                        reason = ai_output.split("-")[-1].strip() if "-" in ai_output else ai_output
                    
                    results_data.append({
                        "File Name": uploaded_file.name,
                        "Status": status,
                        "Reason/Analysis": reason
                    })
                    
                except Exception as e:
                    # Agar fail ho to list me error dikhaye
                    results_data.append({
                        "File Name": uploaded_file.name,
                        "Status": "ERROR",
                        "Reason/Analysis": str(e)
                    })

            # 5. Dashboard
            st.divider()
            if results_data:
                df = pd.DataFrame(results_data)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total", len(df))
                col2.metric("✅ Passed", len(df[df["Status"] == "PASS"]))
                col3.metric("❌ Defective", len(df[df["Status"] == "FAIL"]))
                
                def highlight_status(val):
                    if val == 'PASS': return 'background-color: #d4edda; color: black'
                    elif val == 'FAIL': return 'background-color: #f8d7da; color: black'
                    else: return 'color: black'

                st.dataframe(df.style.map(highlight_status, subset=['Status']), use_container_width=True)
                st.success("✅ Process Complete")

    else:
        st.info("👆 Upload photos to start.")

else:
    st.warning("⚠️ Enter API Key to start.")