import streamlit as st
import requests
import json
from ui.text_preprocessor import split_and_chunk_text, process_and_join_chunks

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
                if not text_chunks or (len(text_chunks) == 1 and not text_chunks[0].strip()):
                    full_result = ""
                else:
                    # Filter out empty chunks and process the non-empty ones in batch
                    non_empty_chunks = [chunk for chunk in text_chunks if chunk.strip()]
                    empty_chunks_map = [not chunk.strip() for chunk in text_chunks]
                    
                    # Show progress bar if we have multiple chunks
                    if len(text_chunks) > 1:
                        progress_bar = st.progress(0.0)
                    
                    # Use batch processing for the non-empty chunks
                    if non_empty_chunks:
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
                            
                            # Update progress bar
                            if len(text_chunks) > 1:
                                progress_bar.progress(1.0)
                            
                            # Reconstruct full result with empty chunks as newlines
                            all_chunks_results = []
                            result_index = 0
                            
                            for is_empty in empty_chunks_map:
                                if is_empty:
                                    all_chunks_results.append("\n")  # Empty chunk becomes a newline
                                else:
                                    all_chunks_results.append(results[result_index])
                                    result_index += 1
                                    
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

# Advanced section - Batch Processing
with st.expander("Batch Processing"):
    st.write("Process multiple texts at once")

    # Text area for batch input (one text per line)
    batch_text = st.text_area(
        "Input multiple texts (one per line)",
        height=150,
        placeholder="Text 1\nText 2\nText 3",
    )

    if st.button("Process Batch"):
        if not batch_text:
            st.warning("Please enter some texts first.")
        else:
            # Split by lines and remove empty lines
            texts = [t.strip() for t in batch_text.split("\n") if t.strip()]

            if not texts:
                st.warning("No valid texts found.")
                st.stop()

            with st.spinner(f"Processing {len(texts)} texts..."):
                try:
                    # Process each text separately, with chunking for long texts
                    all_results = []
                    progress_bar = st.progress(0.0)

                    for i, text in enumerate(texts):
                        # Check if text needs to be chunked
                        text_chunks = split_and_chunk_text(
                            text, max_chunk_size=MAX_CHUNK_SIZE
                        )

                        # Process all chunks for this text
                        processed_chunks = []
                        for chunk in text_chunks:
                            if not chunk.strip():
                                processed_chunks.append("")
                                continue

                            chunk_response = requests.post(
                                f"{api_url}/tashkeel",
                                json={
                                    "text": chunk,
                                    "model_type": selected_model,
                                    "clean_text": clean_text,
                                },
                            )

                            if chunk_response.status_code == 200:
                                processed_chunks.append(
                                    chunk_response.json()["tashkeel"]
                                )
                            else:
                                raise Exception(
                                    f"API Error on text {i+1}: {chunk_response.text}"
                                )

                        # Combine chunks for this text
                        full_result = "".join(processed_chunks)
                        all_results.append(full_result)

                        # Update progress
                        progress_bar.progress((i + 1) / len(texts))

                    st.success(f"✅ Successfully processed {len(texts)} texts!")

                    # Create a table of results
                    result_data = [
                        {"Original": orig, "Diacritized": diact}
                        for orig, diact in zip(texts, all_results)
                    ]

                    st.subheader("Results")
                    st.table(result_data)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# API Documentation
with st.expander("API Documentation"):
    st.write("### API Endpoints")
    st.code(
        """
# Get API status
GET /

# Add diacritics to a single text
POST /tashkeel
{
  "text": "النص العربي بدون تشكيل",
  "model_type": "ed",  # or "eo"
  "clean_text": true
}

# Add diacritics to multiple texts
POST /batch-tashkeel
{
  "texts": ["النص الأول", "النص الثاني"],
  "model_type": "ed",  # or "eo"
  "clean_text": true
}
    """
    )

    st.write("### Text Size Limitations")
    st.info(
        """
        The neural models have a maximum input size limit of 1024 tokens. 
        
        For large texts:
        - This UI automatically splits text into appropriate chunks
        - When using the API directly, consider splitting long texts into smaller segments (900 characters or less is recommended)
        - Use the batch endpoint for processing multiple texts efficiently
        """
    )
