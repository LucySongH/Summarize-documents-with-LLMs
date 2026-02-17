import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.llms import Ollama
import time
import logging

# logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Model registry
MODELS = {
    "llama3.2": None,  # lightweight, newer version
    "phi3": None,      # MS small model, good for quick summaries
    "llama2": None     # heavier, but more powerful, for detailed summaries
}

def load_model(model_name):
    """Load the specified model if not already loaded."""
    if MODELS.get(model_name) is None:
        logger.info(f"🔄 Loading model: {model_name}...")
        try:
            # keep_alive=-1m : keep the model loaded for 1 minute after last use to reduce latency on subsequent calls
            MODELS[model_name] = Ollama(model=model_name, keep_alive="-1m")
            logger.info(f"✅ Loaded {model_name}")
        except Exception as e:
            logger.error(f"❌ Error loading {model_name}: {e}")
            return None
    return MODELS[model_name]

class RequestData(BaseModel):
    text: str
    model_name: str
    summary_type: str

@app.post("/summarize")
async def summarize(data: RequestData):
    model = load_model(data.model_name)
    if not model:
        return {"error": f"Model {data.model_name} not found or failed to load."}
    
    # Prompt Engineering
    system_prompt = (
        "You are a professional analyst. "
        "First, identify the document type and purpose. "
        "Then, provide the summary. "
        "Avoid filler words."
    )
    
    instruction = ""
    if data.summary_type == "bullet_points":
        instruction = "Format: Bullet points."
    elif data.summary_type == "executive":
        instruction = "Format: Executive summary for management."
    
    full_prompt = f"{system_prompt}\n{instruction}\n\nDocument:\n{data.text}"
    
    start_time = time.time()
    try:
        response = model.invoke(full_prompt)
        duration = time.time() - start_time
        return {
            "summary": response,
            "time": round(duration, 2),
            "model": data.model_name
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
