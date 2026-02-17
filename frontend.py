import streamlit as st
import requests
import pandas as pd
import PyPDF2
import docx
from pathlib import Path

# backend URL (fastapi server)
BACKEND_URL = "http://localhost:8000/summarize"

# text limit for CPU processing (to ensure it doesn't take too long) - if the text exceeds this, it will be truncated with a warning.

MAX_CHARS = 30000 

st.set_page_config(layout="wide", page_title="On-Prem AI Summarizer")

# CSS for styling
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1E88E5; text-align: center; margin-bottom: 20px;}
    .stButton>button {width: 100%; border-radius: 5px; height: 50px; font-size: 20px;}
    .status-box {padding: 10px; border-radius: 5px; background-color: #e8f5e9; border: 1px solid #c8e6c9;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📄 Secure On-Prem Document Summarizer</div>', unsafe_allow_html=True)

#  text extraction function (with early stopping for long documents)
def extract_text(file):
    """
    Extract text from uploaded file (PDF, DOCX, TXT).
    For PDFs, it will skip images and only extract text. 
    If the extracted text exceeds MAX_CHARS, 
    it will stop and add a note about truncation to ensure the summarization process remains efficient on CPU.
    """
    text = ""
    try:
        ext = Path(file.name).suffix.lower()
        
        if ext == ".pdf":
            reader = PyPDF2.PdfReader(file)
            # extract text page by page to allow for early stopping if the document is too long
            for i, page in enumerate(reader.pages):
                content = page.extract_text()
                if content:
                    text += content + "\n"
                
                # if the accumulated text exceeds the limit, stop and add a note about truncation
                if len(text) > MAX_CHARS:
                    text += "\n...(Text truncated for speed)..."
                    break
                    
        elif ext == ".docx":
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
                if len(text) > MAX_CHARS:
                    text += "\n...(Text truncated for speed)..."
                    break
                    
        elif ext == ".txt":
            content = file.read().decode("utf-8")
            text = content[:MAX_CHARS] 

    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None
        
    return text

# sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    # select mode (single summary vs model comparison)
    mode = st.radio("Analysis Mode", ["Single Summary", "Model Matrix (Comparison)"])
    
    st.markdown("---")
    st.info(f"⚡ Speed Optimization: ON\nMax text length limited to {MAX_CHARS} chars to ensure <5min response on CPU.")

# main content area

# file uploader (step 1) - this will trigger text extraction immediately upon file upload.
uploaded_file = st.file_uploader("1️⃣ Upload Document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    # extract text from the uploaded file
    text = extract_text(uploaded_file)
    
    if text:
        st.success(f"✅ File loaded successfully! ({len(text)} characters extracted)")
        
        # summary type and model selection
        col1, col2 = st.columns(2)
        
        with col1:
            summary_type = st.selectbox(
                "2️⃣ Select Summary Type", 
                ["comprehensive", "executive", "bullet_points"]
            )
            
        with col2:
            # model selection will only be shown in single summary mode, in matrix mode we will run both models automatically for comparison.
            if mode == "Single Summary":
                selected_model = st.selectbox("3️⃣ Select Model", ["llama3.2", "phi3"])
            else:
                st.info("3️⃣ Matrix Mode: Comparing 'llama3.2' vs 'phi3'")

        st.markdown("---")

        # run analysis button
        if st.button("🚀 Run Analysis", type="primary"):
            
            # single summary mode
            if mode == "Single Summary":
                with st.spinner(f"Running analysis with {selected_model}... (Please wait)"):
                    try:
                        resp = requests.post(BACKEND_URL, json={
                            "text": text, 
                            "model_name": selected_model, 
                            "summary_type": summary_type
                        })
                        
                        if resp.status_code == 200:
                            res = resp.json()
                            st.markdown("### 📝 Summary Result")
                            st.write(res.get("summary"))
                            
                            # 시간 및 성능 지표 표시
                            st.markdown(f"""
                            <div class="status-box">
                                ⏱️ Time Taken: <b>{res.get('time')} seconds</b><br>
                                🤖 Model Used: {res.get('model')}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error("Backend Error. Please check if run_app.py is running.")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

            # model comparison matrix mode
            else:
                st.subheader("📊 Model Performance Matrix")
                models = ["llama3.2", "phi3"]
                results = []
                
                # process each model and update progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                cols = st.columns(len(models))
                
                for idx, model_name in enumerate(models):
                    with cols[idx]:
                        status_text.text(f"Processing with {model_name}...")
                        try:
                            resp = requests.post(BACKEND_URL, json={
                                "text": text, 
                                "model_name": model_name, 
                                "summary_type": summary_type
                            })
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                results.append({
                                    "Model": model_name,
                                    "Time (s)": data.get("time"),
                                    "Preview": data.get("summary")[:100] + "..."
                                })
                                st.success(f"{model_name} Done! ({data.get('time')}s)")
                                with st.expander(f"See Full Summary ({model_name})"):
                                    st.write(data.get("summary"))
                            else:
                                st.error(f"{model_name} Failed")
                        except Exception as e:
                            st.error(f"Connection Error: {e}")
                    
                    progress_bar.progress((idx + 1) / len(models))
                
                status_text.text("Analysis Complete!")
                
                # display results in a table
                if results:
                    st.markdown("### ⚡ Performance Comparison")
                    st.table(pd.DataFrame(results))

    else:
        st.error("Failed to extract text. The file might be empty or scanned (images only).")
