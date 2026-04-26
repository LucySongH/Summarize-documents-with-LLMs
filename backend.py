"""
backend.py — FastAPI backend with Job Queue + Ollama (no langchain needed).
Changes from prototype:
  - Removed langchain dependency (direct requests to Ollama REST API)
  - Added Job Queue via job_queue.py (non-blocking summarization)
  - Improved prompts: summary now starts with document type/purpose (Pascal feedback)
  - Added /job/{id} polling endpoint and /status endpoint
""""""
backend.py — FastAPI backend with Job Queue + Ollama (no langchain needed).

Changes from prototype:
  - Removed langchain dependency (direct requests to Ollama REST API)
  - Fixed keep_alive bug (-1m → -1)
  - Added Job Queue via job_queue.py (non-blocking summarization)
  - Improved prompts: summary now starts with document type/purpose (Pascal feedback)
  - Added /job/{id} polling endpoint and /status endpoint
"""

import asyncio
import logging
import requests as http_requests
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from job_queue import SummarizationQueue

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App + Queue 
app = FastAPI(title="On-Prem Document Summarizer API")
job_queue = SummarizationQueue()

OLLAMA_URL = "http://localhost:11434/api/generate"

# Model registry 
AVAILABLE_MODELS = ["llama3.2", "phi3", "gemma2:2b"]


# Prompt templates v2

SHARED_RULES = """
STRICT GROUNDING RULES — MUST FOLLOW:
- Use ONLY information explicitly stated in the document.
- Do NOT add examples, context, history, or any information from outside the document.
- Do NOT use proper nouns, names, bill numbers, or statistics not in the source text.
- If you are unsure whether something is in the document, OMIT it entirely.
 
NUMBER RULES — CRITICAL:
- ONLY use numbers that appear WORD FOR WORD in the document.
- Do NOT calculate, estimate, average, or derive any numbers yourself.
- Do NOT convert units (e.g. do not convert billions to millions or vice versa).
- Do NOT calculate growth rates, percentages, or trends — only state them if explicitly written.
- If a number is unclear or missing, write "data not specified" instead of guessing.
- COPY numbers exactly as they appear: same unit, same scale, same format.
 
RESTRICTION & EXCLUSION RULES:
- Prohibitions, restrictions, exclusions, and "must not" statements are MORE important than positive ones.
- Do NOT soften or omit negative constraints.
"""
 
def build_prompt(model_name: str, summary_type: str,
                 text: str, max_words: int) -> str:
    """
    Build a model-specific prompt.
    - Phi3  : uses <|system|> / <|user|> / <|assistant|> native tags
    - Gemma2: prepends hard no-conversation instruction
    - Others: standard format
    """
 
    tasks = {
        "comprehensive": (
            "1. Identify the document type (e.g. policy, report, financial, lecture).\n"
            "2. Start with: 'This document is a [type] about [main topic].'\n"
            f"3. Summarise all key information in {max_words} words or fewer.\n"
            "4. Do NOT add sections or content not in the source.\n"
            "5. Preserve all numbers, dates, restrictions, and exclusions."
        ),
        "executive": (
            "1. Identify the document type.\n"
            "2. First sentence: 'This [type] is about [core purpose].'\n"
            f"3. In {max_words} words or fewer: highlight critical decisions, findings, restrictions, and key numbers.\n"
            "4. If the document contains prohibitions or exclusions, they MUST appear in the summary."
        ),
        "bullet_points": (
            "1. First line: 'This document is a [type] about [topic].'\n"
            f"2. Write 5-8 bullet points using {max_words} words or fewer in total.\n"
            "3. Each bullet must be traceable to the source.\n"
            "4. Include all numbers, dates, limits, restrictions.\n"
            "5. Do NOT write bullets about topics not in the document."
        ),
        "html_code": (
            "1. IGNORE all HTML tags, attributes, and code syntax.\n"
            "2. First sentence: 'This document is a [type] about [main topic].'\n"
            f"3. Summarise the actual content in {max_words} words or fewer.\n"
            "4. Do NOT describe code structure or tag names."
        ),
        "excel": (
            "1. First sentence: 'This spreadsheet is about [main topic].'\n"
            "2. Identify what each sheet contains.\n"
            "3. Extract and preserve ALL numerical values, dates, totals, percentages.\n"
            "4. Describe key trends or comparisons visible in the data.\n"
            f"5. Use {max_words} words or fewer.\n"
            "6. Do NOT invent numbers not present in the data.\n"
            "7. If data is unclear, state that explicitly."
        ),
    }
 
    task = tasks.get(summary_type, tasks["comprehensive"])
    output_label = {
        "comprehensive": "Summary",
        "executive":     "Executive Summary",
        "bullet_points": "Key Points",
        "html_code":     "Summary",
        "excel":         "Summary",
    }.get(summary_type, "Summary")
 
    # ── Phi3 native format ─────────────────────────────────────────────────────
    if "phi3" in model_name.lower() or "phi-3" in model_name.lower():
        return (
            f"<|system|>\n"
            f"You are a precise document analyst. Output ONLY the summary. "
            f"Do NOT repeat instructions or continue the document.\n"
            f"{SHARED_RULES}<|end|>\n"
            f"<|user|>\n"
            f"TASK:\n{task}\n\n"
            f"DOCUMENT:\n{text}<|end|>\n"
            f"<|assistant|>\n"
            f"{output_label}:"
        )
 
    # ── Gemma2 format ──────────────────────────────────────────────────────────
    if "gemma" in model_name.lower():
        return (
            f"You are a document summariser. Your only job is to write a {output_label.lower()}.\n"
            f"RULES YOU MUST FOLLOW:\n"
            f"- Do NOT write questions.\n"
            f"- Do NOT write 'Let me know', 'Feel free', or any conversational phrases.\n"
            f"- Do NOT explain what you are doing.\n"
            f"- Output ONLY the {output_label.lower()} text and nothing else.\n"
            f"- Stop writing immediately after the summary is complete.\n\n"
            f"{SHARED_RULES}\n"
            f"TASK:\n{task}\n\n"
            f"DOCUMENT:\n{text}\n\n"
            f"{output_label} (output only, no questions, no commentary):\n"
        )
 
    # ── Default (Llama3.2 and others) ─────────────────────────────────────────
    return (
        f"You are a precise document analyst. "
        f"Output ONLY the {output_label.lower()}. Do NOT add commentary.\n\n"
        f"{SHARED_RULES}\n"
        f"TASK:\n{task}\n\n"
        f"DOCUMENT:\n{text}\n\n"
        f"{output_label}:"
    )

def summarize(text: str, model_name: str, summary_type: str) -> str:
    """
    Call Ollama REST API directly (no langchain).
    Blocking function — runs inside a thread via the queue worker.
    Uses model-specific prompt format to prevent injection and chatbot responses.
    """
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown model '{model_name}'. Available: {AVAILABLE_MODELS}")
 
    valid_types = ["comprehensive", "executive", "bullet_points", "html_code", "excel"]
    if summary_type not in valid_types:
        raise ValueError(f"Unknown summary type '{summary_type}'. Choose from: {valid_types}")
 
    # Dynamic word limit: 30% of source, min 100, max 800
    source_word_count = len(text.split())
    max_words = max(100, min(800, int(source_word_count * 0.3)))
 
    prompt = build_prompt(model_name, summary_type, text, max_words)
 
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "keep_alive": -1,
        "options": {
            "temperature": 0.3,
            "num_predict": 800,
            "num_ctx": 8000,
        },
    }
 
    try:
        resp = http_requests.post(OLLAMA_URL, json=payload, timeout=600)
        resp.raise_for_status()
        result = resp.json().get("response", "").strip()
        if not result:
            raise ValueError("Ollama returned an empty response.")
        return result
    except http_requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot connect to Ollama. Make sure it is running: ollama serve")
    except http_requests.exceptions.Timeout:
        raise RuntimeError("Ollama timed out (10 min limit). Try a shorter document or a smaller model like phi3 or gemma2:2b.")

# Startup

@app.on_event("startup")
async def startup():
    asyncio.create_task(job_queue.worker(summarize))
    logger.info("Queue worker started.")

# Request schema

class SummarizeRequest(BaseModel):
    text: str
    model_name: str = "llama3.2"
    summary_type: str = "comprehensive"

# Endpoints

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/models")
def list_models():
    """Return available models and whether they're pulled in Ollama."""
    available = []
    try:
        resp = http_requests.get("http://localhost:11434/api/tags", timeout=3)
        if resp.status_code == 200:
            pulled = [m["name"] for m in resp.json().get("models", [])]
            for m in AVAILABLE_MODELS:
                is_ready = any(p.startswith(m) for p in pulled)
                available.append({"name": m, "ready": is_ready})
    except Exception:
        available = [{"name": m, "ready": False} for m in AVAILABLE_MODELS]
    return {"models": available}


@app.post("/summarize")
async def submit_job(data: SummarizeRequest):
    """
    Submit a document for summarization.
    Returns a job_id immediately — poll /job/{job_id} for the result.
    """
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if data.model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Unknown model. Choose from: {AVAILABLE_MODELS}")
    VALID_TYPES = ["comprehensive", "executive", "bullet_points", "html_code", "excel"]
    if data.summary_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown summary type. Choose from: {VALID_TYPES}")
 
    job_id = await job_queue.submit(data.text, data.model_name, data.summary_type)
    return {"job_id": job_id, "status": "queued"}


@app.get("/job/{job_id}")
def get_job(job_id: str):
    """Poll the status and result of a submitted job."""
    job = job_queue.get_status(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job


@app.get("/status")
def queue_status():
    return job_queue.get_stats()

# Entry point

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

import asyncio
import logging
import requests as http_requests
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from job_queue import SummarizationQueue

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App + Queue 
app = FastAPI(title="On-Prem Document Summarizer API")
job_queue = SummarizationQueue()

OLLAMA_URL = "http://localhost:11434/api/generate"

# Model registry 
AVAILABLE_MODELS = ["llama3.2", "phi3", "gemma2:2b"]


# Prompt templates
# Pascal feedback: summary must ALWAYS start by stating what the document is
# about before going into details. Avoid over-emphasizing brand names/entities.

PROMPTS = {
    "comprehensive": (
        "You are a professional document analyst.\n\n"
        "RULES:\n"
        "1. Start with: 'This document is [type] about [main topic/purpose].'\n"
        "2. Summarize all key information clearly and concisely (300-400 words).\n"
        "3. Do not over-emphasize brand names or trademarks.\n"
        "4. Focus on substance: purpose, findings, arguments, or recommendations.\n\n"
        "Document:\n{text}\n\nSummary:"
    ),
    "executive": (
        "You are a senior business analyst writing for executives.\n\n"
        "RULES:\n"
        "1. First sentence: state what this document is and its core business purpose.\n"
        "2. Highlight the most critical decisions, findings, or recommendations.\n"
        "3. Be concise and action-oriented (150-200 words).\n\n"
        "Document:\n{text}\n\nExecutive Summary:"
    ),
    "bullet_points": (
        "You are a professional document analyst.\n\n"
        "RULES:\n"
        "1. First line: 'This document is [type] about [topic].'\n"
        "2. List 5-7 key points as bullet points.\n"
        "3. Each bullet must be a complete, informative sentence.\n"
        "4. Focus on purpose, key facts, and conclusions — not entity names.\n\n"
        "Document:\n{text}\n\nKey Points:"
    ),
}


def summarize(text: str, model_name: str, summary_type: str) -> str:
    """
    Call Ollama REST API directly (no langchain).
    Blocking function — runs inside a thread via the queue worker.
    """
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown model '{model_name}'. Available: {AVAILABLE_MODELS}")

    prompt_template = PROMPTS.get(summary_type, PROMPTS["comprehensive"])
    prompt = prompt_template.format(text=text)

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "keep_alive": -1,       # keep model loaded in Ollama between jobs
        "options": {
            "temperature": 0.3, # lower = more factual, less hallucination
            "num_predict": 800, # max output tokens
            "num_ctx": 8000,    # context window
        },
    }

    try:
        resp = http_requests.post(OLLAMA_URL, json=payload, timeout=600)
        resp.raise_for_status()
        result = resp.json().get("response", "").strip()
        if not result:
            raise ValueError("Ollama returned an empty response.")
        return result
    except http_requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot connect to Ollama. Make sure it is running: ollama serve")
    except http_requests.exceptions.Timeout:
        raise RuntimeError("Ollama timed out. Try a smaller model like phi3.")

# Startup

@app.on_event("startup")
async def startup():
    asyncio.create_task(job_queue.worker(summarize))
    logger.info("Queue worker started.")

# Request schema

class SummarizeRequest(BaseModel):
    text: str
    model_name: str = "llama3.2"
    summary_type: str = "comprehensive"

# Endpoints

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/models")
def list_models():
    """Return available models and whether they're pulled in Ollama."""
    available = []
    try:
        resp = http_requests.get("http://localhost:11434/api/tags", timeout=3)
        if resp.status_code == 200:
            pulled = [m["name"] for m in resp.json().get("models", [])]
            for m in AVAILABLE_MODELS:
                is_ready = any(p.startswith(m) for p in pulled)
                available.append({"name": m, "ready": is_ready})
    except Exception:
        available = [{"name": m, "ready": False} for m in AVAILABLE_MODELS]
    return {"models": available}


@app.post("/summarize")
async def submit_job(data: SummarizeRequest):
    """
    Submit a document for summarization.
    Returns a job_id immediately — poll /job/{job_id} for the result.
    """
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if data.model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Unknown model. Choose from: {AVAILABLE_MODELS}")
    if data.summary_type not in PROMPTS:
        raise HTTPException(status_code=400, detail=f"Unknown summary type. Choose from: {list(PROMPTS.keys())}")

    job_id = await job_queue.submit(data.text, data.model_name, data.summary_type)
    return {"job_id": job_id, "status": "queued"}


@app.get("/job/{job_id}")
def get_job(job_id: str):
    """Poll the status and result of a submitted job."""
    job = job_queue.get_status(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job


@app.get("/status")
def queue_status():
    return job_queue.get_stats()

# Entry point

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
