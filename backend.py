"""
backend.py — FastAPI backend with Job Queue + Ollama (no langchain needed).
Changes from prototype:
  - Removed langchain dependency (direct requests to Ollama REST API)
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
AVAILABLE_MODELS = ["llama3.2", "phi3"]


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
            "num_predict": 500, # max output tokens
            "num_ctx": 4096,    # context window
        },
    }

    try:
        resp = http_requests.post(OLLAMA_URL, json=payload, timeout=300)
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
