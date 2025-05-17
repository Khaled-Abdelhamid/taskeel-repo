import streamlit as st
import requests
import json

st.set_page_config(page_title="Tashkeel Web UI", page_icon="🔤", layout="wide")

st.title("🔤 Arabic Diacritization (Tashkeel)")

# Set the API URL
api_url = "http://localhost:8000"


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
    """
    )

# Process button
if st.button("Add Tashkeel"):
    if not input_text:
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Processing..."):
            try:
                response = requests.post(
                    f"{api_url}/tashkeel",
                    json={
                        "text": input_text,
                        "model_type": selected_model,
                        "clean_text": clean_text,
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Success!")

                    # Display results
                    st.subheader("Result")
                    st.text_area(
                        "Diacritized text (with tashkeel)",
                        value=result["tashkeel"],
                        height=150,
                    )
                else:
                    st.error(f"❌ Error: {response.text}")
            except Exception as e:
                st.error(f"❌ Error connecting to API: {str(e)}")

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
                    response = requests.post(
                        f"{api_url}/batch-tashkeel",
                        json={
                            "texts": texts,
                            "model_type": selected_model,
                            "clean_text": clean_text,
                        },
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.success(
                            f"✅ Successfully processed {len(result['tashkeels'])} texts!"
                        )

                        # Create a table of results
                        result_data = [
                            {"Original": orig, "Diacritized": diact}
                            for orig, diact in zip(texts, result["tashkeels"])
                        ]

                        st.subheader("Results")
                        st.table(result_data)
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error connecting to API: {str(e)}")

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
