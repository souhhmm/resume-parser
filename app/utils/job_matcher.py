from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st


@st.cache_resource
def load_sentence_transformer():
    """Load and cache the sentence transformer model."""
    return SentenceTransformer('all-MiniLM-L6-v2')


def extract_resume_text_for_matching(parsed_resume):
    texts = []
    
    # basic details
    if parsed_resume.get('basic_details'):
        basic = parsed_resume['basic_details']
        if basic.get('summary'):
            texts.append(basic['summary'])
    
    # skills
    if parsed_resume.get('skills'):
        skills = parsed_resume['skills']
        if skills.get('technical_skills'):
            texts.extend(skills['technical_skills'])
        if skills.get('tools_and_technologies'):
            texts.extend(skills['tools_and_technologies'])
    
    # experience
    if parsed_resume.get('experience'):
        for exp in parsed_resume['experience']:
            if exp.get('job_title'):
                texts.append(exp['job_title'])
            if exp.get('description'):
                texts.append(exp['description'])
            if exp.get('key_achievements'):
                texts.extend(exp['key_achievements'])
    
    # education
    if parsed_resume.get('education'):
        for edu in parsed_resume['education']:
            if edu.get('degree'):
                texts.append(edu['degree'])
            if edu.get('major'):
                texts.append(edu['major'])
    
    # projects
    if parsed_resume.get('projects'):
        for proj in parsed_resume['projects']:
            if proj.get('name'):
                texts.append(proj['name'])
            if proj.get('description'):
                texts.append(proj['description'])
            if proj.get('technologies'):
                texts.extend(proj['technologies'])
            if proj.get('key_features'):
                texts.extend(proj['key_features'])
    
    # certifications
    if parsed_resume.get('certifications'):
        for cert in parsed_resume['certifications']:
            if cert.get('name'):
                texts.append(cert['name'])
    
    return ' '.join([text for text in texts if text and text != 'null'])


def extract_jd_text_for_matching(parsed_jd):
    texts = []
    
    # job details
    if parsed_jd.get('job_details'):
        job = parsed_jd['job_details']
        if job.get('job_title'):
            texts.append(job['job_title'])
        if job.get('job_summary'):
            texts.append(job['job_summary'])
    
    # requirements
    if parsed_jd.get('requirements'):
        req = parsed_jd['requirements']
        if req.get('required_skills'):
            texts.extend(req['required_skills'])
        if req.get('preferred_skills'):
            texts.extend(req['preferred_skills'])
        if req.get('education'):
            texts.extend(req['education'])
        if req.get('experience'):
            texts.extend(req['experience'])
        if req.get('certifications'):
            texts.extend(req['certifications'])
    
    # responsibilities
    if parsed_jd.get('responsibilities'):
        texts.extend(parsed_jd['responsibilities'])
    
    # technologies
    if parsed_jd.get('technologies'):
        texts.extend(parsed_jd['technologies'])
    
    return ' '.join([text for text in texts if text and text != 'null'])


def calculate_similarity_score(resume_text, jd_text):
    if not resume_text or not jd_text:
        return 0.0
    
    model = load_sentence_transformer()
    
    # Generate embeddings
    resume_embedding = model.encode([resume_text])
    jd_embedding = model.encode([jd_text])
    
    # Calculate cosine similarity
    similarity = cosine_similarity(resume_embedding, jd_embedding)[0][0]
    
    return float(similarity)


def calculate_detailed_similarity(parsed_resume, parsed_jd):
    model = load_sentence_transformer()
    
    results = {
        'overall_score': 0.0,
        'skills_match': 0.0,
        'experience_match': 0.0,
        'education_match': 0.0,
        'section_scores': {}
    }
    
    # skills matching
    resume_skills = []
    if parsed_resume.get('skills'):
        skills = parsed_resume['skills']
        if skills.get('technical_skills'):
            resume_skills.extend(skills['technical_skills'])
        if skills.get('tools_and_technologies'):
            resume_skills.extend(skills['tools_and_technologies'])
    
    jd_skills = []
    if parsed_jd.get('requirements'):
        req = parsed_jd['requirements']
        if req.get('required_skills'):
            jd_skills.extend(req['required_skills'])
        if req.get('preferred_skills'):
            jd_skills.extend(req['preferred_skills'])
    if parsed_jd.get('technologies'):
        jd_skills.extend(parsed_jd['technologies'])
    
    if resume_skills and jd_skills:
        resume_skills_text = ' '.join([skill for skill in resume_skills if skill and skill != 'null'])
        jd_skills_text = ' '.join([skill for skill in jd_skills if skill and skill != 'null'])
        
        if resume_skills_text and jd_skills_text:
            skills_embeddings = model.encode([resume_skills_text, jd_skills_text])
            results['skills_match'] = float(cosine_similarity([skills_embeddings[0]], [skills_embeddings[1]])[0][0])
    
    # experience matching
    resume_exp = []
    if parsed_resume.get('experience'):
        for exp in parsed_resume['experience']:
            if exp.get('job_title'):
                resume_exp.append(exp['job_title'])
            if exp.get('description'):
                resume_exp.append(exp['description'])
    
    jd_exp = []
    if parsed_jd.get('job_details', {}).get('job_title'):
        jd_exp.append(parsed_jd['job_details']['job_title'])
    if parsed_jd.get('responsibilities'):
        jd_exp.extend(parsed_jd['responsibilities'])
    
    if resume_exp and jd_exp:
        resume_exp_text = ' '.join([text for text in resume_exp if text and text != 'null'])
        jd_exp_text = ' '.join([text for text in jd_exp if text and text != 'null'])
        
        if resume_exp_text and jd_exp_text:
            exp_embeddings = model.encode([resume_exp_text, jd_exp_text])
            results['experience_match'] = float(cosine_similarity([exp_embeddings[0]], [exp_embeddings[1]])[0][0])
    
    # education matching
    resume_edu = []
    if parsed_resume.get('education'):
        for edu in parsed_resume['education']:
            if edu.get('degree'):
                resume_edu.append(edu['degree'])
            if edu.get('major'):
                resume_edu.append(edu['major'])
    
    jd_edu = []
    if parsed_jd.get('requirements', {}).get('education'):
        jd_edu.extend(parsed_jd['requirements']['education'])
    
    if resume_edu and jd_edu:
        resume_edu_text = ' '.join([text for text in resume_edu if text and text != 'null'])
        jd_edu_text = ' '.join([text for text in jd_edu if text and text != 'null'])
        
        if resume_edu_text and jd_edu_text:
            edu_embeddings = model.encode([resume_edu_text, jd_edu_text])
            results['education_match'] = float(cosine_similarity([edu_embeddings[0]], [edu_embeddings[1]])[0][0])
    
    # overall score calculation
    resume_full_text = extract_resume_text_for_matching(parsed_resume)
    jd_full_text = extract_jd_text_for_matching(parsed_jd)
    results['overall_score'] = calculate_similarity_score(resume_full_text, jd_full_text)
    
    return results


def get_match_interpretation(score):
    if score >= 0.8:
        return "Excellent Match", "green"
    elif score >= 0.6:
        return "Good Match", "blue"
    elif score >= 0.4:
        return "Fair Match", "orange"
    elif score >= 0.2:
        return "Poor Match", "red"
    else:
        return "Very Poor Match", "red"
