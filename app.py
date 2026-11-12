import streamlit as st
import pdfplumber
import docx
import pandas as pd
import re

st.set_page_config(
    page_title="Resume Parsing & Candidate Ranking",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Resume Parsing and Candidate Ranking")
st.write("Upload resumes and rank candidates according to job requirements.")

# Skills database
SKILLS = [
    "python", "java", "c++", "sql", "machine learning",
    "deep learning", "data science", "excel", "power bi",
    "tableau", "html", "css", "javascript", "aws",
    "communication", "leadership", "statistics"
]

# Extract text from PDF
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# Extract text from DOCX
def read_docx(file):
    document = docx.Document(file)
    return "\n".join(p.text for p in document.paragraphs)

# Extract text from TXT
def read_txt(file):
    return file.read().decode("utf-8", errors="ignore")

# Read uploaded resume
def extract_text(file):
    if file.name.lower().endswith(".pdf"):
        return read_pdf(file)
    elif file.name.lower().endswith(".docx"):
        return read_docx(file)
    elif file.name.lower().endswith(".txt"):
        return read_txt(file)
    return ""
def extract_details(text):

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    name = "Not found"

    if lines:
        first_line = lines[0]

        if not any(char.isdigit() for char in first_line):
            name = first_line

    email = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+', text
    )

    phone = re.search(
        r'\+?\d[\d\s-]{8,14}\d', text
    )

    found_skills = [
        skill for skill in SKILLS
        if skill in text.lower()
    ]

    education_list = [
        "BSc", "B.Sc", "Bachelor of Science",
        "BCom", "B.Com", "Bachelor of Commerce",
        "BA", "B.A", "Bachelor of Arts",
        "BE", "B.E", "BTech", "B.Tech",
        "MBA", "MCA", "MSc", "M.Sc",
        "MCom", "M.Com", "PhD", "Diploma"
    ]

    education = next(
        (
            degree for degree in education_list
            if degree.lower() in text.lower()
        ),
        "Not found"
    )
    experience = re.search(
    r'\d+(?:\.\d+)?\s*\+?\s*(?:years?|yrs?)',
    text.lower()
)

    experience = experience.group(0) if experience else "Not found" 

    return {
    "Name": name,
    "Email": email.group(0) if email else "Not found",
    "Phone": phone.group(0) if phone else "Not found",
    "Education": education,
    "Experience": experience,
    "Skills": found_skills
}
# Sidebar
st.sidebar.header("Job Requirements")

job_description = st.sidebar.text_area(
    "Enter job description",
    placeholder="Enter the skills required for the job..."
)

required_skills = [
    skill.strip().lower()
    for skill in job_description.split(",")
    if skill.strip()
]

st.sidebar.write("Required skills:", required_skills)
# Resume upload
st.header("Upload Candidate Resumes")

uploaded_files = st.file_uploader(
    "Upload multiple resumes",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if uploaded_files and required_skills:

    results = []

    for file in uploaded_files:

        text = extract_text(file)
        details = extract_details(text)

        matched = [
            skill for skill in required_skills
            if skill in details["Skills"]
        ]

        missing = [
            skill for skill in required_skills
            if skill not in details["Skills"]
        ]

        score = (
            len(matched) / len(required_skills)
        ) * 100

        results.append({
    "Candidate": details["Name"],
    "Resume File": file.name,
    "Email": details["Email"],
            "Phone": details["Phone"],
            "Education": details["Education"],
            "Experience": details["Experience"],
            "Matched Skills": ", ".join(matched),
            "Missing Skills": ", ".join(missing),
            "Match Score": round(score, 2)
        })

    df = pd.DataFrame(results)

    df = df.sort_values(
        by="Match Score",
        ascending=False
    )

    df.insert(
        0,
        "Rank",
        range(1, len(df) + 1)
    )

    st.success("Resume analysis completed!") 

    st.subheader("Candidate Ranking")
    st.subheader("📊 Dashboard Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Resumes",
        len(df)
    )

    col2.metric(
        "Top Candidate",
        df.iloc[0]["Candidate"]
    )

    col3.metric(
        "Average Match Score",
        f"{df['Match Score'].mean():.1f}%"
    )
    st.dataframe(df, use_container_width=True)

    st.subheader("Ranking Chart")
    st.bar_chart(
        df.set_index("Candidate")["Match Score"]
    )

    st.download_button(
        "Download Candidate Results",
        df.to_csv(index=False),
        "candidate_ranking.csv",
        "text/csv"
    )

elif uploaded_files:
    st.warning("Please enter job requirements first.")

else:
    st.info("Upload resumes to begin candidate analysis.")