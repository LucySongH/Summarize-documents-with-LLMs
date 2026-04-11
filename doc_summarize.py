# doc_summarize.py — minimal, safe, Streamlit-compatible

from pathlib import Path
import os
import requests
import PyPDF2
import docx

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

# -------------------------------
# Ollama config & helper
# -------------------------------
FALLBACK_MODELS = ["llama3.2:3b", "llama3.1:8b", "llama2:7b"]
OLLAMA_BASE = "http://127.0.0.1:11434"

def get_llm():
    """Return a locally available Ollama LLM, or raise a clear error."""
    try:
        resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        resp.raise_for_status()
        have = {m.get("name") for m in resp.json().get("models", [])}
    except Exception as e:
        raise RuntimeError(
            "Ollama server not running.\n"
            "Open a new PowerShell and run:\n"
            "  ollama serve\n"
            "Then pull a model, e.g.:\n"
            "  ollama pull llama3.2:3b"
        ) from e
    for m in FALLBACK_MODELS:
        if m in have:
            return Ollama(model=m, base_url=OLLAMA_BASE), m
    raise RuntimeError(
        "No local model found. Run one of:\n"
        "  ollama pull llama3.2:3b\n"
        "  ollama pull llama3.1:8b\n"
        "  ollama pull llama2:7b"
    )

# -------------------------------
# Text extraction
# -------------------------------
def extract_text_from_pdf(file_obj) -> str | None:
    try:
        reader = PyPDF2.PdfReader(file_obj)
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except Exception:
        return None

def extract_text_from_docx(file_obj) -> str | None:
    try:
        doc = docx.Document(file_obj)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return None

def extract_text_from_txt(file_obj) -> str | None:
    try:
        return file_obj.read().decode("utf-8", errors="ignore")
    except Exception:
        return None

def extract_text(uploaded_file) -> str | None:
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(uploaded_file)
    if suffix == ".docx":
        return extract_text_from_docx(uploaded_file)
    if suffix == ".txt":
        return extract_text_from_txt(uploaded_file)
    return None

# -------------------------------
# Summarization
# -------------------------------
def build_prompt(text: str, summary_type: str) -> str:
    if summary_type == "brief":
        template = "Summarize the following document in 2–3 sentences:\n\n{text}\n\nSummary:"
    elif summary_type == "key_points":
        template = "Extract 5–7 key bullet points from the document:\n\n{text}\n\nKey points:"
    else:
        template = "Provide a 300–500 word comprehensive summary of the document:\n\n{text}\n\nSummary:"
    return ChatPromptTemplate.from_template(template).format(text=text[:15000])  # simple truncation guard

def summarize_text(text: str, summary_type: str = "comprehensive") -> str:
    llm, model_id = get_llm()
    prompt = build_prompt(text, summary_type)
    result = llm.invoke(prompt)
    return result if isinstance(result, str) else str(result)

def summarize_document(uploaded_file, summary_type: str = "comprehensive") -> str:
    """High-level helper: extract text then summarize."""
    text = extract_text(uploaded_file)
    if not text:
        raise ValueError("Failed to extract text from the uploaded file.")
    return summarize_text(text, summary_type)

# -------------------------------
# Optional: CLI quick test
# -------------------------------
if __name__ == "__main__":
    # Minimal manual test (expects a path arg)
    import sys
    if len(sys.argv) < 2:
        print("Usage: python doc_summarize.py <file_path> [comprehensive|brief|key_points]")
        raise SystemExit(1)
    path = Path(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) >= 3 else "comprehensive"
    with open(path, "rb") as f:
        out = summarize_document(type("U", (), {"name": path.name, "read": f.read, "__iter__": lambda s: iter(())})(), mode)  # quick hack for interface
    os.makedirs("evidence/outputs", exist_ok=True)
    out_path = Path("evidence/outputs/summary_cli.txt")
    out_path.write_text(out, encoding="utf-8")
    print(f"Saved summary to {out_path}")

