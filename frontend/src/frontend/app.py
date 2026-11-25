import streamlit as st
import requests
import os

BASE_URL = os.getenv("API_URL", default="http://localhost:8001")

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
    
    if st.button("Send"):
        if question.strip():
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"prompt": question}
            )

            data = response.json()

            st.subheader("Your question:")
            st.write(question)

            st.subheader("Answer:")
            for source in data["sources"]:
                st.markdown(
                    f"[{source['title']}]({source['url']})"
                )
        else:
            st.warning("Please enter a question.")


if __name__ == "__main__":
    main()