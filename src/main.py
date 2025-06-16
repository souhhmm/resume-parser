import os
import sys
sys.path.append("./")

import json
import argparse
from pathlib import Path

import spacy
from spacy_layout import spaCyLayout
from google import genai
from src.llm.prompts import PROMPT

def extract_text_from_resume(file_path):
    try:
        # initialize spaCy with blank english model
        nlp = spacy.blank("en")
        layout = spaCyLayout(nlp)
        
        # process the document
        doc = layout(str(file_path))
        
        # return the text content
        return doc.text
        
    except Exception as e:
        print(f"error processing file: {e}")
        return None

def parse_resume(resume_path):
    # extract text from resume
    resume_text = extract_text_from_resume(resume_path)
    if not resume_text:
        print("failed to extract text from resume")
        return None
    
    print(f"extracted text from resume ({len(resume_text)} characters)")
    
    # prepare prompt with resume text
    full_prompt = f"{PROMPT}\n\nResume text:\n{resume_text}"
    
    # initialize Gemini client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    try:
        # get response from llm
        response = client.models.generate_content(
            model="gemma-3-27b-it", contents=full_prompt
        )
        
        # parse json response
        try:
            parsed_response = json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"error parsing json response: {e}")
            print(f"raw response: {response.text}")
            return None
        
        # output
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        resume_name = Path(resume_path).stem
        output_path = output_dir / f"output_{resume_name}.json"
        
        # save to json file
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(parsed_response, file, indent=2, ensure_ascii=False)
        
        print(f"resume parsing completed. results saved to: {output_path}")
        return parsed_response
        
    except Exception as e:
        print(f"error during llm processing: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='parse resume and extract details')
    parser.add_argument('resume_path', help='path to the resume file (.pdf or .docx)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.resume_path):
        print(f"error: resume file not found: {args.resume_path}")
        sys.exit(1)
    
    result = parse_resume(args.resume_path)
    
    if result:
        print("\nextracted education details:")
        print(json.dumps(result, indent=2))
    else:
        print("resume parsing failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
