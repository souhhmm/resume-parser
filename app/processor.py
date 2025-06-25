import streamlit as st
import tempfile
import os
import sys
import time

sys.path.append("./")

from utils import extract_text_from_resume, parse_resume_text, convert_to_dataframes
from src.llm import prompts


def process_uploaded_file(uploaded_file):
    # save file temporarily
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}"
    ) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    # create placeholders for temp messages
    text_extraction_placeholder = st.empty()
    parsing_success_placeholder = st.empty()

    try:
        with st.spinner("Extracting text from resume..."):
            resume_text = extract_text_from_resume(tmp_file_path)

        if resume_text:
            # show temp success message for text extraction
            text_extraction_placeholder.success(
                f"Text extracted successfully! ({len(resume_text)} characters)"
            )

            with st.expander("View Extracted Text"):
                st.text_area("Resume Text", resume_text, height=200)

            with st.spinner("Parsing resume..."):
                parsed_data = parse_resume_text(resume_text, prompts)

            if parsed_data:
                # clear the text extraction message
                text_extraction_placeholder.empty()

                # show temp success message for parsing
                parsing_success_placeholder.success("Resume parsed successfully!")

                dataframes = convert_to_dataframes(parsed_data)

                # clear after 3s
                time.sleep(3)
                parsing_success_placeholder.empty()

                return parsed_data, dataframes
            else:
                text_extraction_placeholder.empty()
                st.error("Failed to parse the resume.")
                return None, None
        else:
            st.error("Failed to extract text from the resume.")
            return None, None

    finally:
        # cleanup temp file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
