import os
import sys

sys.path.append("./")

import json
import argparse
from pathlib import Path

import spacy
from spacy_layout import spaCyLayout
from google import genai
from src.llm.prompts import (
    SYSTEM_PROMPT,
    BASIC_DETAILS_PROMPT,
    EDUCATION_PROMPT,
    EXPERIENCE_PROMPT,
    SKILLS_PROMPT,
    CERTIFICATIONS_PROMPT,
    PROJECTS_PROMPT,
)


def extract_text_from_resume(file_path):
    try:
        # process document with spacy layout
        nlp = spacy.blank("en")
        layout = spaCyLayout(nlp)
        doc = layout(str(file_path))
        return doc.text

    except Exception as e:
        print(f"error processing file: {e}")
        return None


def parse_resume(resume_path):
    resume_text = extract_text_from_resume(resume_path)
    if not resume_text:
        print("failed to extract text from resume")
        return None

    print(f"extracted text from resume ({len(resume_text)} characters)")

    # combine all prompts into full request
    full_prompt = f"""{SYSTEM_PROMPT}

Your task is to extract ALL the following information from the resume in a single JSON response:

1. Basic Details:
{BASIC_DETAILS_PROMPT.replace("As a resume parser, your job is to extract basic personal details from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

2. Education:
{EDUCATION_PROMPT.replace("As a resume parser, your job is to extract education details from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

3. Experience:
{EXPERIENCE_PROMPT.replace("As a resume parser, your job is to extract work experience details from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

4. Skills:
{SKILLS_PROMPT.replace("As a resume parser, your job is to extract skills from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

5. Certifications:
{CERTIFICATIONS_PROMPT.replace("As a resume parser, your job is to extract certifications and licenses from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

6. Projects:
{PROJECTS_PROMPT.replace("As a resume parser, your job is to extract project details from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

Combine all sections into a single JSON response with the following structure:
{{
    "basic_details": {{ ... }},
    "education": [ ... ],
    "experience": [ ... ],
    "skills": {{ ... }},
    "certifications": [ ... ],
    "projects": [ ... ]
}}

Do NOT wrap anything in ```json``` tags, and only respond with the JSON object. Make sure to include the outer curly braces.

Resume text:
{resume_text}"""

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    try:
        response = client.models.generate_content(
            model="gemma-3-27b-it", contents=full_prompt
        )

        try:
            # extract json from response
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                start_marker = "```json"
                end_marker = "```"
                start_idx = response_text.find(start_marker) + len(start_marker)
                end_idx = response_text.rfind(end_marker)
                if end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx].strip()

            parsed_response = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"error parsing json response: {e}")
            print(f"raw response: {response.text}")
            return None

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        resume_name = Path(resume_path).stem
        output_path = output_dir / f"output_{resume_name}.json"

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(parsed_response, file, indent=2, ensure_ascii=False)

        print(f"resume parsing completed. results saved to: {output_path}")
        return parsed_response

    except Exception as e:
        print(f"error during llm processing: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="parse resume and extract details")
    parser.add_argument(
        "resume_path",
        nargs="?",
        default="files/soham_resume.pdf",
        help="path to the resume file (.pdf or .docx). Default: files/soham_resume.pdf",
    )

    args = parser.parse_args()

    if not os.path.exists(args.resume_path):
        print(f"error: resume file not found: {args.resume_path}")
        sys.exit(1)

    print(f"processing resume: {args.resume_path}")
    result = parse_resume(args.resume_path)

    if result:
        print("\nextracted resume details:")
        print(json.dumps(result, indent=2))
    else:
        print("resume parsing failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
