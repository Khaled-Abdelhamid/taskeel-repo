# Tashkeel API

This API provides a way to run inference over the two Arabic diacritization (tashkeel) models in the CATT project.

## Models

Two models are supported:

- **ED (Encoder-Decoder)**: A transformer model using an encoder-decoder architecture
- **EO (Encoder-Only)**: A transformer model using an encoder-only architecture

## Setup

The API requires the dependencies already listed in the project's pyproject.toml. The models need to be in the `models/` directory at the root of the project.

## Running the API

### Start the API Server

```bash
./start_api.sh
```

This will start the FastAPI server on port 8000.

### Start the Web UI

```bash
./start_web_ui.sh
```

This will start the Streamlit web interface that connects to the API.

## API Endpoints

### GET /

Returns the API status and available models.

### POST /tashkeel

Add diacritics to a single text.

Request body:

```json
{
  "text": "النص العربي بدون تشكيل",
  "model_type": "ed",  // or "eo"
  "clean_text": true
}
```

### POST /batch-tashkeel

Add diacritics to multiple texts.

Request body:

```json
{
  "texts": ["النص الأول", "النص الثاني"],
  "model_type": "ed",  // or "eo"
  "clean_text": true
}
```

## Using with Python

```python
import requests

# Add diacritics to a single text
response = requests.post(
    "http://localhost:8000/tashkeel",
    json={
        "text": "النص العربي بدون تشكيل",
        "model_type": "ed",
        "clean_text": True
    }
)
result = response.json()
print(result["tashkeel"])
```
