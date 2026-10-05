# Offline AI Resume Analyzer

A Streamlit-based web application that analyzes resumes, identifies skills, and suggests improvements **entirely offline** using Natural Language Processing (NLP) and rule-based AI. 

No APIs, no internet, and no data leaving your machine!

## Features
- 📄 Upload PDF resumes.
- 🧠 **Extracts skills** using a local skills database and regex matching.
- 💬 **NLP Analysis** using `spaCy` to check for strong action verbs.
- 💡 **Provides feedback** based on ATS best practices (word count, quantifiable metrics, contact info).
- 🚫 **100% Private:** Runs totally offline.

## Setup

1. **Install Dependencies:**
   Make sure you have Python installed, then open your terminal and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download the NLP Model:**
   This app uses `spaCy` for Natural Language Processing. You need to download the English language model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Run the Application:**
   Start the Streamlit server by running:
   ```bash
   streamlit run app.py
   ```
   The application will automatically open in your default web browser (usually at http://localhost:8501).
