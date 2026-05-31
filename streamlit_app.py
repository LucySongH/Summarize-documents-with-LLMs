import streamlit as st
import PyPDF2, docx, os, tempfile, requests
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

# =========================
# Page config & styles
# =========================
st.set_page_config(page_title="Document Summarizer", page_icon="📄", layout="wide")
st.markdown("""
<style>
.main-header {font-size:2.2rem;font-weight:700;text-align:center;color:#1f77b4;margin:1rem 0;}
.sub-header {font-size:1.05rem;text-align:center;color:#666;margin-bottom:1.2rem;}
</style>
""", unsafe_allow_html=True)

# =========================
# Ollama setup (auto-fallback)
# =========================
FALLBACK_MODELS = ["llama3.2:3b", "llama3.1:8b", "llama2:7b"]
OLLAMA_BASE = "http://127.0.0.1:11434"

@st.cache_resource
def initialize_model():
    """Connect to local Ollama, pick the first available model from FALLBACK_MODELS."""
    try:
        resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        resp.raise_for_status()
    except Exception:
        st.error("❌ Ollama server not running.")
        st.info("Open a NEW PowerShell and run:\n  ollama serve\nThen pull a model, e.g.:\n  ollama pull llama3.2:3b")
        st.stop()
    have = {m.get("name") for m in resp.json().get("models", [])}
    for m in FALLBACK_MODELS:
        if m in have:
            return Ollama(model=m, base_url=OLLAMA_BASE), m
    st.error("❌ No local model found.")
    st.info("Run one of:\n  ollama pull llama3.2:3b\n  ollama pull llama3.1:8b\n  ollama pull llama2:7b")
    st.stop()

# =========================
# Helpers: extract text
# =========================
def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF: {e}"); return None

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        st.error(f"Error reading DOCX: {e}"); return None

def extract_text_from_txt(file):
    try:
        return file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        st.error(f"Error reading TXT: {e}"); return None

def extract_text(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".pdf":   return extract_text_from_pdf(uploaded_file)
    if suffix == ".docx":  return extract_text_from_docx(uploaded_file)
    if suffix == ".txt":   return extract_text_from_txt(uploaded_file)
    st.error(f"Unsupported file format: {suffix}"); return None

# =========================
# UI
# =========================
st.markdown('<div class="main-header">📄 Document Summarizer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your document and get an AI-powered summary instantly!</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    summary_type = st.selectbox(
        "Summary Type", ["comprehensive", "brief", "key_points"],
        format_func=lambda x: x.replace("_", " ").title()
    )
    st.header("🤖 Model Status")
    llm, model_id = initialize_model()
    st.success(f"Model ready: {model_id}")
    st.caption("Formats: PDF, DOCX, TXT (≤200MB)")

uploaded = st.file_uploader("📁 Upload Document", type=["pdf", "docx", "txt"])
gen = st.button("Generate Summary", type="primary", use_container_width=True, disabled=uploaded is None)

if uploaded:
    st.write({
        "Filename": uploaded.name,
        "File size (KB)": round(uploaded.size/1024, 2),
        "File type": uploaded.type
    })

if gen and uploaded:
    with st.spinner(f"Processing file: {uploaded.name}"):
        text = extract_text(uploaded)
    if not text:
        st.stop()
    st.success(f"✅ Extracted {len(text)} characters of text")

    # prompt
    if summary_type == "brief":
        template = "Summarize the following document in 2–3 sentences:\n\n{text}\n\nSummary:"
    elif summary_type == "key_points":
        template = "Extract 5–7 key bullet points from the document:\n\n{text}\n\nKey points:"
    else:
        template = "Provide a 300–500 word comprehensive summary of the document:\n\n{text}\n\nSummary:"

    prompt = ChatPromptTemplate.from_template(template).format(text=text[:15000])  # 防止超长
    try:
        with st.spinner("Generating summary with AI..."):
            result = llm.invoke(prompt)   # LangChain LLM接口
        st.subheader("🧾 Summary")
        st.write(result)
        # 保存一份用于证据
        os.makedirs("evidence/outputs", exist_ok=True)
        with open(os.path.join("evidence/outputs", "summary.txt"), "w", encoding="utf-8") as f:
            f.write(result if isinstance(result, str) else str(result))
        st.toast("Saved to evidence/outputs/summary.txt")
    except Exception as e:
        st.error(f"Error generating summary: {e}")


    
