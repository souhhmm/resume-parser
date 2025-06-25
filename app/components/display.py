import streamlit as st


def display_basic_details(basic_details):
    st.subheader("Basic Details")

    col1, col2 = st.columns(2)

    with col1:
        if basic_details.get("full_name") and basic_details["full_name"] != "null":
            st.write(f"**Name:** {basic_details['full_name']}")
        if basic_details.get("email") and basic_details["email"] != "null":
            st.write(f"**Email:** {basic_details['email']}")
        if basic_details.get("phone") and basic_details["phone"] != "null":
            st.write(f"**Phone:** {basic_details['phone']}")
        if basic_details.get("location") and basic_details["location"] != "null":
            st.write(f"**Location:** {basic_details['location']}")

    with col2:
        if basic_details.get("linkedin") and basic_details["linkedin"] != "null":
            st.write(f"**LinkedIn:** {basic_details['linkedin']}")
        if basic_details.get("github") and basic_details["github"] != "null":
            st.write(f"**GitHub:** {basic_details['github']}")
        if basic_details.get("portfolio") and basic_details["portfolio"] != "null":
            st.write(f"**Portfolio:** {basic_details['portfolio']}")

    if basic_details.get("summary") and basic_details["summary"] != "null":
        st.write(f"**Summary:** {basic_details['summary']}")


def display_education(education):
    st.subheader("Education")

    for edu in education:
        with st.container():
            st.write(f"**{edu.get('degree', 'N/A')}** in {edu.get('major', 'N/A')}")
            st.write(
                f"*{edu.get('institution', 'N/A')}* - {edu.get('location', 'N/A')}"
            )

            col1, col2 = st.columns(2)
            with col1:
                if edu.get("start_year") and edu.get("end_year"):
                    st.write(f"**Duration:** {edu['start_year']} - {edu['end_year']}")
            with col2:
                if edu.get("grade") and edu["grade"] != "null":
                    st.write(f"**Grade:** {edu['grade']}")

            st.divider()


def display_experience(experience):
    st.subheader("Experience")

    for exp in experience:
        with st.container():
            st.write(f"**{exp.get('job_title', 'N/A')}**")
            st.write(f"*{exp.get('company', 'N/A')}* - {exp.get('location', 'N/A')}")

            if exp.get("start_date") and exp.get("end_date"):
                st.write(f"**Duration:** {exp['start_date']} - {exp['end_date']}")

            if exp.get("description") and exp["description"] != "null":
                st.write(f"**Description:** {exp['description']}")

            if exp.get("key_achievements") and exp["key_achievements"]:
                st.write("**Key Achievements:**")
                for achievement in exp["key_achievements"]:
                    st.write(f"• {achievement}")

            st.divider()


def display_skills(skills):
    st.subheader("Skills")

    col1, col2 = st.columns(2)

    with col1:
        if skills.get("technical_skills"):
            st.write("**Technical Skills:**")
            tech_skills_str = ", ".join(skills["technical_skills"])
            st.write(tech_skills_str)

        if skills.get("tools_and_technologies"):
            st.write("**Tools & Technologies:**")
            tools_str = ", ".join(skills["tools_and_technologies"])
            st.write(tools_str)

    with col2:
        if skills.get("soft_skills"):
            st.write("**Soft Skills:**")
            soft_skills_str = ", ".join(skills["soft_skills"])
            st.write(soft_skills_str)

        if skills.get("languages"):
            st.write("**Languages:**")
            languages_list = []
            for lang in skills["languages"]:
                proficiency = lang.get("proficiency", "N/A")
                if proficiency == "null":
                    proficiency = "N/A"
                languages_list.append(f"{lang.get('language', 'N/A')} ({proficiency})")
            languages_str = ", ".join(languages_list)
            st.write(languages_str)


def display_certifications(certifications):
    if not certifications:
        return

    st.subheader("Certifications")

    for cert in certifications:
        with st.container():
            st.write(f"**{cert.get('name', 'N/A')}**")
            if (
                cert.get("issuing_organization")
                and cert["issuing_organization"] != "null"
            ):
                st.write(f"*Issued by: {cert['issuing_organization']}*")

            col1, col2 = st.columns(2)
            with col1:
                if cert.get("issue_date") and cert["issue_date"] != "null":
                    st.write(f"**Issue Date:** {cert['issue_date']}")
            with col2:
                if cert.get("expiry_date") and cert["expiry_date"] != "null":
                    st.write(f"**Expiry:** {cert['expiry_date']}")

            if cert.get("verification_url") and cert["verification_url"] != "null":
                st.write(f"**Verification:** {cert['verification_url']}")

            st.divider()


def display_projects(projects):
    if not projects:
        return

    st.subheader("Projects")

    for project in projects:
        with st.container():
            st.write(f"**{project.get('name', 'N/A')}**")

            if project.get("description") and project["description"] != "null":
                st.write(f"{project['description']}")

            col1, col2 = st.columns(2)
            with col1:
                if project.get("role") and project["role"] != "null":
                    st.write(f"**Role:** {project['role']}")
                if project.get("team_size") and project["team_size"] != "null":
                    st.write(f"**Team Size:** {project['team_size']}")

            with col2:
                if project.get("start_date") and project.get("end_date"):
                    if project["start_date"] != "null" or project["end_date"] != "null":
                        start = (
                            project["start_date"]
                            if project["start_date"] != "null"
                            else "N/A"
                        )
                        end = (
                            project["end_date"]
                            if project["end_date"] != "null"
                            else "N/A"
                        )
                        st.write(f"**Duration:** {start} - {end}")

                if project.get("url") and project["url"] != "null":
                    st.write(f"**URL:** {project['url']}")

            if project.get("technologies") and project["technologies"]:
                st.write("**Technologies:**")
                tech_str = ", ".join(project["technologies"])
                st.write(tech_str)

            if project.get("key_features") and project["key_features"]:
                st.write("**Key Features:**")
                for feature in project["key_features"]:
                    st.write(f"• {feature}")

            st.divider()
