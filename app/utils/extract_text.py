import streamlit as st
import spacy
from spacy_layout import spaCyLayout


def extract_text_from_resume(file_path):
    try:
        nlp = spacy.blank("en")
        layout = spaCyLayout(nlp)
        doc = layout(str(file_path))
        return doc.text
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None
