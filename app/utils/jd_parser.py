import json
import os
import sys
import streamlit as st
from google import genai

sys.path.append("./")
from config import LLM_MODEL


def parse_job_description_text(jd_text, prompts):
    if not jd_text:
        return None

    full_prompt = f"""{prompts.SYSTEM_PROMPT}

Your task is to extract structured information from the job description:

{prompts.JOB_DESCRIPTION_PROMPT}

Job Description Text:
{jd_text}"""

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("GEMINI_API_KEY environment variable not set!")
            return None

        client = genai.Client(api_key=api_key)

        with st.spinner("Analyzing job description..."):
            response = client.models.generate_content(
                model=LLM_MODEL, contents=full_prompt
            )

        try:
            # extract JSON from response
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
            st.error(f"Error parsing job description response: {e}")
            with st.expander("Raw Response"):
                st.text(response.text)
            return None

    except Exception as e:
        st.error(f"Error during job description processing: {e}")
        return None
