import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# 1. Page Configuration (Professional Look)
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")

st.title("🏭 AI Quality Inspector Pro")
st.markdown("### Universal Defect Detection System (Batch Processing)")
st.caption("Powered by Google Gemini AI")

# 2. Sidebar - Authentication
with st.sidebar:
    st.header("⚙️ Settings")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Connected to Server Key")
    else:
        api_key = st.text_input("Enter Google API Key", type="password")

# --- SMART MODEL LOADER ---
def get_gemini_response(model_name, prompt, image):
    """Try to get response, handle errors automatically."""
    model = genai.GenerativeModel(model_name)
    response = model.generate_content([prompt, image])
    return response.text.strip()

# 3. Core Logic
if api_key:
    genai.configure(api_key=api_key)
    
    # System Prompt
    system_prompt = """
    Act as a Senior QA Engineer. Analyze this image.
    1. Detect defects (rust, crack, damage).
    2. If NO defect: Output "Status: PASS".
    3. If defect found: Output "Status: FAIL - [Reason]".
    """

    # 4. Batch Image Uploader
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
            
            for index, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing Item {index + 1}/{len(uploaded_files)}...")
                progress_bar.progress((index + 1) / len(uploaded_files))
                
                try:
                    image = Image.open(uploaded_file)
                    
                    # --- AUTO-SWITCH LOGIC ---
                    # Pehle Flash try karega, fail hua to Pro Vision
                    try:
                        ai_output = get_gemini_response("gemini-1.5-flash", system_prompt, image)
                    except:
                        try:
                            ai_output = get_gemini_response("gemini-1.5-flash-latest", system_prompt, image)
                        except:
                            ai_output = get_gemini_response("gemini-pro-vision", system_prompt, image)

                    # Parsing Logic
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
                    st.error(f"Failed {uploaded_file.name}: {e}")

            # 5. Final Dashboard
            st.divider()
            if results_data:
                df = pd.DataFrame(results_data)
                
                col1, col2, col3 = st.columns(3)
                total = len(df)
                passed = len(df[df["Status"] == "PASS"])
                failed = len(df[df["Status"] == "FAIL"])
                
                col1.metric("Total", total)
                col2.metric("✅ Passed", passed)
                col3.metric("❌ Defective", failed)
                
                # Styling
                def highlight_status(val):
                    return 'background-color: #d4edda' if val == 'PASS' else 'background-color: #f8d7da'

                st.dataframe(df.style.map(highlight_status, subset=['Status']), use_container_width=True)
                st.success("✅ Inspection Completed!")

    else:
        st.info("👆 Upload multiple images to check quality.")

else:
    st.warning("⚠️ Enter API Key to start.")