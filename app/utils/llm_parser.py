import json
import os
import sys
import streamlit as st
from google import genai

sys.path.append("./")
from config import LLM_MODEL


def parse_resume_text(resume_text, prompts):
    if not resume_text:
        return None

    # combine all prompts into full request
    full_prompt = f"""{prompts.SYSTEM_PROMPT}

Your task is to extract ALL the following information from the resume in a single JSON response:

1. Basic Details:
{prompts.BASIC_DETAILS_PROMPT.replace("As a resume parser, your job is to extract basic personal details from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

2. Education:
{prompts.EDUCATION_PROMPT.replace("As a resume parser, your job is to extract education details from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

3. Experience:
{prompts.EXPERIENCE_PROMPT.replace("As a resume parser, your job is to extract work experience details from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

4. Skills:
{prompts.SKILLS_PROMPT.replace("As a resume parser, your job is to extract skills from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

5. Certifications:
{prompts.CERTIFICATIONS_PROMPT.replace("As a resume parser, your job is to extract certifications and licenses from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

6. Projects:
{prompts.PROJECTS_PROMPT.replace("As a resume parser, your job is to extract project details from resumes provided as plain text.", "").replace("Respond in the following JSON format:", "").strip()}

Combine all sections into a single JSON response with the following structure:
{{
    "basic_details": {{ ... }},
    "education": [ ... ],
    "experience": [ ... ],
    "skills": {{ ... }},
    "certifications": [ ... ],
    "projects": [ ... ]
}}

Resume text:
{resume_text}"""

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("GEMINI_API_KEY environment variable not set!")
            return None

        client = genai.Client(api_key=api_key)

        with st.spinner("Analyzing resume..."):
            response = client.models.generate_content(
                model=LLM_MODEL, contents=full_prompt
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
            return parsed_response

        except json.JSONDecodeError as e:
            st.error(f"Error parsing response: {e}")
            with st.expander("Raw Response"):
                st.text(response.text)
            return None

    except Exception as e:
        st.error(f"Error during processing: {e}")
        return None
