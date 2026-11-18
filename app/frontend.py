
import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="Agentic RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/ask"

st.title("🤖 Agentic RAG")
st.subheader("Enterprise Knowledge Assistant")

st.write(
    "Ask questions about your enterprise documents "
    "and get AI-generated answers with source references."
)

question = st.text_input(
    "Ask your question",
    placeholder="How many annual leave days do employees receive?"
)

if st.button("Ask AI"):
    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            with st.spinner("Searching documents and generating your answer..."):

                response = requests.post(
                    API_URL,
                    json={"question": question},
                    timeout=120
                )

                response.raise_for_status()
                result = response.json()

            st.subheader("Answer")
            st.write(result["answer"])

            st.subheader("Source Documents")

            for source in result["sources"]:
                st.write(f"📄 {source}")

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the FastAPI backend. Is it running?")

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")

        except requests.exceptions.HTTPError as error:
            st.error(f"API returned an error: {error}")

        except (KeyError, ValueError):
            st.error("The API returned an unexpected response.")
