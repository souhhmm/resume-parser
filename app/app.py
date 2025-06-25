import streamlit as st
import sys

sys.path.append("./src")

from components import render_data_tabs, render_download_section
from config import APP_TITLE, APP_ICON
from processor import process_uploaded_file


def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title(APP_TITLE)
    st.markdown(
        "Upload your resume and get structured information extracted automatically!"
    )

    if "parsed_data" not in st.session_state:
        st.session_state.parsed_data = None
    if "current_file" not in st.session_state:
        st.session_state.current_file = None
    if "dataframes" not in st.session_state:
        st.session_state.dataframes = None

    st.markdown("---")
    st.subheader("Upload Resume")

    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=["pdf", "docx"],
        help="Upload a PDF or DOCX resume file",
    )

    if uploaded_file is not None:
        file_changed = st.session_state.current_file != uploaded_file.name

        if file_changed or st.session_state.parsed_data is None:
            parsed_data, dataframes = process_uploaded_file(uploaded_file)

            if parsed_data and dataframes:
                st.session_state.parsed_data = parsed_data
                st.session_state.current_file = uploaded_file.name
                st.session_state.dataframes = dataframes
            else:
                return
        else:
            st.success(f"Using cached results for: {uploaded_file.name}")

        if st.session_state.parsed_data:
            parsed_data = st.session_state.parsed_data
            dataframes = st.session_state.dataframes

            render_data_tabs(parsed_data, dataframes)

            render_download_section(
                parsed_data, dataframes, st.session_state.current_file
            )

    else:
        st.info("""
        ### How to use:
        1. Upload a PDF or DOCX resume file using the file uploader
        2. The system will extract and analyze the content
        3. View structured information in organized tabs
        4. Download the results as JSON or CSV
        
        ### Features:
        - Automated text extraction
        - Structured data parsing
        - Multiple view formats
        - JSON and CSV export functionality
        """)


if __name__ == "__main__":
    main()
