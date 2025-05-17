from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from models.models import get_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Tashkeel API",
    description="API for adding diacritics (tashkeel) to Arabic text using neural models",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Can be set to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Input/Output models
class TashkeelRequest(BaseModel):
    text: str
    model_type: Optional[str] = "ed"  # "ed" or "eo"
    clean_text: Optional[bool] = True


class BatchTashkeelRequest(BaseModel):
    texts: List[str]
    model_type: Optional[str] = "ed"  # "ed" or "eo"
    clean_text: Optional[bool] = True


class TashkeelResponse(BaseModel):
    tashkeel: str


class BatchTashkeelResponse(BaseModel):
    tashkeels: List[str]


class StatusResponse(BaseModel):
    status: str
    available_models: List[str]


# Initialize models in the background
def load_models_in_background():
    """Initialize both models in the background"""
    try:
        ed_model = get_model("ed")
        logger.info("ED model loaded successfully")
        eo_model = get_model("eo")
        logger.info("EO model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Run when the API starts"""
    # Start loading models in the background
    background_tasks = BackgroundTasks()
    background_tasks.add_task(load_models_in_background)


@app.get("/", response_model=StatusResponse)
async def status():
    """Get API status"""
    return {
        "status": "running",
        "available_models": ["ed", "eo"],
    }


@app.post("/tashkeel", response_model=TashkeelResponse)
async def tashkeel(request: TashkeelRequest):
    """
    Add diacritics (tashkeel) to a single Arabic text

    - **text**: Input text without diacritics
    - **model_type**: Model to use ('ed' or 'eo'), default is 'ed'
    - **clean_text**: Whether to clean non-Arabic characters, default is True
    """
    try:
        model = get_model(request.model_type)
        result = model.tashkeel(
            request.text, clean_text=request.clean_text, verbose=False
        )
        return {"tashkeel": result}
    except Exception as e:
        logger.error(f"Error in tashkeel endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-tashkeel", response_model=BatchTashkeelResponse)
async def batch_tashkeel(request: BatchTashkeelRequest):
    """
    Add diacritics (tashkeel) to multiple Arabic texts

    - **texts**: List of input texts without diacritics
    - **model_type**: Model to use ('ed' or 'eo'), default is 'ed'
    - **clean_text**: Whether to clean non-Arabic characters, default is True
    """
    try:
        model = get_model(request.model_type)
        results = model.tashkeel(
            request.texts, clean_text=request.clean_text, verbose=True
        )
        return {"tashkeels": results}
    except Exception as e:
        logger.error(f"Error in batch-tashkeel endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
