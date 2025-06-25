import pandas as pd


def convert_to_dataframes(parsed_data):
    dataframes = {}

    if parsed_data.get("basic_details"):
        basic_df = pd.DataFrame([parsed_data["basic_details"]])
        dataframes["Basic Details"] = basic_df

    if parsed_data.get("education"):
        education_df = pd.DataFrame(parsed_data["education"])
        dataframes["Education"] = education_df

    if parsed_data.get("experience"):
        # convert achievements to string for csv
        experience_data = []
        for exp in parsed_data["experience"]:
            exp_copy = exp.copy()
            if exp_copy.get("key_achievements"):
                exp_copy["key_achievements"] = "; ".join(exp_copy["key_achievements"])
            experience_data.append(exp_copy)
        experience_df = pd.DataFrame(experience_data)
        dataframes["Experience"] = experience_df

    if parsed_data.get("skills"):
        skills_data = []
        skills = parsed_data["skills"]

        if skills.get("technical_skills"):
            for skill in skills["technical_skills"]:
                skills_data.append(
                    {"category": "Technical", "skill": skill, "proficiency": "N/A"}
                )

        if skills.get("soft_skills"):
            for skill in skills["soft_skills"]:
                skills_data.append(
                    {"category": "Soft", "skill": skill, "proficiency": "N/A"}
                )

        if skills.get("tools_and_technologies"):
            for tool in skills["tools_and_technologies"]:
                skills_data.append(
                    {"category": "Tools & Tech", "skill": tool, "proficiency": "N/A"}
                )

        if skills.get("languages"):
            for lang in skills["languages"]:
                proficiency = lang.get("proficiency", "N/A")
                if proficiency == "null":
                    proficiency = "N/A"
                skills_data.append(
                    {
                        "category": "Language",
                        "skill": lang.get("language", "N/A"),
                        "proficiency": proficiency,
                    }
                )

        if skills_data:
            skills_df = pd.DataFrame(skills_data)
            dataframes["Skills"] = skills_df

    if parsed_data.get("certifications"):
        certifications_df = pd.DataFrame(parsed_data["certifications"])
        dataframes["Certifications"] = certifications_df

    if parsed_data.get("projects"):
        # convert lists to strings for csv
        projects_data = []
        for proj in parsed_data["projects"]:
            proj_copy = proj.copy()
            if proj_copy.get("technologies"):
                proj_copy["technologies"] = "; ".join(proj_copy["technologies"])
            if proj_copy.get("key_features"):
                proj_copy["key_features"] = "; ".join(proj_copy["key_features"])
            projects_data.append(proj_copy)
        projects_df = pd.DataFrame(projects_data)
        dataframes["Projects"] = projects_df

    return dataframes
