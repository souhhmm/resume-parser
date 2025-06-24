import re
import spacy
from typing import Optional, Dict, Any
from pdfminer.high_level import extract_text
import docx2txt


class BasicResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = spacy.blank("en")

    def extract_text_from_file(self, file_path: str) -> str:
        file_path_lower = file_path.lower()

        if file_path_lower.endswith(".pdf"):
            return extract_text(file_path)
        elif file_path_lower.endswith(".docx"):
            return docx2txt.process(file_path)
        else:
            raise ValueError("unsupported file format. only PDF and DOCX supported.")

    def extract_email(self, text: str) -> Optional[str]:
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)

        if emails:
            return emails[0].lower()
        return None

    def extract_phone(self, text: str) -> Optional[str]:
        phone_patterns = [
            r"\+91[-.\s]?[6-9]\d{9}",  # indian format with +91
            r"[6-9]\d{9}",  # indian 10 digit starting with 6-9
            r"\+91[-.\s]?\d{10}",  # indian format +91 with any 10 digits
            r"\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",  # us format
            r"\+?(\d{1,3})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})",  # international
            r"\b\d{10}\b",  # 10 digit
            r"\(\d{3}\)\s?\d{3}-\d{4}",  # (123) 456-7890
            r"\d{3}-\d{3}-\d{4}",  # 123-456-7890
            r"\d{3}\.\d{3}\.\d{4}",  # 123.456.7890
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    return "".join(matches[0])
                else:
                    return matches[0]

        return None

    def extract_linkedin(self, text: str) -> Optional[str]:
        linkedin_patterns = [
            r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?",
            r"linkedin\.com/in/[A-Za-z0-9_-]+/?",
            r"www\.linkedin\.com/in/[A-Za-z0-9_-]+/?",
        ]

        for pattern in linkedin_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                url = matches[0]
                if not url.startswith("http"):
                    url = "https://" + url
                return url

        return None

    def extract_name(self, text: str) -> Optional[str]:
        lines = text.split("\n")[:5]
        text_snippet = " ".join(lines)

        # use spacy ner to find person entities
        doc = self.nlp(text_snippet)
        person_entities = [
            ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"
        ]

        if person_entities:
            name = person_entities[0]
            # clean up name (remove prefixes)
            name = re.sub(r"\b(Mr|Mrs|Ms|Dr|Prof)\.?\s*", "", name, flags=re.IGNORECASE)
            return name.strip()

        return None

    def extract_all_fields(self, text: str) -> Dict[str, Any]:
        return {
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "linkedin": self.extract_linkedin(text),
        }

    def parse_resume_file(self, file_path: str) -> Dict[str, Any]:
        try:
            text = self.extract_text_from_file(file_path)
            return self.extract_all_fields(text)
        except Exception as e:
            print(f"error parsing file {file_path}: {e}")
            return {
                "name": None,
                "email": None,
                "phone": None,
                "linkedin": None,
                "error": str(e),
            }


def extract_name(text: str) -> Optional[str]:
    parser = BasicResumeParser()
    return parser.extract_name(text)


def extract_email(text: str) -> Optional[str]:
    parser = BasicResumeParser()
    return parser.extract_email(text)


def extract_phone(text: str) -> Optional[str]:
    parser = BasicResumeParser()
    return parser.extract_phone(text)


def extract_linkedin(text: str) -> Optional[str]:
    parser = BasicResumeParser()
    return parser.extract_linkedin(text)


# test with sample resume
if __name__ == "__main__":
    import sys

    parser = BasicResumeParser()

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"parsing resume: {file_path}")
        result = parser.parse_resume_file(file_path)
    else:
        # default
        file_path = "files/soham_resume.pdf"
        print(f"parsing resume: {file_path}")
        result = parser.parse_resume_file(file_path)

    print("extracted fields:")
    print(f"name: {result['name']}")
    print(f"email: {result['email']}")
    print(f"phone: {result['phone']}")
    print(f"linkedin: {result['linkedin']}")
