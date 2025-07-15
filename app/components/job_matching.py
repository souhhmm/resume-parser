import streamlit as st
import tempfile
import os
import sys

sys.path.append("./")

from utils.extract_text import extract_text_from_resume
from utils.jd_parser import parse_job_description_text
from utils.job_matcher import calculate_detailed_similarity, get_match_interpretation
from src.llm import prompts


def render_job_matching_tab(parsed_resume):
    st.subheader("Job Description Matching")
    st.write("Upload a job description to see how well it matches with the resume.")
    
    # initialize session state for job matching
    if "jd_parsed_data" not in st.session_state:
        st.session_state.jd_parsed_data = None
    if "jd_current_file" not in st.session_state:
        st.session_state.jd_current_file = None
    if "similarity_results" not in st.session_state:
        st.session_state.similarity_results = None
    
    # job description upload
    uploaded_jd = st.file_uploader(
        "Choose a job description file",
        type=["pdf", "docx", "txt"],
        help="Upload a PDF, DOCX, or TXT job description file",
        key="jd_uploader"
    )
    
    if uploaded_jd is not None:
        file_changed = st.session_state.jd_current_file != uploaded_jd.name
        
        if file_changed or st.session_state.jd_parsed_data is None:
            # process the job description
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{uploaded_jd.name.split('.')[-1]}"
            ) as tmp_file:
                tmp_file.write(uploaded_jd.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # extract text from job description
                jd_text = extract_text_from_resume(tmp_file_path)
                
                if jd_text:
                    with st.expander("View Extracted Job Description Text"):
                        st.text_area("Job Description Text", jd_text, height=200, key="jd_text")
                    
                    # parse job description
                    parsed_jd = parse_job_description_text(jd_text, prompts)
                    
                    if parsed_jd:
                        st.session_state.jd_parsed_data = parsed_jd
                        st.session_state.jd_current_file = uploaded_jd.name

                        # calculate similarity
                        similarity_results = calculate_detailed_similarity(parsed_resume, parsed_jd)
                        st.session_state.similarity_results = similarity_results
                        
                        st.success("Job description processed successfully!")
                    else:
                        st.error("Failed to parse the job description.")
                        return
                else:
                    st.error("Failed to extract text from the job description.")
                    return
            finally:
                # cleanup temp file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
        else:
            st.success(f"Using cached results for: {uploaded_jd.name}")
    
    # display results if available
    if st.session_state.jd_parsed_data and st.session_state.similarity_results:
        display_job_matching_results(
            st.session_state.jd_parsed_data, 
            st.session_state.similarity_results
        )
    elif uploaded_jd is None:
        st.info("""
        ### How to use Job Matching:
        1. Upload a job description file (PDF, DOCX, or TXT)
        2. The system will extract and analyze the job requirements
        3. View the similarity score between your resume and the job description
        4. See detailed matching results for different sections
        
        ### What gets analyzed:
        - Skills matching
        - Experience relevance
        - Education requirements
        - Overall compatibility score
        """)


def display_job_matching_results(parsed_jd, similarity_results):
    st.markdown("---")
    st.subheader("Matching Results")
    
    # overall score display
    overall_score = similarity_results['overall_score']
    interpretation, color = get_match_interpretation(overall_score)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Overall Match Score",
            value=f"{overall_score:.2%}",
            help="Overall similarity between resume and job description"
        )
    
    with col2:
        st.metric(
            label="Match Quality",
            value=interpretation,
            help="Interpretation of the similarity score"
        )
    
    with col3:
        # color-coded indicator
        if color == "green":
            st.success("Strong candidate match")
        elif color == "blue":
            st.info("Good candidate match")
        elif color == "orange":
            st.warning("Moderate candidate match")
        else:
            st.error("Weak candidate match")
    
    # detailed section scores
    st.subheader("Detailed Section Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        skills_score = similarity_results['skills_match']
        st.metric(
            label="Skills Match",
            value=f"{skills_score:.2%}",
            help="How well your skills match the job requirements"
        )
    
    with col2:
        exp_score = similarity_results['experience_match']
        st.metric(
            label="Experience Match",
            value=f"{exp_score:.2%}",
            help="How relevant your experience is to the job"
        )
    
    with col3:
        edu_score = similarity_results['education_match']
        st.metric(
            label="Education Match",
            value=f"{edu_score:.2%}",
            help="How well your education matches the requirements"
        )
    
    # job details display
    st.subheader("Job Description Summary")
    
    if parsed_jd.get('job_details'):
        job_details = parsed_jd['job_details']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if job_details.get('job_title'):
                st.write(f"**Position:** {job_details['job_title']}")
            if job_details.get('company'):
                st.write(f"**Company:** {job_details['company']}")
            if job_details.get('location'):
                st.write(f"**Location:** {job_details['location']}")
            if job_details.get('employment_type'):
                st.write(f"**Employment Type:** {job_details['employment_type']}")
        
        with col2:
            if job_details.get('experience_level'):
                st.write(f"**Experience Level:** {job_details['experience_level']}")
            if job_details.get('salary_range'):
                st.write(f"**Salary Range:** {job_details['salary_range']}")
    
    # requirements breakdown
    if parsed_jd.get('requirements'):
        st.subheader("Job Requirements Analysis")
        
        requirements = parsed_jd['requirements']
        
        tab1, tab2, tab3 = st.tabs(["Skills", "Experience", "Education"])
        
        with tab1:
            if requirements.get('required_skills'):
                st.write("**Required Skills:**")
                for skill in requirements['required_skills']:
                    if skill and skill != 'null':
                        st.write(f"• {skill}")
            
            if requirements.get('preferred_skills'):
                st.write("**Preferred Skills:**")
                for skill in requirements['preferred_skills']:
                    if skill and skill != 'null':
                        st.write(f"• {skill}")
        
        with tab2:
            if requirements.get('experience'):
                st.write("**Experience Requirements:**")
                for exp in requirements['experience']:
                    if exp and exp != 'null':
                        st.write(f"• {exp}")
        
        with tab3:
            if requirements.get('education'):
                st.write("**Education Requirements:**")
                for edu in requirements['education']:
                    if edu and edu != 'null':
                        st.write(f"• {edu}")
            
            if requirements.get('certifications'):
                st.write("**Certifications:**")
                for cert in requirements['certifications']:
                    if cert and cert != 'null':
                        st.write(f"• {cert}")
    
    # eecommendations section
    st.subheader("Recommendations")
    
    if overall_score >= 0.8:
        st.success("""
        **Excellent match!**
        """)
    elif overall_score >= 0.6:
        st.info("""
        **Good match!**
        """)
    elif overall_score >= 0.4:
        st.warning("""
        **Fair match.**
        """)
    else:
        st.error("""
        **Limited match.**
        """)
