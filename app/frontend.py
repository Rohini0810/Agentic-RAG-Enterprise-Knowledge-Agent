
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Agentic RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

# Application title
st.title("🤖 Agentic RAG")
st.subheader("Enterprise Knowledge Assistant")

st.write(
    "Ask questions about your enterprise documents "
    "and get AI-generated answers with source references."
)

# Question input
question = st.text_input(
    "Ask your question",
    placeholder="Example: How many annual leave days do employees receive?"
)

# Submit button
if st.button("Ask AI"):
    if question.strip():
        st.info("Your question: " + question)
    else:
        st.warning("Please enter a question.")
