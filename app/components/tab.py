import streamlit as st
from .display import (
    display_basic_details,
    display_education,
    display_experience,
    display_skills,
    display_certifications,
    display_projects,
)


def render_data_tabs(parsed_data, dataframes):
    tabs = st.tabs(
        [
            "Basic",
            "Education",
            "Experience",
            "Skills",
            "Certifications",
            "Projects",
            "CSV View",
            "Raw Data",
        ]
    )

    with tabs[0]:  # basic Details
        if parsed_data.get("basic_details"):
            display_basic_details(parsed_data["basic_details"])
            if "Basic Details" in dataframes:
                st.subheader("Table View")
                st.dataframe(dataframes["Basic Details"], use_container_width=True)
        else:
            st.info("No basic details found")

    with tabs[1]:  # education
        if parsed_data.get("education"):
            display_education(parsed_data["education"])
            if "Education" in dataframes:
                st.subheader("Table View")
                st.dataframe(dataframes["Education"], use_container_width=True)
        else:
            st.info("No education information found")

    with tabs[2]:  # experience
        if parsed_data.get("experience"):
            display_experience(parsed_data["experience"])
            if "Experience" in dataframes:
                st.subheader("Table View")
                st.dataframe(dataframes["Experience"], use_container_width=True)
        else:
            st.info("No experience information found")

    with tabs[3]:  # skills
        if parsed_data.get("skills"):
            display_skills(parsed_data["skills"])
            if "Skills" in dataframes:
                st.subheader("Table View")
                st.dataframe(dataframes["Skills"], use_container_width=True)
        else:
            st.info("No skills information found")

    with tabs[4]:  # certifications
        if parsed_data.get("certifications"):
            display_certifications(parsed_data["certifications"])
            if "Certifications" in dataframes:
                st.subheader("Table View")
                st.dataframe(dataframes["Certifications"], use_container_width=True)
        else:
            st.info("No certifications found")

    with tabs[5]:  # projects
        if parsed_data.get("projects"):
            display_projects(parsed_data["projects"])
            if "Projects" in dataframes:
                st.subheader("Table View")
                st.dataframe(dataframes["Projects"], use_container_width=True)
        else:
            st.info("No projects found")

    with tabs[6]:  # csv view
        st.subheader("All Data in CSV Format")
        if dataframes:
            for section_name, df in dataframes.items():
                st.write(f"**{section_name}:**")
                st.dataframe(df, use_container_width=True)
                st.divider()
        else:
            st.info("No data available for CSV view")

    with tabs[7]:  # raw data
        st.json(parsed_data)
