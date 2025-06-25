import re
import spacy
from typing import Dict, List, Any
import nltk
from nltk.corpus import stopwords
from pdfminer.high_level import extract_text
import docx2txt


class AdvancedResumeParser:
    def __init__(self, debug=False):
        self.debug = debug
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = spacy.blank("en")

        # download nltk data if needed
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")

        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords")

        self.stop_words = set(stopwords.words("english"))

        # basic section patterns
        self.section_patterns = {
            "education": r"(?i)(education|academic|qualification|degree|university|college|school)",
            "experience": r"(?i)(experience|employment|work|career|professional|job)",
            "skills": r"(?i)(skills|technical|competencies|technologies|tools|programming)",
            "certifications": r"(?i)(certification|certificate|license|credential)",
            "projects": r"(?i)(projects|portfolio|work samples|achievements)",
        }

    def extract_text_from_file(self, file_path: str) -> str:
        file_path_lower = file_path.lower()

        if file_path_lower.endswith(".pdf"):
            return extract_text(file_path)
        elif file_path_lower.endswith(".docx"):
            return docx2txt.process(file_path)
        else:
            raise ValueError("unsupported file format")

    def find_sections(self, text: str) -> Dict[str, str]:
        sections = {}
        lines = text.split("\n")

        current_section = None
        current_content = []

        # flexible section patterns
        section_patterns = {
            "education": r"(?i)^(education|academic|qualifications?|academic\s+scores?)$",
            "experience": r"(?i)^(experience|work\s+experience|employment|professional\s+experience)$",
            "skills": r"(?i)^(technical\s+skills?|skills?|competencies|technologies)$",
            "projects": r"(?i)^(projects?|portfolio|work\s+samples?)$",
            "achievements": r"(?i)^(achievements?|awards?|honors?|accomplishments?)$",
            "certifications": r"(?i)^(certifications?|certificates?|licenses?)$",
            "activities": r"(?i)^(extra.curricular\s+activities|activities|extracurricular)$",
            "courses": r"(?i)^(relevant\s+courses?|coursework|courses?)$",
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # check if line is section header
            section_found = None

            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line):
                    section_found = section_name
                    break

            if section_found:
                # save previous section
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content)

                current_section = section_found
                current_content = []
                if self.debug:
                    print(f"found section header: {section_found} -> {line}")
            else:
                if current_section:
                    current_content.append(line)

        # save last section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content)

        return sections

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        education_entries = []
        lines = text.split("\n")

        # for academic scores format, use special parser
        if "academic scores" in text.lower():
            return self._extract_academic_scores(text)

        # standard education parsing
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # look for institutions
            if re.search(r"(?i)(institute|university|college|school|bits)", line):
                entry = {"institution": line}

                # look ahead for related info
                j = i + 1
                while j < len(lines) and j < i + 6:
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue

                    # stop if we hit another institution
                    if (
                        re.search(
                            r"(?i)(institute|university|college|school)", next_line
                        )
                        and j > i + 1
                    ):
                        break

                    # extract degree and major
                    degree_patterns = [
                        r"(?i)(be|bachelor|b\.tech|b\.e\.?|master|m\.tech|phd|diploma)\s+(?:in\s+|of\s+)?([^;,\n]+)",
                        r"(?i)(undergraduate|graduate)\s+(?:in\s+)?([^;,\n]+)",
                    ]

                    for pattern in degree_patterns:
                        match = re.search(pattern, next_line)
                        if match:
                            entry["degree"] = match.group(1).strip()
                            entry["major"] = match.group(2).strip()
                            break

                    # extract gpa/grade
                    gpa_match = re.search(
                        r"(?i)(?:gpa|grade):\s*([\d.]+(?:/[\d.]+)?)", next_line
                    )
                    if gpa_match:
                        entry["grade"] = gpa_match.group(1)

                    # extract location
                    if re.search(r"(?i)[a-z]+,\s*(?:india|usa|uk|canada)", next_line):
                        entry["location"] = next_line

                    # extract dates
                    date_match = re.search(
                        r"(\w+\s+\d{4})\s*[–-]\s*(\d{4}|present|\w+\s+\d{4})",
                        next_line,
                        re.IGNORECASE,
                    )
                    if date_match:
                        start_year = re.search(r"\d{4}", date_match.group(1))
                        if start_year:
                            entry["start_year"] = start_year.group()

                        if (
                            "expected" in next_line.lower()
                            or "present" in next_line.lower()
                        ):
                            entry["end_year"] = "present"
                        else:
                            end_year = re.search(r"\d{4}", date_match.group(2))
                            if end_year:
                                entry["end_year"] = end_year.group()

                    j += 1

                if entry:
                    education_entries.append(entry)
                i = j - 1

            i += 1

        return education_entries

    def _extract_academic_scores(self, text: str) -> List[Dict[str, Any]]:
        education_entries = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 10th/12th grade pattern
            if re.search(r"(?i)(\d+)(?:th|st|nd|rd)\s*-\s*([\d.]+%?)", line):
                match = re.search(
                    r"(?i)(\d+)(?:th|st|nd|rd)\s*-\s*([\d.]+%?)\s*\((\d{4})\)", line
                )
                if match:
                    grade_level = match.group(1)
                    percentage = match.group(2)
                    year = match.group(3)

                    if grade_level == "10":
                        degree = "Secondary School"
                    elif grade_level == "12":
                        degree = "Senior Secondary"
                    else:
                        degree = f"Grade {grade_level}"

                    education_entries.append(
                        {
                            "degree": degree,
                            "grade": percentage,
                            "end_year": year,
                            "institution": "Not specified",
                        }
                    )

            # entrance exam patterns
            elif re.search(r"(?i)(jee|bitsat|neet)", line):
                match = re.search(
                    r"(?i)(jee\s+\w+|bitsat|neet)\s*-\s*(?:air\s*)?([\d/]+)", line
                )
                if match:
                    exam_name = match.group(1)
                    score = match.group(2)
                    year_match = re.search(r"\((\d{4})\)", line)
                    year = year_match.group(1) if year_match else None

                    education_entries.append(
                        {
                            "degree": f"{exam_name} Entrance Exam",
                            "grade": score,
                            "end_year": year,
                            "institution": "Entrance Examination",
                        }
                    )

        return education_entries

    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        experience_entries = []

        lines = text.split("\n")
        current_entry = {}

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # look for job titles
            job_title_patterns = [
                r"(?i)(engineer|developer|analyst|manager|consultant|intern|lead|senior|member|backend|frontend)",
                r"(?i)^[A-Z][A-Z\s,]+$",  # all caps lines
            ]

            is_job_title = False
            for pattern in job_title_patterns:
                if (
                    re.search(pattern, line)
                    and len(line) < 100
                    and not line.startswith("◦")
                ):
                    # avoid false positives
                    if not re.search(r"\d{4}", line) and not re.search(
                        r"(?i)(skills|languages|technologies)", line
                    ):
                        is_job_title = True
                        break

            if is_job_title:
                current_entry = {"title": line}
                if self.debug:
                    print(f"found job title: {line}")

                # look ahead for company details
                j = i + 1
                while j < len(lines) and j < i + 8:
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue

                    # stop if we hit another job title
                    for pattern in job_title_patterns:
                        if (
                            re.search(pattern, next_line)
                            and len(next_line) < 100
                            and not next_line.startswith("◦")
                        ):
                            if not re.search(r"\d{4}", next_line):
                                # found next job, stop here
                                break
                    else:
                        # continue processing this job

                        # extract company name
                        if (
                            not current_entry.get("company")
                            and not re.search(
                                r"\d{4}|present|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
                                next_line,
                                re.IGNORECASE,
                            )
                            and not re.search(
                                r"(?i)(mumbai|delhi|goa|pune|bangalore|india)",
                                next_line,
                            )
                        ):
                            current_entry["company"] = next_line
                            if self.debug:
                                print(f"found company: {next_line}")

                        # extract dates
                        elif re.search(
                            r"(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}",
                            next_line,
                        ):
                            date_match = re.search(
                                r"(\w+\s+\d{4})\s*[-–]\s*(present|\w+\s+\d{4})",
                                next_line,
                                re.IGNORECASE,
                            )
                            if date_match:
                                current_entry["start_date"] = date_match.group(1)
                                current_entry["end_date"] = date_match.group(2)

                            # extract location from same line
                            location_match = re.search(
                                r"(?i)(mumbai|delhi|goa|pune|bangalore|hyderabad|chennai|kolkata)",
                                next_line,
                            )
                            if location_match:
                                current_entry["location"] = location_match.group()

                            if self.debug:
                                print(f"found dates/location: {next_line}")

                        # collect bullet points
                        elif next_line.startswith("◦") or re.search(
                            r"^[•▪▫◦-]\s*", next_line
                        ):
                            if "description" not in current_entry:
                                current_entry["description"] = []

                            # clean bullet point
                            clean_desc = re.sub(r"^[•▪▫◦-]\s*", "", next_line).strip()
                            if clean_desc:
                                current_entry["description"].append(clean_desc)

                        j += 1
                        continue

                    # if we broke out of the for loop, we found next job
                    break

                # save entry if we have enough info
                if current_entry and (
                    "company" in current_entry or "start_date" in current_entry
                ):
                    experience_entries.append(current_entry)
                    current_entry = {}

                i = j - 1

            i += 1

        return experience_entries

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        skills = {"languages": [], "libraries": [], "tools": [], "technologies": []}

        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # look for "category: skills" pattern
            if ":" in line:
                category_match = re.match(r"([^:]+):\s*(.+)", line)
                if category_match:
                    category = category_match.group(1).strip().lower()
                    skills_text = category_match.group(2).strip()

                    # extract skills in braces with proficiency levels
                    brace_matches = re.findall(
                        r"\{([^}]+)\}\s*\(([^)]+)\)", skills_text
                    )

                    extracted_skills = []
                    if brace_matches:
                        # format: {python, c, c++} (proficient) - extract only skill names
                        for skills_group, proficiency in brace_matches:
                            skills_list = [
                                skill.strip() for skill in skills_group.split(",")
                            ]
                            extracted_skills.extend(skills_list)
                    else:
                        # simple format: languages: python, golang, c, java
                        skills_list = [
                            skill.strip() for skill in skills_text.split(",")
                        ]
                        extracted_skills.extend(skills_list)

                    # categorize skills
                    if "language" in category:
                        skills["languages"] = extracted_skills
                    elif "librar" in category:
                        skills["libraries"] = extracted_skills
                    elif "tool" in category:
                        skills["tools"] = extracted_skills
                    elif "technolog" in category:
                        skills["technologies"] = extracted_skills
                    else:
                        # if category doesn't match, put in technologies
                        skills["technologies"] = extracted_skills

        return skills

    def extract_certifications(self, text: str) -> List[Dict[str, Any]]:
        certifications = []

        cert_patterns = [
            r"(?i)(aws|azure|google cloud|gcp)\s+(certified|certification)",
            r"(?i)(cisco|oracle|microsoft|adobe)\s+(certified|certification)",
            r"(?i)(pmp|cissp|cisa|cism|comptia)",
            r"(?i)(certified|certification)\s+.{5,50}",
        ]

        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            for pattern in cert_patterns:
                if re.search(pattern, line):
                    # extract year if present
                    year_match = re.search(r"(19|20)\d{2}", line)
                    year = year_match.group() if year_match else None

                    certifications.append({"name": line, "year": year})
                    break

        return certifications

    def extract_projects(self, text: str) -> List[Dict[str, Any]]:
        projects = []

        lines = text.split("\n")
        current_entry = {}

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # look for project titles
            if not line.startswith("◦") and re.search(
                r"(?i)(transformer|assignment|project|application|system)", line
            ):
                current_entry = {"name": line}

                # look for github link
                github_match = re.search(r"github[/.]([^\s]+)", line, re.IGNORECASE)
                if not github_match and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    github_match = re.search(
                        r"github[/.]([^\s]+)", next_line, re.IGNORECASE
                    )

                if github_match:
                    current_entry["github"] = f"github.com/{github_match.group(1)}"

                # collect description points
                description_points = []
                j = i + 1
                while j < len(lines):
                    desc_line = lines[j].strip()
                    if not desc_line:
                        j += 1
                        continue

                    if desc_line.startswith("◦"):
                        description_points.append(desc_line[1:].strip())
                        j += 1
                    elif re.search(
                        r"(?i)(transformer|assignment|project|open source)", desc_line
                    ) and not desc_line.startswith("◦"):
                        # start of next project
                        break
                    else:
                        j += 1

                if description_points:
                    current_entry["description"] = description_points

                # extract technologies from description
                technologies = set()
                for desc in description_points:
                    # common tech patterns
                    tech_matches = re.findall(
                        r"(?i)(pytorch|numpy|pandas|resnet|cifar|ucf101|s4|state-space|attention|transformer)",
                        desc,
                    )
                    technologies.update([tech.lower() for tech in tech_matches])

                if technologies:
                    current_entry["technologies"] = list(technologies)

                if current_entry:
                    projects.append(current_entry)

                i = j - 1

            i += 1

        return projects

    def extract_achievements(self, text: str) -> List[Dict[str, Any]]:
        achievements = []

        lines = text.split("\n")
        achievement_dates = []

        # first pass: collect date lines
        for line in lines:
            line = line.strip()
            if re.match(
                r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}",
                line,
                re.IGNORECASE,
            ):
                achievement_dates.append(line)

        # second pass: extract achievements
        date_index = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # skip location and date lines
            if re.search(r"(?i)(pune|india|goa)", line) or re.match(
                r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}",
                line,
                re.IGNORECASE,
            ):
                continue

            # look for achievement entries
            if re.search(r"(?i)(1st place|top|scored|awarded|state)", line):
                achievement = {"description": line}

                # try to extract date from line
                date_match = re.search(
                    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}",
                    line,
                    re.IGNORECASE,
                )
                if date_match:
                    achievement["date"] = date_match.group()
                elif date_index < len(achievement_dates):
                    # use corresponding date from collected dates
                    achievement["date"] = achievement_dates[date_index]
                    date_index += 1

                # try to extract year if no date found
                year_match = re.search(r"\b(20\d{2})\b", line)
                if year_match and "date" not in achievement:
                    achievement["year"] = year_match.group()

                achievements.append(achievement)

        return achievements

    def parse_resume_full(self, text: str) -> Dict[str, Any]:
        sections = self.find_sections(text)

        # debug: print sections found
        if self.debug:
            print("\n=== DEBUG: sections found ===")
            for section_name, section_content in sections.items():
                print(f"{section_name}: {len(section_content)} characters")
                print(f"  preview: {section_content[:100]}...")
            print("=== end sections debug ===\n")

        result = {
            "education": [],
            "experience": [],
            "skills": {},
            "certifications": [],
            "projects": [],
            "achievements": [],
        }

        # parse each section
        if "education" in sections:
            result["education"] = self.extract_education(sections["education"])

        if "experience" in sections:
            result["experience"] = self.extract_experience(sections["experience"])

        if "skills" in sections:
            result["skills"] = self.extract_skills(sections["skills"])
        else:
            # fallback: extract from entire text
            result["skills"] = self.extract_skills(text)

        if "certifications" in sections:
            result["certifications"] = self.extract_certifications(
                sections["certifications"]
            )

        if "projects" in sections:
            result["projects"] = self.extract_projects(sections["projects"])
        else:
            # fallback: extract from entire text
            result["projects"] = self.extract_projects(text)

        if "achievements" in sections:
            result["achievements"] = self.extract_achievements(sections["achievements"])

        return result

    def parse_resume_file(self, file_path: str) -> Dict[str, Any]:
        try:
            text = self.extract_text_from_file(file_path)

            # debug: print extracted text
            if self.debug:
                print("\n=== DEBUG: extracted text ===")
                print(f"text length: {len(text)} characters")
                print("first 500 characters:")
                print(text[:500])
                print("\n=== end debug ===\n")

            return self.parse_resume_full(text)
        except Exception as e:
            print(f"error parsing file {file_path}: {e}")
            return {
                "education": [],
                "experience": [],
                "skills": {},
                "certifications": [],
                "projects": [],
                "achievements": [],
                "error": str(e),
            }


# test parser
if __name__ == "__main__":
    import sys

    # check for debug flag
    debug_mode = "--debug" in sys.argv or "-d" in sys.argv
    if debug_mode:
        sys.argv = [arg for arg in sys.argv if arg not in ["--debug", "-d"]]

    parser = AdvancedResumeParser(debug=debug_mode)

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "files/soham_resume.pdf"

    print(f"parsing resume: {file_path}")
    result = parser.parse_resume_file(file_path)

    print("\n=== parsed resume data ===")
    print(f"education: {len(result['education'])} entries")
    for edu in result["education"]:
        print(f"  - {edu}")

    print(f"\nexperience: {len(result['experience'])} entries")
    for exp in result["experience"]:
        print(f"  - {exp}")

    print(f"\nskills: {result['skills']}")

    print(f"\ncertifications: {len(result['certifications'])} found")
    for cert in result["certifications"]:
        print(f"  - {cert}")

    print(f"\nprojects: {len(result['projects'])} found")
    for proj in result["projects"]:
        print(f"  - {proj}")

    print(f"\nachievements: {len(result['achievements'])} found")
    for achievement in result["achievements"]:
        print(f"  - {achievement}")
