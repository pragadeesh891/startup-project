import streamlit as st
from PyPDF2 import PdfReader
import re
import spacy
from collections import Counter
import random

# Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "main"
if "analyzed_skills" not in st.session_state:
    st.session_state.analyzed_skills = []
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

def reset_quiz():
    st.session_state.page = "main"
    st.session_state.quiz_questions = []
    st.session_state.current_q_index = 0
    st.session_state.score = 0
    st.session_state.analysis_results = None

# Try to load the English NLP model
@st.cache_resource
def load_nlp_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.error("The NLP model is missing. Please run: `python -m spacy download en_core_web_sm` in your terminal.")
        return None

nlp = load_nlp_model()

SKILLS_DB = [
    "Python", "Java", "C++", "C#", "JavaScript", "HTML", "CSS", "React", "Angular", "Vue",
    "Node.js", "Express", "Django", "Flask", "SQL", "MySQL", "PostgreSQL", "MongoDB",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "GitHub", "Linux", "Unix",
    "Machine Learning", "Deep Learning", "Data Science", "Artificial Intelligence", "NLP",
    "Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management",
    "Project Management", "Agile", "Scrum", "Data Analysis", "Excel", "Tableau", "Power BI"
]
SKILLS_DB_LOWER = [skill.lower() for skill in SKILLS_DB]

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
    return text

def analyze_resume_local(text):
    results = {"skills": [], "suggestions": [], "strengths": []}
    if not text.strip(): return results
    text_lower = text.lower()
    
    found_skills = []
    for skill, skill_lower in zip(SKILLS_DB, SKILLS_DB_LOWER):
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', text_lower):
            found_skills.append(skill)
    results["skills"] = found_skills

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    has_email = bool(re.search(email_pattern, text))
    has_phone = bool(re.search(phone_pattern, text))
    if not has_email: results["suggestions"].append("Add a professional email address.")
    if not has_phone: results["suggestions"].append("Add a phone number so recruiters can reach you.")

    word_count = len(text.split())
    if word_count < 200:
        results["suggestions"].append(f"Your resume is quite short ({word_count} words). Consider adding more details.")
    elif word_count > 1000:
        results["suggestions"].append(f"Your resume is very long ({word_count} words). Aim for conciseness.")
    else:
        results["strengths"].append(f"Good resume length ({word_count} words).")

    has_metrics = bool(re.search(r'\d+%|\$\d+|\b\d+\b', text))
    if has_metrics:
        results["strengths"].append("You used numbers/metrics, which is great for showing measurable impact.")
    else:
        results["suggestions"].append("Include quantifiable metrics (e.g., %, $, numbers).")

    if nlp:
        doc = nlp(text)
        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
        strong_verbs = {"develop", "manage", "create", "lead", "design", "build", "improve", "increase"}
        found_strong_verbs = set(verbs).intersection(strong_verbs)
        if found_strong_verbs:
            results["strengths"].append(f"Good use of strong action verbs (e.g., {', '.join(list(found_strong_verbs)[:3])}).")
        else:
            results["suggestions"].append("Start your bullet points with strong action verbs like 'Developed' or 'Managed'.")
            
    return results

MCQ_DB = {
    "Python": [
        {"q": "Which data structure is immutable in Python?", "options": ["List", "Dictionary", "Set", "Tuple"], "ans": 3},
        {"q": "What is the output of 2 ** 3?", "options": ["6", "8", "9", "12"], "ans": 1},
        {"q": "Which keyword is used for a function in Python?", "options": ["def", "function", "fun", "define"], "ans": 0},
        {"q": "What is the GIL in Python?", "options": ["Global Interpreter Lock", "General Interface Layer", "Global Interaction Link", "General Interpreter Lock"], "ans": 0},
    ],
    "Java": [
        {"q": "Which of these is NOT an OOP concept in Java?", "options": ["Inheritance", "Compilation", "Polymorphism", "Encapsulation"], "ans": 1},
        {"q": "What is the size of int in Java?", "options": ["16 bit", "32 bit", "64 bit", "Depends on OS"], "ans": 1},
        {"q": "Which keyword is used to inherit a class?", "options": ["implements", "inherits", "extends", "super"], "ans": 2},
    ],
    "JavaScript": [
        {"q": "Which keyword is used to declare a block-scoped variable?", "options": ["var", "let", "constant", "int"], "ans": 1},
        {"q": "What is the result of '2' + 2 in JS?", "options": ["4", "22", "NaN", "Error"], "ans": 1},
        {"q": "Which method adds an element to the end of an array?", "options": ["push()", "pop()", "shift()", "unshift()"], "ans": 0},
    ],
    "React": [
        {"q": "What hook is used to manage state?", "options": ["useEffect", "useState", "useContext", "useReducer"], "ans": 1},
        {"q": "What is the Virtual DOM?", "options": ["A direct copy of the real DOM", "A lightweight representation of the real DOM", "A browser feature", "A React plugin"], "ans": 1},
        {"q": "How do you pass data to child components?", "options": ["State", "Props", "Context", "Redux"], "ans": 1},
    ],
    "SQL": [
        {"q": "Which command extracts data from a database?", "options": ["GET", "EXTRACT", "SELECT", "PULL"], "ans": 2},
        {"q": "Which SQL statement is used to update data in a database?", "options": ["UPDATE", "MODIFY", "SAVE", "CHANGE"], "ans": 0},
        {"q": "What does SQL stand for?", "options": ["Structured Query Language", "Strong Question Language", "Structured Question Language", "Sequential Query Language"], "ans": 0},
    ],
    "Machine Learning": [
        {"q": "Which of these is an unsupervised learning algorithm?", "options": ["Linear Regression", "Decision Tree", "K-Means Clustering", "Logistic Regression"], "ans": 2},
        {"q": "What does overfitting mean?", "options": ["Model performs well on training data but poorly on unseen data", "Model performs poorly on both", "Model performs well on test data only", "Model training is too fast"], "ans": 0},
    ],
    "Docker": [
        {"q": "What file is used to build a Docker image?", "options": ["DockerFile", "docker-compose.yml", "Dockerfile", "ContainerFile"], "ans": 2},
        {"q": "What is the difference between an image and a container?", "options": ["Image is running, container is static", "Image is static, container is a running instance", "They are the same", "Container is for Linux, image is for Windows"], "ans": 1},
    ],
    "AWS": [
        {"q": "Which AWS service is used for scalable object storage?", "options": ["EC2", "RDS", "S3", "Lambda"], "ans": 2},
        {"q": "What does IAM stand for in AWS?", "options": ["Identity and Access Management", "Internal Application Monitoring", "Instance And Machine", "Internet Access Module"], "ans": 0},
    ],
    "General": [
        {"q": "What does HTTP stand for?", "options": ["HyperText Transfer Protocol", "HyperText Transmission Protocol", "Hyper Transfer Text Protocol", "Hyperlink Transfer Technology Protocol"], "ans": 0},
        {"q": "Which data structure uses LIFO (Last In First Out)?", "options": ["Queue", "Stack", "Tree", "Graph"], "ans": 1},
        {"q": "What is the time complexity of binary search?", "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"], "ans": 2},
        {"q": "What does API stand for?", "options": ["Application Programming Interface", "Applied Protocol Interface", "Application Process Integration", "Automated Programming Interface"], "ans": 0},
        {"q": "Which design pattern ensures a class only has one instance?", "options": ["Factory", "Observer", "Singleton", "Decorator"], "ans": 2},
        {"q": "What is a primary key in a database?", "options": ["A key that allows null values", "A unique identifier for a record", "A key used for encryption", "A foreign key in another table"], "ans": 1},
        {"q": "Which sorting algorithm is typically the fastest for large datasets?", "options": ["Bubble Sort", "Insertion Sort", "Selection Sort", "Quick Sort"], "ans": 3},
        {"q": "What does DRY stand for in software engineering?", "options": ["Don't Repeat Yourself", "Do Repeat Yourself", "Data Resource Yield", "Deploy Rapidly Yearly"], "ans": 0},
        {"q": "What is the purpose of Git?", "options": ["Version Control", "Database Management", "Web Hosting", "Code Compilation"], "ans": 0},
        {"q": "What is CI/CD?", "options": ["Continuous Integration / Continuous Deployment", "Code Inspection / Code Delivery", "Constant Iteration / Constant Design", "Code Integration / Constant Deployment"], "ans": 0},
        {"q": "Which of these is a NoSQL database?", "options": ["MySQL", "PostgreSQL", "MongoDB", "Oracle"], "ans": 2},
        {"q": "What is a closure in programming?", "options": ["A function inside another function that retains access to its parent scope", "A way to end a loop", "A method to close a database connection", "A syntax error"], "ans": 0},
        {"q": "What does CSS stand for?", "options": ["Cascading Style Sheets", "Computer Style Sheets", "Creative Style Sheets", "Colorful Style Sheets"], "ans": 0},
        {"q": "Which HTTP method is used to submit data to be processed?", "options": ["GET", "POST", "DELETE", "HEAD"], "ans": 1},
        {"q": "What is JSON?", "options": ["Java Standard Object Notation", "JavaScript Object Notation", "JavaScript Standard Output Network", "Java Serialized Object Network"], "ans": 1},
    ]
}

def generate_mcq_test(skills, num=15):
    pool = []
    for skill in skills:
        if skill in MCQ_DB:
            pool.extend([{"skill": skill, **q} for q in MCQ_DB[skill]])
            
    # fill remaining with general
    pool.extend([{"skill": "General", **q} for q in MCQ_DB["General"]])
    
    # remove duplicates
    seen = set()
    unique_pool = []
    for q in pool:
        if q["q"] not in seen:
            unique_pool.append(q)
            seen.add(q["q"])
            
    random.shuffle(unique_pool)
    return unique_pool[:num]

import streamlit.components.v1 as components

def enable_proctoring():
    st.markdown("""
        <style>
            header[data-testid="stHeader"] {visibility: hidden;}
            footer {visibility: hidden;}
            .stApp {
                -webkit-user-select: none;
                -ms-user-select: none;
                user-select: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    js_code = """
    <script>
        const parentDoc = window.parent.document;
        const parentWin = window.parent;

        if (!parentWin.proctoringEnabled) {
            parentWin.proctoringEnabled = true;

            parentWin.handleContextMenu = (e) => e.preventDefault();
            parentWin.handleCopy = (e) => { e.preventDefault(); alert("Copying is disabled during the exam."); };
            parentWin.handlePaste = (e) => { e.preventDefault(); alert("Pasting is disabled during the exam."); };
            
            parentWin.handleVisibility = () => {
                if (parentDoc.hidden) {
                    alert("⚠️ PROCTORING WARNING: You switched tabs or minimized the window! This is a violation of exam rules.");
                }
            };

            parentDoc.addEventListener('contextmenu', parentWin.handleContextMenu);
            parentDoc.addEventListener('copy', parentWin.handleCopy);
            parentDoc.addEventListener('paste', parentWin.handlePaste);
            parentDoc.addEventListener('visibilitychange', parentWin.handleVisibility);

            parentWin.onbeforeunload = function() {
                return "You are in a proctored exam. Are you sure you want to exit?";
            };

            // Inject TFJS, COCO-SSD and BlazeFace for AI Detection
            if (!parentDoc.getElementById('tfjs-script')) {
                const tfjs = parentDoc.createElement('script');
                tfjs.id = 'tfjs-script';
                tfjs.src = 'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs';
                parentDoc.head.appendChild(tfjs);
                
                const cocossd = parentDoc.createElement('script');
                cocossd.id = 'cocossd-script';
                cocossd.src = 'https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd';
                parentDoc.head.appendChild(cocossd);
                
                const blazeface = parentDoc.createElement('script');
                blazeface.id = 'blazeface-script';
                blazeface.src = 'https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface';
                parentDoc.head.appendChild(blazeface);
            }

            // Inject the execution script directly into the parent's head to bypass iframe fullscreen blocks
            if (!parentDoc.getElementById("proctor-script")) {
                const script = parentDoc.createElement("script");
                script.id = "proctor-script";
                script.innerHTML = `
                    window.startProctoredExam = function() {
                        const btn = document.getElementById('proctorBtn');
                        btn.innerText = "Requesting permissions...";
                        btn.disabled = true;

                        // 1. Request Screen Recording FIRST
                        navigator.mediaDevices.getDisplayMedia({
                            video: { mediaSource: "screen" }
                        }).then(screenStream => {
                            // 2. Request Camera SECOND
                            navigator.mediaDevices.getUserMedia({ video: true }).then(cameraStream => {
                                window.examStream = screenStream;
                                window.examCameraStream = cameraStream;
                                
                                const rules = document.getElementById('proctorRules');
                                rules.innerHTML = "<span style='color: #00ff00; font-weight: bold;'>Permissions Granted!</span><br><br>Click the button below to enter fullscreen and begin your exam.";
                                
                                btn.innerText = "Enter Fullscreen & Start Exam";
                                btn.disabled = false;
                                btn.setAttribute('onclick', 'window.finalizeExamStart()');
                                
                            }).catch(err => {
                                alert("You must grant camera permissions for proctoring! Error: " + err.message);
                                btn.innerText = "Grant Permissions";
                                btn.disabled = false;
                            });
                        }).catch(err => {
                            alert("You must grant screen recording permissions to take this exam! Error: " + err.message);
                            btn.innerText = "Grant Permissions";
                            btn.disabled = false;
                        });
                    };

                    window.finalizeExamStart = function() {
                        // 3. Enter Fullscreen (Synchronous and guaranteed to work)
                        const elem = document.documentElement;
                        try {
                            if (elem.requestFullscreen) {
                                elem.requestFullscreen().catch(e => console.log(e));
                            } else if (elem.webkitRequestFullscreen) {
                                elem.webkitRequestFullscreen();
                            } else if (elem.msRequestFullscreen) {
                                elem.msRequestFullscreen();
                            }
                        } catch(e) {
                            console.log("Fullscreen failed", e);
                        }
                        
                        // Setup Screen Recorder
                        window.examRecorder = new MediaRecorder(window.examStream);
                        window.recordedChunks = [];
                        
                        window.examRecorder.ondataavailable = (e) => {
                            if (e.data.size > 0) window.recordedChunks.push(e.data);
                        };
                        
                        window.examRecorder.onstop = () => {
                            const blob = new Blob(window.recordedChunks, { type: 'video/webm' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.style.display = 'none';
                            a.href = url;
                            a.download = 'exam_recording.webm';
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                        };
                        window.examRecorder.start();
                        
                        // Setup Camera Video Feed
                        const video = document.createElement('video');
                        video.id = 'proctorCamera';
                        video.autoplay = true;
                        video.srcObject = window.examCameraStream;
                        video.style.position = 'fixed';
                        video.style.bottom = '20px';
                        video.style.right = '20px';
                        video.style.width = '240px';
                        video.style.borderRadius = '10px';
                        video.style.border = '3px solid #ff4b4b';
                        video.style.boxShadow = '0 4px 10px rgba(0,0,0,0.5)';
                        video.style.zIndex = '999999';
                        document.body.appendChild(video);

                        // Start AI Detection (Phone + Head Turn)
                        if (window.cocoSsd && window.blazeface) {
                            Promise.all([
                                cocoSsd.load(),
                                blazeface.load()
                            ]).then(([cocoModel, faceModel]) => {
                                window.phoneDetectionInterval = setInterval(async () => {
                                    if (video.readyState >= 2) {
                                        // 1. Phone Detection (Lowered threshold and included misclassifications)
                                        const cocoPredictions = await cocoModel.detect(video);
                                        const hasPhone = cocoPredictions.some(p => 
                                            (p.class === 'cell phone' || p.class === 'remote') && p.score > 0.3
                                        );
                                        if (hasPhone) {
                                            alert("⚠️ PROCTORING WARNING: Cell phone or unauthorized device detected on camera! This is a violation.");
                                        }

                                        // 2. Head Turn Detection
                                        const facePredictions = await faceModel.estimateFaces(video, false);
                                        if (facePredictions.length > 0) {
                                            const p = facePredictions[0];
                                            if (p.landmarks && p.landmarks.length >= 3) {
                                                const rx = p.landmarks[0][0]; // Right eye X
                                                const lx = p.landmarks[1][0]; // Left eye X
                                                const nx = p.landmarks[2][0]; // Nose X

                                                const leftToNose = Math.abs(lx - nx);
                                                const noseToRight = Math.abs(nx - rx);
                                                
                                                const turnRatio = leftToNose / (noseToRight || 1);
                                                
                                                if (turnRatio > 3.5 || turnRatio < 0.25) {
                                                    alert("⚠️ PROCTORING WARNING: Please look straight at the screen! Head turning detected.");
                                                }
                                            }
                                        }
                                    }
                                }, 1500); // Check every 1.5 seconds
                            });
                        }

                        const overlay = document.getElementById('proctorOverlay');
                        if (overlay) overlay.remove();
                    };
                `;
                parentDoc.head.appendChild(script);
            }

            // Overlay for Fullscreen and Recording
            const overlay = parentDoc.createElement('div');
            overlay.id = "proctorOverlay";
            overlay.style.position = "fixed";
            overlay.style.top = "0";
            overlay.style.left = "0";
            overlay.style.width = "100vw";
            overlay.style.height = "100vh";
            overlay.style.backgroundColor = "rgba(0,0,0,0.95)";
            overlay.style.color = "white";
            overlay.style.display = "flex";
            overlay.style.flexDirection = "column";
            overlay.style.justifyContent = "center";
            overlay.style.alignItems = "center";
            overlay.style.zIndex = "999999";
            overlay.style.fontFamily = "sans-serif";

            const title = parentDoc.createElement('h2');
            title.innerText = "Proctored Exam Rules";
            title.style.marginBottom = "20px";
            
            const rules = parentDoc.createElement('p');
            rules.id = 'proctorRules';
            rules.innerHTML = "1. Must remain in fullscreen.<br>2. Tab switching is recorded.<br>3. Copy/Paste is disabled.<br>4. Screen and Camera recording is mandatory.";
            rules.style.marginBottom = "30px";
            rules.style.textAlign = "center";
            rules.style.lineHeight = "1.5";

            const btn = parentDoc.createElement('button');
            btn.id = 'proctorBtn';
            btn.innerText = "Grant Permissions";
            btn.style.padding = "15px 30px";
            btn.style.fontSize = "18px";
            btn.style.cursor = "pointer";
            btn.style.backgroundColor = "#ff4b4b";
            btn.style.color = "white";
            btn.style.border = "none";
            btn.style.borderRadius = "5px";

            // Trigger parent function entirely in parent context
            btn.setAttribute('onclick', 'window.startProctoredExam()');

            overlay.appendChild(title);
            overlay.appendChild(rules);
            overlay.appendChild(btn);
            parentDoc.body.appendChild(overlay);
        }
    </script>
    """
    components.html(js_code, height=0, width=0)

def disable_proctoring():
    js_code = """
    <script>
        const parentDoc = window.parent.document;
        const parentWin = window.parent;

        if (parentWin.proctoringEnabled) {
            parentDoc.removeEventListener('contextmenu', parentWin.handleContextMenu);
            parentDoc.removeEventListener('copy', parentWin.handleCopy);
            parentDoc.removeEventListener('paste', parentWin.handlePaste);
            parentDoc.removeEventListener('visibilitychange', parentWin.handleVisibility);
            parentWin.proctoringEnabled = false;

            // Exit Fullscreen safely
            try {
                if (parentDoc.fullscreenElement || parentDoc.webkitFullscreenElement || parentDoc.msFullscreenElement) {
                    if (parentDoc.exitFullscreen) {
                        parentDoc.exitFullscreen().catch(err => console.log(err));
                    } else if (parentDoc.webkitExitFullscreen) {
                        parentDoc.webkitExitFullscreen();
                    } else if (parentDoc.msExitFullscreen) {
                        parentDoc.msExitFullscreen();
                    }
                }
            } catch (e) {
                console.log("Exit fullscreen failed", e);
            }

            if (parentWin.examRecorder && parentWin.examRecorder.state !== 'inactive') {
                parentWin.examRecorder.stop();
            }
            if (parentWin.examStream) {
                parentWin.examStream.getTracks().forEach(track => track.stop());
            }
            
            // Clean up camera and AI intervals
            if (parentWin.examCameraStream) {
                parentWin.examCameraStream.getTracks().forEach(track => track.stop());
            }
            if (parentWin.phoneDetectionInterval) {
                clearInterval(parentWin.phoneDetectionInterval);
            }
            const camVideo = parentDoc.getElementById('proctorCamera');
            if (camVideo) camVideo.remove();
            
            const overlay = parentDoc.getElementById('proctorOverlay');
            if (overlay) overlay.remove();
        }
        parentWin.onbeforeunload = null;
    </script>
    """
    components.html(js_code, height=0, width=0)

# --- Streamlit UI Routing ---
st.set_page_config(page_title="Offline AI Resume Analyzer", page_icon="📄", layout="wide")

if st.session_state.page == "main":
    disable_proctoring()
    st.title("📄 Offline AI Resume Analyzer")
    st.markdown("Analyze your resume locally using **Natural Language Processing (NLP)** and rule-based AI.")
    
    uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type=["pdf"])
    
    if st.button("Analyze Resume", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("Extracting text and analyzing..."):
                resume_text = extract_text_from_pdf(uploaded_file)
                if resume_text.strip():
                    st.session_state.analysis_results = analyze_resume_local(resume_text)
                    st.session_state.analyzed_skills = st.session_state.analysis_results.get("skills", [])
                else:
                    st.error("Could not extract text from this PDF.")
        else:
            st.error("Please upload a PDF resume first.")

    # Show analysis results if they exist
    if st.session_state.analysis_results:
        analysis = st.session_state.analysis_results
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎯 Identified Skills")
            if analysis["skills"]:
                tags = " ".join([f"`{skill}`" for skill in analysis["skills"]])
                st.markdown(tags)
            else:
                st.warning("No standard skills identified.")
                
            st.subheader("💪 Resume Strengths")
            if analysis["strengths"]:
                for strength in analysis["strengths"]:
                    st.success(strength)
            else:
                st.info("No particular strengths detected. Keep working on it!")
                
        with col2:
            st.subheader("🛠️ Recommended Changes")
            if analysis["suggestions"]:
                for suggestion in analysis["suggestions"]:
                    st.warning(suggestion)
            else:
                st.success("Your resume looks great! No major suggestions.")
                
        st.markdown("---")
        st.subheader("📝 Ready to test your skills?")
        st.write("Take a 15-question technical mock test based on the skills found in your resume.")
        if st.button("Try Mock Test", type="primary", use_container_width=True):
            st.session_state.page = "quiz"
            st.session_state.quiz_questions = generate_mcq_test(st.session_state.analyzed_skills, 15)
            st.session_state.current_q_index = 0
            st.session_state.score = 0
            st.rerun()

elif st.session_state.page == "quiz":
    enable_proctoring()
    st.title("📝 Technical Mock Test (Proctored)")
    
    q_index = st.session_state.current_q_index
    questions = st.session_state.quiz_questions
    
    if q_index < len(questions):
        st.progress((q_index) / len(questions))
        st.write(f"### Question {q_index + 1} of {len(questions)}")
        
        q_data = questions[q_index]
        st.info(f"**[{q_data['skill']}]** {q_data['q']}")
        
        choice = st.radio("Select an answer:", q_data["options"], index=None, key=f"q_{q_index}")
        
        if st.button("Submit Answer & Next"):
            if choice is None:
                st.warning("Please select an answer!")
            else:
                chosen_index = q_data["options"].index(choice)
                if chosen_index == q_data["ans"]:
                    st.session_state.score += 1
                
                st.session_state.current_q_index += 1
                st.rerun()
    else:
        st.session_state.page = "result"
        st.rerun()
        
elif st.session_state.page == "result":
    disable_proctoring()
    st.title("📊 Mock Test Results")
    score = st.session_state.score
    total = len(st.session_state.quiz_questions)
    
    st.subheader(f"You scored: {score} / {total}")
    st.progress(score / total if total > 0 else 0.0)
    
    if score == total:
        st.balloons()
        st.success("Perfect score! Outstanding job!")
    elif score >= total * 0.7:
        st.success("Great job! You have a solid grasp of these technical concepts.")
    else:
        st.warning("Good attempt! Keep reviewing your technical skills.")
        
    if st.button("Back to Resume Analyzer"):
        reset_quiz()
        st.rerun()
