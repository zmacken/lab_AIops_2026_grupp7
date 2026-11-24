import streamlit as st
import requests
import os

BASE_URL = os.getenv("API_URL", default="http://localhost:8000")

def main():
    st.set_page_config(
        page_title="MCF Assistant",
        page_icon="🛡️"
    )

    st.title("MCF Assistant")

    st.write(
        "Ask questions about civil defence "
        "and emergency preparedness in Sweden"
    )

    question = st.text_input(
    "Write your question:"
    )


if __name__ == "__main__":
    main()