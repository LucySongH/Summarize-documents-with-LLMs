# Summarize Documents with LLMs — On-Premise Document Summarizer

> AI-powered document summarization that runs **fully on your machine**.  
> No internet required after setup. Your documents never leave your computer.

---

## Overview

Summarize Documents with LLMs is a year capstone project developed at Auckland University of Technology (AUT) in collaboration with **Pingar**.

The system allows users to upload documents and generate AI-powered summaries using locally running large language models (LLMs) via [Ollama](https://ollama.com). All processing happens on-device (no cloud APIs, no data transmission, no GPU required).

---

## Features

- **Multi-format support** - PDF, DOCX, PPTX, XLSX, CSV, TXT, MD, HTML, PY
- **Multi-model comparison** - llama3.2, phi3, gemma2:2b side by side
- **Non-blocking job queue** - upload multiple files, process in background
- **Model Matrix** - compare all model × summary type combinations at once
- **Quality metrics** - Flesch readability, word count, topic identification
- **Export results** - download summaries as `.txt` or matrix results as `.xlsx`
- **Fully offline** - works with no internet after initial model download

---

## Architecture

```
run_app.py
    ├── backend.py      FastAPI server (port 8000)
    │       └── job_queue.py    Async job queue (asyncio)
    │               └── Ollama  Local LLM server (port 11434)
    └── frontend.py     Streamlit UI (port 8501)
            └── evaluation.py   Quality metrics
```

---

## File Structure

```
DocSum/
├── backend.py          FastAPI backend - summarization requests,
│                       prompt engineering, Ollama REST API calls
├── frontend.py         Streamlit frontend - 3 tabs: Summarize, Model Matrix, History
├── job_queue.py        Async job queue - non-blocking background processing
├── evaluation.py       Quality metrics - readability, word count, topic check
├── run_app2.py          One-command launcher (starts backend + frontend)
└── requirements2.txt    Python dependencies
```

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running
- 8 GB RAM minimum (16 GB recommended)

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/docsum.git
cd docsum
```

**2. Install Python dependencies**
```bash
pip install -r requirements.txt
```

**3. Install Ollama**

Download from https://ollama.com/download and install for your OS.

**4. Pull AI models**
```bash
ollama pull llama3.2
ollama pull phi3
ollama pull gemma2:2b
```

---

## Running the App

```bash
python run_app.py
```

Then open your browser at:

```
http://localhost:8501
```

---

## How to Use

### Summarize Tab
1. Upload one or more documents (drag & drop or multi-select)
2. Choose a summary type:
   - **Comprehensive**: full detailed summary
   - **Executive**: short, decision-focused
   - **Bullet Points**: key points as a list
3. Select a model (`llama3.2` recommended)
4. Click **Run All**
5. Download results as `.txt`

### 📊 Model Matrix Tab
1. Upload a test document
2. Select models and summary types to compare
3. Click **Run Matrix Experiment**
4. View results side by side
5. Export to `.xlsx`

### 📜 History Tab
- View all jobs submitted in the current session
- Expand any entry to read the full summary

---

## Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-layer only (no scanned/image PDFs) |
| Word | `.docx` | |
| PowerPoint | `.pptx` | Extracts text per slide |
| Excel | `.xlsx`, `.xls` | Header-value extraction via pandas |
| CSV | `.csv` | |
| Text | `.txt` | |
| Markdown | `.md` | |
| HTML | `.html` | Tags stripped via BeautifulSoup |
| Python | `.py` | |

---

## AI Models

| Model | Size | Best For |
|-------|------|----------|
| `llama3.2` | ~2 GB | Best overall quality ⭐ recommended |
| `phi3` | ~2.3 GB | Fast, good for most documents |
| `gemma2:2b` | ~1.7 GB | Fastest, best for short documents |

---

## Prompt Architecture

DocSum uses a model-specific prompt builder (`build_prompt()` in `backend.py`) with shared grounding rules applied to all models:

- **SHARED_RULES**: strict grounding, no external knowledge, no hallucinated numbers
- **Phi3**: native `<|system|>` tag format
- **Gemma2**: explicit no-conversation instruction
- **Llama3.2**: standard format

Five prompt types: `comprehensive`, `executive`, `bullet_points`, `html_code`, `excel`.  
File-specific prompts are auto-selected based on file extension.

---

## Evaluation Results (Iterations 1 & 2)

| Model | v1 Avg | v2 Avg | Change | Good Rate (≥7) v2 |
|-------|--------|--------|--------|-------------------|
| llama3.2 | 5.53 | 7.04 | ↑ +1.51 | 72% |
| phi3 | 5.03 | 6.17 | ↑ +1.14 | 71% |
| gemma2:2b | 6.07 | 6.50 | ↑ +0.43 | 73% |

**llama3.2** ranked first on both ROUGE-L and BERTScore F1, winning 13/15 documents in Iteration 2.

---

## Known Limitations

| Model | Issue |
|-------|-------|
| phi3 | Converts billion-scale figures to millions |
| phi3 | Empty response on bullet_points for Excel input |
| gemma2:2b | Chatbot-style endings despite explicit rules |
| gemma2:2b | Shallow coverage on technical documents |
| All models | Some hallucination on structured/numerical data |

---

## Deployment

The system uses a local deployment approach for optimal performance on CPU-only machines.
Go to the Docker Folder.
**Windows**

Install Python - check "Add Python to PATH"
Install Ollama
Run install.bat (first time only - downloads AI models)
Run start.bat to launch the app

**Mac / Linux**

Install Python
Install Ollama
Run ./install.sh (first time only)
Run ./start.sh to launch the app

Then open: http://localhost:8501

---

## Team

| Name | Role |
|------|------|
| Lucy (Hyangrim Song) | Developer |
| Syed Abbas Ali | Document Collection & Baseline Summaries |
| Caitlin Howse | Automated Evaluation (ROUGE-L, BERTScore) |
| Yu Gu | Human Rubric Scoring & Documentation |

**Supervisor:** Yanbin  
**Client:** Pingar  
**Institution:** Auckland University of Technology (AUT)

---

## License

This project was developed as part of an AUT academic capstone project for Pingar.
