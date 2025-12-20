import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")

st.title("🏭 AI Quality Inspector Pro")
st.markdown("### Universal Defect Detection System (Batch Processing)")
st.caption("Powered by Google Gemini AI")

# 2. Sidebar - Authentication & Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Connected to Server Key")
    else:
        api_key = st.text_input("Enter Google API Key", type="password")

# 3. Core Logic
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Smart Fallback Mechanism (To handle 404 Errors)
        try:
            # First Choice: Flash (Fastest)
            model = genai.GenerativeModel("gemini-1.5-flash")
        except:
            try:
                 # Second Choice: Pro (More Stable)
                model = genai.GenerativeModel("gemini-1.5-pro")
            except:
                # Last Resort: Pro Vision (Legacy)
                model = genai.GenerativeModel("gemini-pro-vision")

        # System Prompt (Defines the Role)
        system_prompt = """
        You are a Senior Quality Control Engineer. Analyze this industrial component image.
        1. Detect any visible defects (rust, cracks, deformation, discoloration, missing parts).
        2. If NO defect is found, strictly output: "Status: PASS".
        3. If a defect is found, output: "Status: FAIL" followed by a concise reason (max 15 words).
        
        Important: Output MUST start with 'Status: PASS' or 'Status: FAIL'.
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
            
            # Start Button
            if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
                
                for index, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Inspecting Item {index + 1}/{len(uploaded_files)}...")
                    progress_bar.progress((index + 1) / len(uploaded_files))
                    
                    try:
                        image = Image.open(uploaded_file)
                        
                        # Universal Call Method (Works on ALL Models)
                        # We send prompt + image together to avoid version conflicts
                        response = model.generate_content([system_prompt, image])
                        ai_output = response.text.strip()
                        
                        # Parsing Logic
                        if "Status: PASS" in ai_output:
                            status = "PASS"
                            reason = "Clean Component / No Defects"
                        else:
                            status = "FAIL"
                            reason = ai_output.split("-")[-1].strip() if "-" in ai_output else ai_output
                        
                        results_data.append({
                            "File Name": uploaded_file.name,
                            "Status": status,
                            "Reason/Analysis": reason
                        })
                        
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")

                # 5. Final Dashboard
                st.divider()
                
                if results_data:
                    df = pd.DataFrame(results_data)
                    
                    col1, col2, col3 = st.columns(3)
                    total = len(df)
                    passed = len(df[df["Status"] == "PASS"])
                    failed = len(df[df["Status"] == "FAIL"])
                    
                    col1.metric("Total Items", total)
                    col2.metric("✅ Passed", passed)
                    col3.metric("❌ Defective", failed)
                    
                    st.markdown("### 📋 Detailed Inspection Log")
                    
                    def highlight_status(val):
                        color = '#d4edda' if val == 'PASS' else '#f8d7da'
                        return f'background-color: {color}; color: black'

                    # Safe DataFrame rendering
                    st.dataframe(df.style.map(highlight_status, subset=['Status']), use_container_width=True)
                    
                    st.success("✅ Inspection Completed!")

        else:
            st.info("👆 Upload multiple images to simulate a batch check.")

    except Exception as e:
        st.error(f"Configuration Error: {e}")

else:
    st.warning("⚠️ Enter API Key to start.")