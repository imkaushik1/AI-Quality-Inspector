import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# 1. Page Config
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")

st.title("🏭 AI Quality Inspector Pro")
st.markdown("### Universal Defect Detection System")
st.caption("Powered by Google Gemini AI (Auto-Optimized)")

# 2. SECURE API KEY HANDLING
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    with st.sidebar:
        st.header("⚙️ Settings")
        st.success("✅ Secure Key Loaded!")
else:
    st.error("🚨 API Key Missing! Please add it to Streamlit Secrets.")
    st.stop()

# Configure Google AI
genai.configure(api_key=api_key)

# --- SMART MODEL FINDER (The Real Fix) ---
def get_best_model():
    """
    Ye function server se available models ki list mangta hai.
    Hum '2.5' ko avoid karenge (low quota) aur '1.5' ya 'pro' dhundenge.
    """
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Priority 1: 1.5 Flash (Best Balance)
        for m in available_models:
            if "gemini-1.5-flash" in m and "2.5" not in m:
                return m
        
        # Priority 2: Gemini Pro Vision (Old Reliable)
        for m in available_models:
            if "vision" in m:
                return m
                
        # Priority 3: Gemini 1.5 Pro (Powerful but slower)
        for m in available_models:
            if "gemini-1.5-pro" in m:
                return m

        # Emergency Fallback: Agar kuch na mile to jo hai wo dedo (even 2.5)
        return available_models[0] if available_models else "gemini-1.5-flash"
    except:
        return "gemini-1.5-flash"

# 3. Main Logic
active_model_name = get_best_model()

# Sidebar me dikhao kaunsa model select hua
with st.sidebar:
    st.info(f"🤖 Active Model: {active_model_name}")

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
    st.info(f"ℹ️ Processing with {active_model_name}. Speed limit active to prevent errors.")
    
    if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
        
        st.divider()
        st.subheader("🔍 Real-Time Analysis")
        
        model = genai.GenerativeModel(active_model_name)
        results_data = []
        
        for index, uploaded_file in enumerate(uploaded_files):
            col1, col2 = st.columns([1, 2])
            
            image = Image.open(uploaded_file)
            with col1:
                st.image(image, caption=f"Item #{index+1}", use_container_width=True)
            
            with col2:
                status_placeholder = st.empty()
                with st.spinner(f"Scanning Item #{index+1}..."):
                    
                    # RETRY LOGIC for Quota Errors
                    max_retries = 3
                    ai_output = "Error"
                    
                    for attempt in range(max_retries):
                        try:
                            response = model.generate_content([system_prompt, image])
                            ai_output = response.text.strip()
                            break 
                        except Exception as e:
                            error_msg = str(e)
                            # Agar Quota error aaye (429) to wait karo
                            if "429" in error_msg:
                                status_placeholder.warning(f"⚠️ High Traffic. Retrying in 20s... (Attempt {attempt+1})")
                                time.sleep(20)
                            # Agar 404 aaye to loop break karke error dikhao
                            elif "404" in error_msg:
                                ai_output = f"Model Error: {error_msg}"
                                break
                            else:
                                ai_output = f"Error: {error_msg}"
                                time.sleep(5)
                    
                    # Result Processing
                    if "Status: PASS" in ai_output:
                        status = "PASS"
                        reason = "✅ No Defects Detected. Component is safe."
                        st.success(f"**STATUS: PASS**\n\n{reason}")
                    elif "Status: FAIL" in ai_output:
                        status = "FAIL"
                        reason = ai_output.split("-")[-1].strip() if "-" in ai_output else ai_output
                        st.error(f"**STATUS: FAIL**\n\n❌ Defect Found: {reason}")
                    else:
                        status = "ERROR"
                        reason = ai_output
                        st.error(f"Analysis Failed: {reason}")
                    
                    results_data.append({
                        "File": uploaded_file.name,
                        "Status": status,
                        "Reason": reason
                    })
                    
                    # Safety Gap
                    time.sleep(5)

        # 4. Final Summary
        st.divider()
        st.subheader("📋 Final Report Summary")
        if results_data:
            df = pd.DataFrame(results_data)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Items", len(df))
            m2.metric("Passed", len(df[df["Status"] == "PASS"]))
            m3.metric("Defective", len(df[df["Status"] == "FAIL"]))

            def highlight_row(row):
                if row['Status'] == 'PASS':
                    return ['background-color: #d4edda; color: black'] * len(row)
                elif row['Status'] == 'FAIL':
                    return ['background-color: #f8d7da; color: black'] * len(row)
                else:
                    return ['color: black'] * len(row)

            st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

else:
    st.info("👆 Upload photos to start inspection.")