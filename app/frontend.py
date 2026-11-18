
import streamlit as st
import requests

st.set_page_config(
    page_title="Agentic RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/ask"

st.title("🤖 Agentic RAG")
st.caption("Enterprise Knowledge Assistant")

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear conversation button
if st.button("Clear conversation"):
    st.session_state.messages = []
    st.rerun()

# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("Source Documents"):
                for source in message["sources"]:
                    st.write(f"📄 {source}")

# Chat input
question = st.chat_input("Ask your enterprise knowledge base...")

if question:

    # Display and store user question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    # Call FastAPI
    with st.chat_message("assistant"):

        with st.spinner("Searching documents and generating answer..."):

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

                st.write(answer)

                with st.expander("Source Documents"):
                    for source in sources:
                        st.write(f"📄 {source}")

                # Store assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except requests.exceptions.RequestException as error:
                st.error(f"Could not reach the AI backend: {error}")

            except (KeyError, ValueError):
                st.error("The API returned an unexpected response.")
