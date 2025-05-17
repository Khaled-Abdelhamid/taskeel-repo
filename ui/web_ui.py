import streamlit as st
import requests
from stqdm import stqdm
from ui.text_preprocessor import split_and_chunk_text

st.set_page_config(page_title="Tashkeel Web UI", page_icon="🔤", layout="wide")

st.title("🔤 Arabic Diacritization (Tashkeel)")

# Set the API URL
api_url = "http://localhost:8000"

# Set maximum chunk size (below model's 1024 token limit)
MAX_CHUNK_SIZE = 900


@st.cache_data
def check_api_status():
    """Check if the API is running"""
    try:
        response = requests.get(f"{api_url}/")
        return response.status_code == 200, (
            response.json() if response.status_code == 200 else None
        )
    except:
        raise
        return False, None


# Check API status
api_running, api_status = check_api_status()

if not api_running:
    st.error("❌ API is not running. Please start the API server first.")
    st.info("Run the following command in the terminal to start the API:")
    st.code("uvicorn api.app:app --reload --host 0.0.0.0 --port 8000")
    st.stop()

# Main app
st.write("Add diacritics (tashkeel) to Arabic text using neural models")

# Model selection
model_options = api_status["available_models"] if api_status else ["ed", "eo"]
model_descriptions = {
    "ed": "Encoder-Decoder Transformer (ED)",
    "eo": "Encoder-Only Transformer (EO)",
}

col1, col2 = st.columns([3, 1])

with col1:
    input_text = st.text_area(
        "Input Arabic text (without diacritics)",
        height=150,
        placeholder="Enter Arabic text here...",
    )

with col2:
    selected_model = st.selectbox(
        "Model",
        options=model_options,
        format_func=lambda x: model_descriptions.get(x, x),
        index=0,
    )

    clean_text = st.checkbox("Clean text (remove non-Arabic)", value=True)

    st.info(
        """
    **Models:**  
    **ED** - Encoder-Decoder Transformer  
    **EO** - Encoder-Only Transformer
    
    Long texts will be automatically split into chunks and processed separately.
    """
    )

# Process button
if st.button("Add Tashkeel"):
    if not input_text:
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Processing..."):
            try:
                # Split text into manageable chunks to avoid model size limit errors
                text_chunks = split_and_chunk_text(
                    input_text, max_chunk_size=MAX_CHUNK_SIZE
                )

                # Show info if we have multiple chunks
                if len(text_chunks) > 1:
                    st.info(
                        f"Text has been split into {len(text_chunks)} chunks for processing."
                    )

                # Handle empty text or single empty chunk
                if not text_chunks or (
                    len(text_chunks) == 1 and not text_chunks[0].strip()
                ):
                    full_result = ""
                else:
                    # Filter out empty chunks and process the non-empty ones in batch
                    non_empty_chunks = []
                    chunk_indices = (
                        []
                    )  # To track the original position of non-empty chunks

                    for i, chunk in enumerate(text_chunks):
                        if chunk.strip():
                            non_empty_chunks.append(chunk)
                            chunk_indices.append(i)

                    empty_chunks_map = [not chunk.strip() for chunk in text_chunks]

                    # Use batch processing for the non-empty chunks
                    if non_empty_chunks:
                        with st.spinner(
                            f"Processing {len(non_empty_chunks)} text chunks..."
                        ):
                            response = requests.post(
                                f"{api_url}/batch-tashkeel",
                                json={
                                    "texts": non_empty_chunks,
                                    "model_type": selected_model,
                                    "clean_text": clean_text,
                                },
                            )

                            if response.status_code == 200:
                                results = response.json()["tashkeels"]

                                # Reconstruct full result with empty chunks as newlines
                                # and preserve original line breaks from the chunks
                                all_chunks_results = [""] * len(text_chunks)

                                # Place results back in their original positions
                                for i, result_idx in enumerate(chunk_indices):
                                    all_chunks_results[result_idx] = results[i]

                                # Handle empty chunks
                                for i, is_empty in enumerate(empty_chunks_map):
                                    if is_empty:
                                        all_chunks_results[i] = (
                                            "\n"  # Empty chunk becomes a newline
                                        )

                                # Combine all processed chunks
                                full_result = "".join(all_chunks_results)
                            else:
                                raise Exception(f"API Error: {response.text}")
                    else:
                        full_result = ""  # All chunks were empty

                st.success("✅ Success!")

                # Display results
                st.subheader("Result")
                st.text_area(
                    "Diacritized text (with tashkeel)",
                    value=full_result,
                    height=150,
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
