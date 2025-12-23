import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import time

# --- 1. Page Configuration ---
st.set_page_config(page_title="Quality Inspector AI", page_icon="🏭", layout="wide")
st.title("🏭 Quality Inspector AI")
st.markdown("### Automated Defect Detection System")
st.write("Upload images of mechanical parts to inspect for defects (Rust, Cracks, etc.)")

# --- 2. API Key Authentication ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("🚨 Error: API Key not found. Please add GOOGLE_API_KEY to Streamlit Secrets.")
    st.stop()

# --- 3. Robust Analysis Function (The Fix) ---
def analyze_image_with_fallback(image, prompt):
    """
    Tries gemini-1.5-flash first. 
    If it gets a 404 error, it immediately switches to gemini-pro-vision.
    """
    # Priority 1: The Modern Model
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, image])
        return response.text.strip(), "gemini-1.5-flash"
    except Exception as e:
        # If 1.5 fails (404 Not Found), try Priority 2: The Stable Backup
        try:
            time.sleep(1) # Brief pause
            model = genai.GenerativeModel("gemini-pro-vision")
            response = model.generate_content([prompt, image])
            return response.text.strip(), "gemini-pro-vision (Backup)"
        except Exception as e2:
            return None, str(e) # Return the original error if both fail

# Sidebar Information
with st.sidebar:
    st.header("System Status")
    st.success("✅ Server Online")
    st.info("🤖 Mode: Auto-Failover (Flash → Pro Vision)")

# --- 4. Main Application Loop ---
uploaded_files = st.file_uploader("Upload Component Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    st.info("ℹ️ Note: Analysis includes a safety delay to prevent API blocking.")
    
    if st.button(f"Start Inspection for {len(uploaded_files)} Items"):
        
        st.divider()
        st.subheader("🔍 Inspection Results")
        
        inspection_results = []
        
        for file in uploaded_files:
            col1, col2 = st.columns([1, 2])
            
            # Display Image
            img = Image.open(file)
            col1.image(img, caption=file.name, use_container_width=True)
            
            with col2:
                with st.spinner("Analyzing component..."):
                    # Prompt Engineering
                    prompt = """
                    Analyze this industrial image for defects (rust, cracks, damage).
                    Output strictly in this format:
                    Status: PASS
                    OR
                    Status: FAIL - [Reason]
                    """
                    
                    # CALL THE ROBUST FUNCTION
                    text, used_model = analyze_image_with_fallback(img, prompt)
                    
                    if text:
                        # Logic to parse the result
                        if "Status: PASS" in text:
                            status = "PASS"
                            reason = "✅ No defects detected. Component is safe."
                            st.success(f"**STATUS: PASS**")
                            st.caption(reason)
                            
                        elif "Status: FAIL" in text:
                            status = "FAIL"
                            reason = text.split("-")[-1].strip() if "-" in text else text
                            st.error(f"**STATUS: FAIL**")
                            st.markdown(f"**Defect:** {reason}")
                            
                        else:
                            status = "REVIEW"
                            reason = text
                            st.warning(f"⚠️ Manual Review Needed: {text}")
                            
                        # Save result
                        inspection_results.append({
                            "File Name": file.name,
                            "Status": status,
                            "Details": reason,
                            "Model Used": used_model
                        })
                    else:
                        st.error(f"Failed to analyze. Error: {used_model}") # used_model holds error msg here
                        inspection_results.append({
                            "File Name": file.name,
                            "Status": "ERROR",
                            "Details": "API Connection Failed",
                            "Model Used": "None"
                        })
                    
                    # Safety Delay
                    time.sleep(12)

        # --- 5. Final Report ---
        if inspection_results:
            st.divider()
            st.subheader("📋 Final Report Summary")
            
            df = pd.DataFrame(inspection_results)
            
            def highlight_status(row):
                if row['Status'] == 'PASS':
                    return ['background-color: #d1e7dd; color: black'] * len(row)
                elif row['Status'] == 'FAIL':
                    return ['background-color: #f8d7da; color: black'] * len(row)
                else:
                    return ['color: black'] * len(row)

            st.dataframe(df.style.apply(highlight_status, axis=1), use_container_width=True)