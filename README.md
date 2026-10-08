# CareerPath.AI - Offline AI Resume Analyzer & Skill Assessment

A modern Streamlit web application that analyzes resumes, calculates ATS compatibility scores, suggests improvements, and provides proctored technical skill mock tests. Integrated with **MongoDB** for user accounts, scan history, and test score tracking, styled with a polished UI/UX using the signature `#ff4b4b` theme.

---

## 🚀 Key Features

- 🔐 **Authentication System**:
  - Secure user registration and login with `bcrypt` password encryption.
  - Quick demo guest mode for testing.
  - Personalized user sessions and sidebar profile widget.

- 🍃 **MongoDB Database Integration**:
  - **`users`**: Secure account credentials, profiles, and timestamps.
  - **`resume_scans`**: Extracted technical skills, ATS scores, strengths, and recommendations.
  - **`mock_tests`**: Proctored exam scores, percentages, and skill breakdown.
  - Live database health and statistics monitor.

- 📄 **Offline AI Resume Analyzer**:
  - Local text extraction from PDF resumes using `PyPDF2`.
  - Skill extraction across 40+ high-demand tech stacks.
  - Natural Language Processing (NLP) with `spaCy` to verify strong action verbs.
  - ATS compatibility score calculation (0–100%).

- 📝 **Proctored Mock Test**:
  - Customized 15-question technical quiz generated dynamically from detected skills.
  - Anti-cheat proctoring: fullscreen enforcement, tab-switch monitoring, copy/paste prevention, and AI webcam monitoring (phone & head-turn detection).

- 📊 **User History & Analytics Dashboard**:
  - Review previous resume analyses and historical ATS scores.
  - Track quiz score progression over time.

---

## 🛠️ Setup & Installation

### 1. Install Dependencies
Make sure you have Python 3.10+ installed:
```bash
pip install -r requirements.txt
```

### 2. Download the English NLP Model
Download the `spaCy` language model:
```bash
python -m spacy download en_core_web_sm
```

### 3. Ensure MongoDB is Running
CareerPath.AI connects by default to `mongodb://localhost:27017/`.
To customize the connection string, set the `MONGO_URI` environment variable:
```bash
# Optional: Set custom MongoDB URI
export MONGO_URI="mongodb://localhost:27017/"
```

### 4. Run the Application
Start the Streamlit application:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.
