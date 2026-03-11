import streamlit as st
import pdfplumber
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import re

# -------------------------
# PAGE SETTINGS
# -------------------------

st.set_page_config(page_title="AI Resume Scanner", layout="wide")

# -------------------------
# DARK THEME
# -------------------------

st.markdown("""
<style>
.stApp {
background-color:#0e1117;
color:white;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# LOGIN SYSTEM
# -------------------------

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("AI Recruiter Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        if user == "recruiter" and pwd == "recruiter123":

            st.session_state.login = True
            st.rerun()

        else:
            st.error("Wrong credentials")

    st.stop()

# -------------------------
# TITLE
# -------------------------

st.title("AI Resume Scanner & Recruiter Dashboard")

st.markdown("---")

# -------------------------
# UPLOAD RESUME
# -------------------------

st.header("Step 1 — Upload Resumes")

files = st.file_uploader(
    "Upload resumes",
    type="pdf",
    accept_multiple_files=True
)

# -------------------------
# JOB DESCRIPTION
# -------------------------

st.header("Step 2 — Paste Job Description")

jd = st.text_area("Paste Job Description")

# -------------------------
# FUNCTIONS
# -------------------------

def extract_text(file):

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            t = page.extract_text()

            if t:
                text += t

    return text.lower()


def extract_email(text):

    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

    emails = re.findall(pattern, text)

    if emails:
        return emails[0]

    return "Not Found"


def ats_score(resume, jd):

    r = set(resume.split())
    j = set(jd.split())

    match = r.intersection(j)

    score = int(len(match)/len(j)*100) if len(j)>0 else 0

    return score, match


def ai_suggestions(score):

    if score > 80:
        return "Excellent resume. Minor improvements needed."

    if score > 60:
        return "Add more relevant technical skills and measurable achievements."

    if score > 40:
        return "Resume needs improvement. Add more keywords from job description."

    return "Resume is poorly optimized. Add skills, projects and achievements."


# -------------------------
# ANALYSIS
# -------------------------

results = []

if files and jd:

    for f in files:

        text = extract_text(f)

        score, match = ats_score(text, jd.lower())

        email = extract_email(text)

        results.append({
            "Candidate":f.name,
            "Email":email,
            "ATS Score":score,
            "Matched Skills":len(match)
        })

# -------------------------
# DASHBOARD
# -------------------------

if len(results)>0:

    df = pd.DataFrame(results)

    df = df.sort_values(by="ATS Score", ascending=False)

    # -------------------------
    # TOP CANDIDATE
    # -------------------------

    top = df.iloc[0]["Candidate"]

    st.success("Top Candidate: " + top)

    # -------------------------
    # RANKING TABLE
    # -------------------------

    st.subheader("Candidate Ranking")

    st.dataframe(df)

    st.markdown("---")

    # -------------------------
    # FILTER
    # -------------------------

    minscore = st.slider("Minimum ATS Score",0,100,50)

    filtered = df[df["ATS Score"]>=minscore]

    st.dataframe(filtered)

    st.markdown("---")

    # -------------------------
    # COMPARISON GRAPH
    # -------------------------

    st.subheader("Candidate Comparison")

    bar = go.Figure([go.Bar(x=df["Candidate"], y=df["ATS Score"])])

    st.plotly_chart(bar)

    st.markdown("---")

    # -------------------------
    # INDIVIDUAL ANALYSIS
    # -------------------------

    st.header("Detailed Resume Analysis")

    for i,row in df.iterrows():

        st.subheader(row["Candidate"])

        score = row["ATS Score"]

        st.write("Email:", row["Email"])

        # color indicator

        if score>75:
            st.success(f"ATS Score: {score}")

        elif score>50:
            st.warning(f"ATS Score: {score}")

        else:
            st.error(f"ATS Score: {score}")

        # animated progress

        st.progress(score)

        # gauge

        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text":"ATS Score"},
            gauge={"axis":{"range":[0,100]}}
        ))

        st.plotly_chart(gauge, key="g"+str(i))

        # pie chart

        pie = go.Figure(data=[go.Pie(
            labels=["Matched Skills","Missing Skills"],
            values=[row["Matched Skills"],20]
        )])

        st.plotly_chart(pie, key="p"+str(i))

        # heatmap

        fig, ax = plt.subplots()

        sns.heatmap([[row["Matched Skills"]]],
                    annot=True,
                    cmap="YlGnBu",
                    ax=ax)

        st.pyplot(fig)

        # AI suggestions

        st.info("AI Suggestions: " + ai_suggestions(score))

        st.markdown("---")