from setuptools import setup, find_packages

setup(
    name="resume-parser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-genai",
        "spacy",
        "spacy-layout",
        "pdfminer.six",
        "docx2txt",
        "nltk",
        "streamlit",
        "pandas",
    ],
    python_requires=">=3.10",
)
