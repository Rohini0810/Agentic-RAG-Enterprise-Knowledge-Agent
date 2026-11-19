
import streamlit as st
import requests

# --------------------------------
# Page configuration
# --------------------------------

st.set_page_config(
    page_title="Agentic RAG | Knowledge Assistant",
    page_icon="🤖",
    layout="wide"
)

import os

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000/ask"
)

# --------------------------------
# Session state
# --------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------
# Sidebar
# --------------------------------

with st.sidebar:
    st.title("🤖 Agentic RAG")
    st.caption("Enterprise Knowledge Assistant")

    st.divider()

    st.subheader("Workspace")

    if st.button("➕ New conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    
    st.subheader("System information")

    st.write("**Frontend:** Streamlit")

    try:
        health_response = requests.get(
            "http://127.0.0.1:8000/health",
        timeout=5
        )

        if health_response.status_code == 200:
            health_data = health_response.json()

            if health_data.get("status") == "healthy":
                st.success("Backend: Online")
            else:
                st.error("Backend: Unhealthy")
        else:
            st.error("Backend: Unavailable")

    except requests.exceptions.RequestException:
        st.error("Backend: Offline")

    st.write("**LLM:** Qwen 2.5 3B")
    st.write("**Retrieval:** Hybrid + Reranking")


    st.divider()

    st.caption("Project 4 — AI Engineering Roadmap")

# --------------------------------
# Main page
# --------------------------------

st.title("Enterprise Knowledge Assistant")

st.write(
    "Ask questions about your enterprise knowledge base. "
    "Get AI-generated answers supported by source documents."
)

st.divider()

# --------------------------------
# Display conversation history
# --------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("📚 View source documents"):
                for source in message["sources"]:
                    st.write(f"📄 {source}")

# --------------------------------
# User input
# --------------------------------

question = st.chat_input(
    "Ask your enterprise knowledge base..."
)

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching enterprise documents and generating an answer..."
        ):

            try:
                response = requests.post(
                    API_URL,
                    json={"question": question},
                    timeout=120
                )

                response.raise_for_status()

                result = response.json()

                answer = result["answer"]
                sources = result["sources"]

                st.markdown(answer)

                if sources:
                    with st.expander("📚 View source documents"):
                        for source in sources:
                            st.write(f"📄 {source}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except requests.exceptions.ConnectionError:
                st.error(
                    "Unable to connect to the backend. "
                    "Please check whether FastAPI is running."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "The request timed out. Please try again."
                )

            except requests.exceptions.HTTPError as error:
                st.error(f"Backend API error: {error}")

            except (KeyError, ValueError):
                st.error(
                    "The backend returned an unexpected response."
                )
