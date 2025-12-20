import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="AI Quality Inspector Pro", page_icon="🏭", layout="wide")

st.title("🏭 AI Quality Inspector Pro")
st.markdown("### Universal Defect Detection System (Batch Processing)")
st.caption("Powered by Google Gemini 1.5 Flash")

# 2. Sidebar - Authentication & Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Secure API Key Handling
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Connected to Server Key")
    else:
        api_key = st.text_input("Enter Google API Key", type="password")
        st.caption("Enter your API key to proceed.")

# 3. Core Logic
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # System Prompt - Acting as a Senior QA Engineer
        system_prompt = """
        You are a Senior Quality Control Engineer. Analyze this industrial component image.
        1. Detect any visible defects (rust, cracks, deformation, discoloration, missing parts).
        2. If NO defect is found, strictly output: "Status: PASS".
        3. If a defect is found, output: "Status: FAIL" followed by a concise reason (max 15 words).
        
        Format example:
        Status: FAIL - Severe rust corrosion on the outer flange.
        """
        
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)

        # 4. Batch Image Uploader
        uploaded_files = st.file_uploader(
            "Upload Component Images (Batch Mode)", 
            type=["jpg", "png", "jpeg"], 
            accept_multiple_files=True
        )

        if uploaded_files:
            st.divider()
            st.subheader("🔍 Inspection Results")
            
            # List to store processing results
            results_data = []
            
            # UI Elements for progress
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Trigger Button
            if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
                
                for index, uploaded_file in enumerate(uploaded_files):
                    # Update User Interface
                    status_text.text(f"Inspecting Item {index + 1}/{len(uploaded_files)}...")
                    progress_bar.progress((index + 1) / len(uploaded_files))
                    
                    try:
                        # Load Image
                        image = Image.open(uploaded_file)
                        
                        # API Call
                        response = model.generate_content(image)
                        ai_output = response.text.strip()
                        
                        # Parse Response (Pass/Fail Logic)
                        if "Status: PASS" in ai_output:
                            status = "PASS"
                            reason = "Clean Component / No Defects"
                        else:
                            status = "FAIL"
                            # Extracting the reason after the hyphen
                            reason = ai_output.split("-")[-1].strip() if "-" in ai_output else ai_output
                        
                        # Append to results
                        results_data.append({
                            "File Name": uploaded_file.name,
                            "Status": status,
                            "Reason/Analysis": reason
                        })
                        
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")

                # 5. Final Dashboard & Analytics
                st.divider()
                status_text.text("Inspection Completed.")
                
                # Convert results to DataFrame
                df = pd.DataFrame(results_data)
                
                # Metrics Display
                col1, col2, col3 = st.columns(3)
                total = len(df)
                passed = len(df[df["Status"] == "PASS"])
                failed = len(df[df["Status"] == "FAIL"])
                
                col1.metric("Total Items Processed", total)
                col2.metric("✅ Passed Components", passed)
                col3.metric("❌ Defective Components", failed)
                
                # Detailed Data Table
                st.markdown("### 📋 Detailed Inspection Log")
                
                # Styling the dataframe for better visualization
                def highlight_status(val):
                    color = '#d4edda' if val == 'PASS' else '#f8d7da' # Light Green vs Light Red
                    return f'background-color: {color}; color: black'

             st.dataframe(df.style.map(highlight_status, subset=['Status']), use_container_width=True)