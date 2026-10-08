import streamlit as st
from PyPDF2 import PdfReader
import re
import spacy
from collections import Counter
import random
from datetime import datetime
import streamlit.components.v1 as components
import database
import quiz_engine
from styles import apply_custom_styles

# Configure Streamlit page with collapsed sidebar for a clean web-app layout
st.set_page_config(
    page_title="CareerPath.AI — Enterprise AI Resume Analytics & Certified Assessment",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom White and Royal Blue SaaS styling matching user reference design
apply_custom_styles()

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "📄 Resume Analyzer"
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "quiz_finished" not in st.session_state:
    st.session_state.quiz_finished = False
if "analyzed_skills" not in st.session_state:
    st.session_state.analyzed_skills = []
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "🌐 Full Stack Developer"
if "score" not in st.session_state:
    st.session_state.score = 0
if "roadmap_data" not in st.session_state:
    st.session_state.roadmap_data = None
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "last_filename" not in st.session_state:
    st.session_state.last_filename = ""
if "exam_start_time" not in st.session_state:
    st.session_state.exam_start_time = None

def reset_quiz():
    st.session_state.quiz_active = False
    st.session_state.quiz_finished = False
    st.session_state.quiz_questions = []
    st.session_state.current_q_index = 0
    st.session_state.user_answers = {}
    st.session_state.score = 0
    st.session_state.roadmap_data = None
    st.session_state.exam_start_time = None

# Try to load the English NLP model
@st.cache_resource
def load_nlp_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        try:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            return spacy.load("en_core_web_sm")
        except Exception:
            return None

nlp = load_nlp_model()

SKILLS_DB = [
    "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "HTML", "CSS", "React", "Angular", "Vue",
    "Node.js", "Express", "Django", "Flask", "FastAPI", "SQL", "MySQL", "PostgreSQL", "MongoDB",
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
            content = page.extract_text()
            if content:
                text += content + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
    return text

def calculate_ats_score(results, text):
    score = 0
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    if re.search(email_pattern, text): score += 10
    if re.search(phone_pattern, text): score += 10
    
    word_count = len(text.split())
    if 250 <= word_count <= 950:
        score += 20
    elif 150 <= word_count < 250 or 950 < word_count <= 1300:
        score += 10
    
    if re.search(r'\d+%|\$\d+|\b\d+\b', text):
        score += 20
        
    if results.get("strengths") and any("action verbs" in s.lower() for s in results.get("strengths", [])):
        score += 20
    elif results.get("strengths"):
        score += 10
        
    skill_cnt = len(results.get("skills", []))
    if skill_cnt >= 6:
        score += 20
    elif skill_cnt >= 3:
        score += 15
    elif skill_cnt >= 1:
        score += 10
        
    return min(100, max(20, score))

def analyze_resume_local(text):
    results = {"skills": [], "suggestions": [], "strengths": [], "word_count": 0, "ats_score": 0}
    if not text.strip(): return results
    text_lower = text.lower()
    
    found_skills = []
    for skill, skill_lower in zip(SKILLS_DB, SKILLS_DB_LOWER):
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', text_lower):
            found_skills.append(skill)
    results["skills"] = list(dict.fromkeys(found_skills))

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    has_email = bool(re.search(email_pattern, text))
    has_phone = bool(re.search(phone_pattern, text))
    if not has_email: results["suggestions"].append("Include a direct email address for recruiter correspondence.")
    if not has_phone: results["suggestions"].append("Include a verified telephone / mobile contact number.")

    word_count = len(text.split())
    results["word_count"] = word_count
    if word_count < 200:
        results["suggestions"].append(f"Resume is very concise ({word_count} words). Expand on key technical projects and impact.")
    elif word_count > 1000:
        results["suggestions"].append(f"Resume length is high ({word_count} words). Condense into a sharp 1-2 page executive brief.")
    else:
        results["strengths"].append(f"Optimal document length achieved ({word_count} words).")

    has_metrics = bool(re.search(r'\d+%|\$\d+|\b\d+\b', text))
    if has_metrics:
        results["strengths"].append("Highlights quantifiable impact through statistics, percentages, and performance benchmarks.")
    else:
        results["suggestions"].append("Quantify key achievements with concrete metrics (e.g. 'reduced API response time by 42%', 'scaled to 50k users').")

    if nlp:
        doc = nlp(text)
        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
        strong_verbs = {"develop", "manage", "create", "lead", "design", "build", "improve", "increase", "architect", "deploy", "implement"}
        found_strong_verbs = set(verbs).intersection(strong_verbs)
        if found_strong_verbs:
            sample_verbs = ", ".join([f"'{v.capitalize()}'" for v in list(found_strong_verbs)[:3]])
            results["strengths"].append(f"High-impact action verbs identified: {sample_verbs}.")
        else:
            results["suggestions"].append("Begin experience bullet points with decisive action verbs like 'Architected', 'Spearheaded', or 'Optimized'.")

    results["ats_score"] = calculate_ats_score(results, text)
    return results

# ==============================================================================
# ENHANCED PROCTORING ENGINE (WHITE & ROYAL BLUE SUITE WITH ANTI-CHEAT SENSORS)
# ==============================================================================
def enable_proctoring():
    st.markdown("""
        <style>
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

        if (!parentWin.proctoringEngineActive) {
            parentWin.proctoringEngineActive = true;
            parentWin.examViolationCount = parentWin.examViolationCount || 0;

            // 1. Context Menu & Copy/Paste Restriction
            parentWin.handleContextMenu = (e) => {
                e.preventDefault();
                parentWin.showProctorToast("⚠️ Right-click context menu is restricted during the examination.");
            };
            parentWin.handleCopy = (e) => {
                e.preventDefault();
                parentWin.showProctorToast("⚠️ Copying text is restricted during the examination.");
            };
            parentWin.handlePaste = (e) => {
                e.preventDefault();
                parentWin.showProctorToast("⚠️ Pasting text is restricted during the examination.");
            };

            // 2. Tab-Switch & Window Blur Detection
            parentWin.handleVisibility = () => {
                if (parentDoc.hidden) {
                    parentWin.examViolationCount += 1;
                    parentWin.showProctorToast(`🚨 PROCTOR ALERT (${parentWin.examViolationCount}/3): Tab switch or window blur detected!`);
                    const countEl = parentDoc.getElementById("proctorViolationCounter");
                    if (countEl) countEl.innerText = `${parentWin.examViolationCount} / 3`;
                }
            };

            // 3. Fullscreen Exit Detection
            parentWin.handleFullscreenChange = () => {
                const isFs = parentDoc.fullscreenElement || parentDoc.webkitFullscreenElement || parentDoc.msFullscreenElement;
                const lockOverlay = parentDoc.getElementById("fsLockOverlay");
                if (!isFs && parentWin.proctoringEngineActive) {
                    if (lockOverlay) lockOverlay.style.display = "flex";
                } else if (isFs) {
                    if (lockOverlay) lockOverlay.style.display = "none";
                }
            };

            parentDoc.addEventListener('contextmenu', parentWin.handleContextMenu);
            parentDoc.addEventListener('copy', parentWin.handleCopy);
            parentDoc.addEventListener('paste', parentWin.handlePaste);
            parentDoc.addEventListener('visibilitychange', parentWin.handleVisibility);
            parentDoc.addEventListener('fullscreenchange', parentWin.handleFullscreenChange);

            parentWin.onbeforeunload = function() {
                return "You are currently in an active proctored examination. Leaving will forfeit your score.";
            };

            // White & Royal Blue Toast Notification
            parentWin.showProctorToast = (message) => {
                let toast = parentDoc.getElementById('proctorToastBox');
                if (!toast) {
                    toast = parentDoc.createElement('div');
                    toast.id = 'proctorToastBox';
                    toast.style.position = 'fixed';
                    toast.style.top = '22px';
                    toast.style.left = '50%';
                    toast.style.transform = 'translateX(-50%)';
                    toast.style.background = '#ffffff';
                    toast.style.color = '#0f172a';
                    toast.style.border = '1.5px solid #bfdbfe';
                    toast.style.borderLeft = '5px solid #2563eb';
                    toast.style.padding = '12px 26px';
                    toast.style.borderRadius = '16px';
                    toast.style.fontWeight = '700';
                    toast.style.fontSize = '14px';
                    toast.style.boxShadow = '0 14px 35px rgba(37,99,235,0.18)';
                    toast.style.zIndex = '9999999';
                    toast.style.transition = 'all 0.3s ease';
                    parentDoc.body.appendChild(toast);
                }
                toast.innerText = message;
                toast.style.display = 'block';
                toast.style.opacity = '1';
                setTimeout(() => {
                    toast.style.opacity = '0';
                    setTimeout(() => toast.style.display = 'none', 300);
                }, 3500);
            };

            // White & Blue Floating Proctor HUD
            if (!parentDoc.getElementById('proctorFloatingHUD')) {
                const hud = parentDoc.createElement('div');
                hud.id = 'proctorFloatingHUD';
                hud.style.position = 'fixed';
                hud.style.top = '16px';
                hud.style.right = '24px';
                hud.style.background = 'rgba(255, 255, 255, 0.95)';
                hud.style.backdropFilter = 'blur(20px)';
                hud.style.border = '1.5px solid #bfdbfe';
                hud.style.borderRadius = '16px';
                hud.style.padding = '8px 18px';
                hud.style.color = '#0f172a';
                hud.style.fontSize = '13px';
                hud.style.fontWeight = '700';
                hud.style.display = 'flex';
                hud.style.alignItems = 'center';
                hud.style.gap = '16px';
                hud.style.zIndex = '999998';
                hud.style.boxShadow = '0 8px 25px rgba(37,99,235,0.12)';
                hud.innerHTML = `
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span style="color:#22c55e; font-size:16px;">●</span>
                        <span style="color:#1e40af;">AI Proctor Active</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; background:#eff6ff; padding:3px 10px; border-radius:10px; border:1px solid #bfdbfe;">
                        <span style="color:#dc2626;">⚠️</span>
                        <span>Violations: <strong id="proctorViolationCounter">0 / 3</strong></span>
                    </div>
                `;
                parentDoc.body.appendChild(hud);
            }

            // Fullscreen Lockdown Recovery Overlay (White & Blue)
            if (!parentDoc.getElementById('fsLockOverlay')) {
                const lockOverlay = parentDoc.createElement('div');
                lockOverlay.id = 'fsLockOverlay';
                lockOverlay.style.position = 'fixed';
                lockOverlay.style.top = '0';
                lockOverlay.style.left = '0';
                lockOverlay.style.width = '100vw';
                lockOverlay.style.height = '100vh';
                lockOverlay.style.backgroundColor = 'rgba(15, 23, 42, 0.88)';
                lockOverlay.style.backdropFilter = 'blur(20px)';
                lockOverlay.style.color = '#0f172a';
                lockOverlay.style.display = 'none';
                lockOverlay.style.flexDirection = 'column';
                lockOverlay.style.justifyContent = 'center';
                lockOverlay.style.alignItems = 'center';
                lockOverlay.style.zIndex = '9999999';
                lockOverlay.style.fontFamily = "'Plus Jakarta Sans', sans-serif";
                lockOverlay.innerHTML = `
                    <div style="background:#ffffff; border-radius:24px; padding:40px; max-width:480px; text-align:center; box-shadow:0 25px 60px rgba(15,23,42,0.3); border:1.5px solid #bfdbfe;">
                        <div style="font-size: 52px; margin-bottom: 12px;">🛡️</div>
                        <h2 style="font-size: 24px; font-weight:800; margin-bottom: 8px; color:#0f172a;">Fullscreen Lockdown Enforced</h2>
                        <p style="color: #475569; font-size: 15px; margin-bottom: 24px; line-height: 1.6;">
                            Exiting fullscreen violates the integrity policy of this examination. Please click below to re-enter secure examination mode.
                        </p>
                        <button id="resumeFsBtn" style="background:linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color:#ffffff; border:none; padding:13px 32px; font-size:15px; font-weight:800; border-radius:14px; cursor:pointer; box-shadow: 0 6px 20px rgba(37,99,235,0.35);">
                            Resume Fullscreen Exam ➔
                        </button>
                    </div>
                `;
                parentDoc.body.appendChild(lockOverlay);

                const resumeBtn = parentDoc.getElementById('resumeFsBtn');
                if (resumeBtn) {
                    resumeBtn.onclick = () => {
                        const elem = parentDoc.documentElement;
                        if (elem.requestFullscreen) elem.requestFullscreen();
                        else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
                        lockOverlay.style.display = 'none';
                    };
                }
            }

            // Sequential script loader to guarantee TFJS is initialized before COCO-SSD & BlazeFace
            function loadScript(src, id) {
                return new Promise((resolve, reject) => {
                    const existing = parentDoc.getElementById(id);
                    if (existing) {
                        resolve();
                        return;
                    }
                    const s = parentDoc.createElement('script');
                    s.id = id;
                    s.src = src;
                    s.onload = () => resolve();
                    s.onerror = (e) => reject(e);
                    parentDoc.head.appendChild(s);
                });
            }

            function ensureAIModelsLoaded() {
                return loadScript('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js', 'tfjs-script')
                    .then(() => {
                        return Promise.all([
                            loadScript('https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd@2.2.3/dist/coco-ssd.min.js', 'cocossd-script'),
                            loadScript('https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.0.7/dist/blazeface.min.js', 'blazeface-script')
                        ]);
                    })
                    .then(() => {
                        const getCoco = () => parentWin.cocoSsd || window.cocoSsd || parentDoc.defaultView?.cocoSsd;
                        const getBlaze = () => parentWin.blazeface || window.blazeface || parentDoc.defaultView?.blazeface;
                        return new Promise((resolve, reject) => {
                            let attempts = 0;
                            const checkInterval = setInterval(() => {
                                attempts++;
                                const c = getCoco();
                                const b = getBlaze();
                                if (c && b) {
                                    clearInterval(checkInterval);
                                    Promise.all([c.load(), b.load()])
                                        .then(([cocoModel, faceModel]) => resolve({ cocoModel, faceModel }))
                                        .catch(err => reject(err));
                                } else if (attempts > 50) {
                                    clearInterval(checkInterval);
                                    reject(new Error("AI Model loading timeout"));
                                }
                            }, 250);
                        });
                    });
            }

            // Setup Camera Feed, AI Detection & Permission Overlay in White & Blue
            if (!parentDoc.getElementById('proctorSetupModal')) {
                const modal = parentDoc.createElement('div');
                modal.id = 'proctorSetupModal';
                modal.style.position = 'fixed';
                modal.style.top = '0';
                modal.style.left = '0';
                modal.style.width = '100vw';
                modal.style.height = '100vh';
                modal.style.backgroundColor = 'rgba(15, 23, 42, 0.75)';
                modal.style.backdropFilter = 'blur(16px)';
                modal.style.color = '#0f172a';
                modal.style.display = 'flex';
                modal.style.flexDirection = 'column';
                modal.style.justifyContent = 'center';
                modal.style.alignItems = 'center';
                modal.style.zIndex = '999999';
                modal.style.fontFamily = "'Plus Jakarta Sans', sans-serif";
                modal.innerHTML = `
                    <div style="background: #ffffff; border: 1.5px solid #bfdbfe; border-radius: 24px; padding: 40px; max-width: 530px; text-align: center; box-shadow: 0 25px 60px rgba(15,23,42,0.25);">
                        <div style="width:58px; height:58px; margin:0 auto 16px auto; border-radius:18px; background:#eff6ff; display:flex; align-items:center; justify-content:center; font-size:28px; border:1.5px solid #bfdbfe;">🛡️</div>
                        <h2 style="font-size: 24px; margin-bottom: 8px; font-weight: 800; color: #0f172a;">Exam Integrity Verification</h2>
                        <p style="color: #475569; font-size: 14px; line-height: 1.6; margin-bottom: 24px;">
                            This is a formal 15-question proctored evaluation. AI Camera monitoring checks for unauthorized mobile phones and screen focus in real time.
                        </p>
                        <div style="background: #eff6ff; border: 1.5px solid #bfdbfe; border-radius: 14px; padding: 16px; margin-bottom: 24px; text-align: left; font-size: 13px; color: #1e40af; line-height: 1.8;">
                            ✓ <strong>AI Mobile Phone Detection:</strong> Phones detected on webcam trigger immediate violation flags.<br>
                            ✓ <strong>AI Head-Turn Movement:</strong> Looking away from screen triggers active proctor alert.<br>
                            ✓ <strong>Fullscreen Lock:</strong> Exiting fullscreen triggers security lockdown overlay.<br>
                            ✓ <strong>Tab-Switch Tracking:</strong> Switching browser tabs is logged against candidate integrity.
                        </div>
                        <button id="startProctorCheckBtn" style="width:100%; background:linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color:#ffffff; border:none; padding:14px; font-size:16px; font-weight:800; border-radius:14px; cursor:pointer; box-shadow:0 8px 25px rgba(37, 99, 235, 0.35);">
                            Verify Permissions & Enter Fullscreen ➔
                        </button>
                    </div>
                `;
                parentDoc.body.appendChild(modal);

                const checkBtn = parentDoc.getElementById('startProctorCheckBtn');
                if (checkBtn) {
                    checkBtn.onclick = () => {
                        checkBtn.innerText = "Requesting Camera & Initializing AI...";
                        checkBtn.disabled = true;

                        navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 } }).then(camStream => {
                            parentWin.examCameraStream = camStream;
                            
                            // Setup Floating Camera Container with Live White & Blue Status Badge
                            let camContainer = parentDoc.getElementById('proctorCamContainer');
                            if (!camContainer) {
                                camContainer = parentDoc.createElement('div');
                                camContainer.id = 'proctorCamContainer';
                                camContainer.style.position = 'fixed';
                                camContainer.style.bottom = '20px';
                                camContainer.style.right = '20px';
                                camContainer.style.width = '220px';
                                camContainer.style.borderRadius = '18px';
                                camContainer.style.overflow = 'hidden';
                                camContainer.style.boxShadow = '0 14px 35px rgba(37,99,235,0.18)';
                                camContainer.style.zIndex = '999998';
                                camContainer.style.fontFamily = "'Plus Jakarta Sans', sans-serif";
                                camContainer.style.border = '2px solid #bfdbfe';
                                camContainer.style.transition = 'all 0.3s ease';

                                camContainer.innerHTML = `
                                    <div id="proctorCamStatusPill" style="background:#ffffff; color:#0f172a; font-size:11px; font-weight:700; padding:7px 12px; display:flex; align-items:center; justify-content:center; gap:6px; border-bottom:1.5px solid #e2e8f0;">
                                        <span id="proctorCamStatusDot" style="color:#22c55e;">●</span>
                                        <span id="proctorCamStatusText">AI Scanning Active</span>
                                    </div>
                                    <div style="position:relative; width:220px; height:155px; background:#0f172a;">
                                        <video id="proctorCamFeed" autoplay muted playsinline style="width:100%; height:100%; object-fit:cover; display:block;"></video>
                                        <div id="proctorCamWarningBanner" style="display:none; position:absolute; bottom:6px; left:6px; right:6px; background:rgba(239,68,68,0.95); color:#ffffff; font-size:10px; font-weight:800; padding:4px 6px; border-radius:6px; text-align:center; text-transform:uppercase; letter-spacing:0.5px;">
                                            ⚠️ VIOLATION
                                        </div>
                                    </div>
                                `;
                                parentDoc.body.appendChild(camContainer);
                                
                                const videoEl = parentDoc.getElementById('proctorCamFeed');
                                videoEl.srcObject = camStream;
                            }

                            // Start Real-Time AI Detection Loop
                            ensureAIModelsLoaded().then(({ cocoModel, faceModel }) => {
                                parentWin.showProctorToast("🤖 AI Proctor Online: Active Phone & Head-Turn Sensors");

                                const statusPill = parentDoc.getElementById('proctorCamStatusPill');
                                const statusDot = parentDoc.getElementById('proctorCamStatusDot');
                                const statusText = parentDoc.getElementById('proctorCamStatusText');
                                const warningBanner = parentDoc.getElementById('proctorCamWarningBanner');
                                const camBox = parentDoc.getElementById('proctorCamContainer');
                                const videoEl = parentDoc.getElementById('proctorCamFeed');

                                let lastPhoneViolationTime = 0;
                                let lastHeadWarningTime = 0;

                                parentWin.aiDetectionInterval = setInterval(async () => {
                                    if (!parentWin.proctoringEngineActive || !videoEl || videoEl.readyState < 2) return;
                                    const now = Date.now();
                                    let phoneDetected = false;
                                    let headTurned = false;
                                    let faceFound = false;

                                    // 1. Mobile Phone Detection (COCO-SSD)
                                    try {
                                        const cocoPreds = await cocoModel.detect(videoEl);
                                        const phoneItem = cocoPreds.find(p =>
                                            (p.class === 'cell phone' || p.class === 'remote' || p.class === 'telephone') && p.score > 0.30
                                        );
                                        if (phoneItem) {
                                            phoneDetected = true;
                                            if (now - lastPhoneViolationTime > 4000) {
                                                lastPhoneViolationTime = now;
                                                parentWin.examViolationCount = (parentWin.examViolationCount || 0) + 1;
                                                parentWin.showProctorToast(`🚨 PROCTOR VIOLATION (${parentWin.examViolationCount}/3): Unauthorized mobile phone detected!`);
                                                const countEl = parentDoc.getElementById("proctorViolationCounter");
                                                if (countEl) countEl.innerText = `${parentWin.examViolationCount} / 3`;
                                            }
                                        }
                                    } catch(e) {}

                                    // 2. Head Movement & Face Presence Detection (BlazeFace)
                                    try {
                                        const facePreds = await faceModel.estimateFaces(videoEl, false);
                                        if (facePreds && facePreds.length > 0) {
                                            faceFound = true;
                                            const p = facePreds[0];
                                            if (p.landmarks && p.landmarks.length >= 3) {
                                                const rx = p.landmarks[0][0]; // Right eye
                                                const lx = p.landmarks[1][0]; // Left eye
                                                const nx = p.landmarks[2][0]; // Nose
                                                const leftToNose = Math.abs(lx - nx);
                                                const noseToRight = Math.abs(nx - rx);
                                                const turnRatio = leftToNose / (noseToRight || 0.001);

                                                // If ratio is skewed beyond 2.2 or below 0.45, candidate has turned their head
                                                if (turnRatio > 2.2 || turnRatio < 0.45) {
                                                    headTurned = true;
                                                    if (now - lastHeadWarningTime > 3500) {
                                                        lastHeadWarningTime = now;
                                                        parentWin.showProctorToast("⚠️ WARNING: Please face the screen directly! Head movement detected.");
                                                    }
                                                }
                                            }
                                        }
                                    } catch(e) {}

                                    // 3. Update Camera HUD Visually
                                    if (camBox && statusPill && statusText) {
                                        if (phoneDetected) {
                                            camBox.style.border = '2px solid #ef4444';
                                            camBox.style.boxShadow = '0 0 25px rgba(239,68,68,0.7)';
                                            statusPill.style.background = '#fee2e2';
                                            statusDot.style.color = '#dc2626';
                                            statusText.innerText = '🚨 PHONE DETECTED!';
                                            if (warningBanner) {
                                                warningBanner.style.display = 'block';
                                                warningBanner.style.background = '#ef4444';
                                                warningBanner.innerText = '🚨 UNAUTHORIZED PHONE';
                                            }
                                        } else if (!faceFound) {
                                            camBox.style.border = '2px solid #ef4444';
                                            camBox.style.boxShadow = '0 0 18px rgba(239,68,68,0.5)';
                                            statusPill.style.background = '#fee2e2';
                                            statusDot.style.color = '#dc2626';
                                            statusText.innerText = '⚠️ NO FACE IN FRAME';
                                            if (warningBanner) {
                                                warningBanner.style.display = 'block';
                                                warningBanner.style.background = '#ef4444';
                                                warningBanner.innerText = '⚠️ FACE MISSING';
                                            }
                                        } else if (headTurned) {
                                            camBox.style.border = '2px solid #f59e0b';
                                            camBox.style.boxShadow = '0 0 20px rgba(245,158,11,0.5)';
                                            statusPill.style.background = '#fef3c7';
                                            statusDot.style.color = '#d97706';
                                            statusText.innerText = '🟡 HEAD TURN DETECTED';
                                            if (warningBanner) {
                                                warningBanner.style.display = 'block';
                                                warningBanner.style.background = '#f59e0b';
                                                warningBanner.innerText = '⚠️ FACE THE SCREEN';
                                            }
                                        } else {
                                            camBox.style.border = '2px solid #bfdbfe';
                                            camBox.style.boxShadow = '0 12px 35px rgba(37,99,235,0.18)';
                                            statusPill.style.background = '#ffffff';
                                            statusDot.style.color = '#22c55e';
                                            statusText.innerText = '🟢 SCREEN FOCUSED';
                                            if (warningBanner) warningBanner.style.display = 'none';
                                        }
                                    }
                                }, 1500);
                            }).catch(err => {
                                console.log("Error initializing AI proctoring models:", err);
                                parentWin.showProctorToast("⚠️ AI Proctoring running in standard surveillance mode.");
                            });

                            // Enter Fullscreen
                            const elem = parentDoc.documentElement;
                            try {
                                if (elem.requestFullscreen) elem.requestFullscreen();
                                else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
                            } catch(e) { console.log(e); }

                            modal.remove();
                        }).catch(err => {
                            alert("Camera access is mandatory for proctored evaluation: " + err.message);
                            checkBtn.innerText = "Retry Camera Access";
                            checkBtn.disabled = false;
                        });
                    };
                }
            }
        }
    </script>
    """
    components.html(js_code, height=0, width=0)

def disable_proctoring():
    js_code = """
    <script>
        const parentDoc = window.parent.document;
        const parentWin = window.parent;

        if (parentWin.proctoringEngineActive) {
            parentDoc.removeEventListener('contextmenu', parentWin.handleContextMenu);
            parentDoc.removeEventListener('copy', parentWin.handleCopy);
            parentDoc.removeEventListener('paste', parentWin.handlePaste);
            parentDoc.removeEventListener('visibilitychange', parentWin.handleVisibility);
            parentDoc.removeEventListener('fullscreenchange', parentWin.handleFullscreenChange);
            parentWin.proctoringEngineActive = false;

            try {
                if (parentDoc.fullscreenElement || parentDoc.webkitFullscreenElement) {
                    if (parentDoc.exitFullscreen) parentDoc.exitFullscreen();
                    else if (parentDoc.webkitExitFullscreen) parentDoc.webkitExitFullscreen();
                }
            } catch (e) { console.log(e); }

            if (parentWin.examCameraStream) {
                parentWin.examCameraStream.getTracks().forEach(track => track.stop());
            }
            if (parentWin.aiDetectionInterval) {
                clearInterval(parentWin.aiDetectionInterval);
            }

            const camBox = parentDoc.getElementById('proctorCamContainer');
            if (camBox) camBox.remove();
            const cam = parentDoc.getElementById('proctorCamFeed');
            if (cam) cam.remove();
            const hud = parentDoc.getElementById('proctorFloatingHUD');
            if (hud) hud.remove();
            const modal = parentDoc.getElementById('proctorSetupModal');
            if (modal) modal.remove();
            const lockOverlay = parentDoc.getElementById('fsLockOverlay');
            if (lockOverlay) lockOverlay.remove();
            const toast = parentDoc.getElementById('proctorToastBox');
            if (toast) toast.remove();
        }
        parentWin.onbeforeunload = null;
    </script>
    """
    components.html(js_code, height=0, width=0)

def render_proctor_self_test():
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd@2.2.3/dist/coco-ssd.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.0.7/dist/blazeface.min.js"></script>
        <style>
            * { box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
            body { margin: 0; padding: 12px; background: transparent; color: #0f172a; }
            .test-container {
                background: #ffffff;
                border: 1.5px solid #bfdbfe;
                border-radius: 20px;
                padding: 24px;
                box-shadow: 0 10px 30px rgba(37,99,235,0.06);
            }
            .ctrl-btn {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                color: #ffffff;
                border: none;
                padding: 11px 24px;
                font-size: 14px;
                font-weight: 800;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 4px 16px rgba(37,99,235,0.3);
            }
            .ctrl-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 22px rgba(37,99,235,0.45); }
            .stop-btn {
                background: #ffffff;
                color: #dc2626;
                border: 1.5px solid #fca5a5;
                margin-left: 10px;
                display: none;
                box-shadow: none;
            }
            .stop-btn:hover { background: #fee2e2; }
            .feed-grid {
                display: grid;
                grid-template-columns: 320px 1fr;
                gap: 20px;
                margin-top: 18px;
            }
            @media (max-width: 700px) {
                .feed-grid { grid-template-columns: 1fr; }
            }
            .video-box {
                position: relative;
                width: 100%;
                height: 240px;
                background: #0f172a;
                border-radius: 16px;
                overflow: hidden;
                border: 2px solid #bfdbfe;
                transition: border 0.3s ease, box-shadow 0.3s ease;
            }
            video { width: 100%; height: 100%; object-fit: cover; }
            .sensor-card {
                background: #eff6ff;
                border: 1.5px solid #bfdbfe;
                border-radius: 14px;
                padding: 14px;
                margin-bottom: 12px;
            }
            .sensor-label { font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 800; letter-spacing: 0.5px; }
            .sensor-value { font-size: 15px; font-weight: 800; margin-top: 4px; display: flex; align-items: center; gap: 8px; color: #0f172a; }
            .pill { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; }
            .pill-good { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
            .pill-warn { background: #fef3c7; color: #d97706; border: 1px solid #fde68a; }
            .pill-danger { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
            .checklist-item {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 13px;
                padding: 8px 12px;
                background: #f8fafc;
                border-radius: 10px;
                margin-bottom: 6px;
                border: 1px solid #e2e8f0;
                color: #334155;
            }
            .chk-icon { width: 20px; height: 20px; border-radius: 50%; border: 1.5px solid #cbd5e1; display: flex; align-items: center; justify-content: center; font-size: 11px; }
            .chk-pass { border-color: #22c55e; background: #22c55e; color: #ffffff; font-weight: 900; }
        </style>
    </head>
    <body>
        <div class="test-container">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h4 style="margin: 0; font-size: 17px; color: #0f172a; font-weight: 800;">🎥 AI Sensor Pre-Flight Diagnostic</h4>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #64748b;">
                        Verify mobile phone detection and head-turn tracking with your live webcam before starting the exam.
                    </p>
                </div>
                <div>
                    <button id="btnStartTest" class="ctrl-btn" onclick="startSelfTest()">▶ Start Live AI Sensor Test</button>
                    <button id="btnStopTest" class="ctrl-btn stop-btn" onclick="stopSelfTest()">⏹ Stop Camera</button>
                </div>
            </div>

            <div id="testArea" style="display: none;" class="feed-grid">
                <div>
                    <div id="videoContainer" class="video-box">
                        <video id="selfTestVideo" autoplay muted playsinline></video>
                    </div>
                    <div style="text-align: center; margin-top: 8px; font-size: 12px; color: #64748b; font-weight: 600;">
                        Live 320x240 Camera View (Encrypted & Processed 100% in Browser)
                    </div>
                </div>

                <div>
                    <div class="sensor-card">
                        <div class="sensor-label">Mobile Phone Sensor (COCO-SSD)</div>
                        <div id="phoneSensorVal" class="sensor-value">
                            <span class="pill pill-good">🟢 No Phone Detected (Clear)</span>
                        </div>
                    </div>

                    <div class="sensor-card">
                        <div class="sensor-label">Face Position & Gaze Tracking (BlazeFace)</div>
                        <div id="headSensorVal" class="sensor-value">
                            <span class="pill pill-good">🟢 Centered & Focused</span>
                        </div>
                    </div>

                    <div style="margin-top: 14px;">
                        <div class="checklist-item">
                            <div id="chkCamIcon" class="chk-icon">✕</div>
                            <span>Webcam hardware verified</span>
                        </div>
                        <div class="checklist-item">
                            <div id="chkFaceIcon" class="chk-icon">✕</div>
                            <span>Face detected in central examination viewport</span>
                        </div>
                        <div class="checklist-item">
                            <div id="chkHeadIcon" class="chk-icon">✕</div>
                            <span>Head-turn angular deflection sensors active</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let localStream = null;
            let testInterval = null;
            let cocoModel = null;
            let faceModel = null;

            async function startSelfTest() {
                const btnStart = document.getElementById('btnStartTest');
                const btnStop = document.getElementById('btnStopTest');
                const testArea = document.getElementById('testArea');

                btnStart.innerText = "⏳ Loading AI Models...";
                btnStart.disabled = true;

                try {
                    localStream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 } });
                    const videoEl = document.getElementById('selfTestVideo');
                    videoEl.srcObject = localStream;
                    testArea.style.display = 'grid';
                    btnStart.style.display = 'none';
                    btnStop.style.display = 'inline-block';

                    document.getElementById('chkCamIcon').className = 'chk-icon chk-pass';
                    document.getElementById('chkCamIcon').innerText = '✓';

                    if (!cocoModel || !faceModel) {
                        const [cModel, fModel] = await Promise.all([cocoSsd.load(), blazeface.load()]);
                        cocoModel = cModel;
                        faceModel = fModel;
                    }

                    testInterval = setInterval(async () => {
                        if (!localStream || videoEl.readyState < 2) return;

                        // 1. Phone Detection
                        try {
                            const preds = await cocoModel.detect(videoEl);
                            const phone = preds.find(p => (p.class === 'cell phone' || p.class === 'remote' || p.class === 'telephone') && p.score > 0.3);
                            const phoneValEl = document.getElementById('phoneSensorVal');
                            const box = document.getElementById('videoContainer');
                            if (phone) {
                                phoneValEl.innerHTML = `<span class="pill pill-danger">🚨 UNAUTHORIZED PHONE DETECTED (${Math.round(phone.score*100)}%)</span>`;
                                box.style.borderColor = '#ef4444';
                                box.style.boxShadow = '0 0 20px rgba(239, 68, 68, 0.5)';
                            } else {
                                phoneValEl.innerHTML = `<span class="pill pill-good">🟢 No Phone Detected (Clear)</span>`;
                                box.style.borderColor = '#bfdbfe';
                                box.style.boxShadow = 'none';
                            }
                        } catch(e) {}

                        // 2. Face & Head Tracking
                        try {
                            const facePreds = await faceModel.estimateFaces(videoEl, false);
                            const headValEl = document.getElementById('headSensorVal');
                            if (facePreds && facePreds.length > 0) {
                                const p = facePreds[0];
                                if (p.landmarks && p.landmarks.length >= 3) {
                                    const rx = p.landmarks[0][0];
                                    const lx = p.landmarks[1][0];
                                    const nx = p.landmarks[2][0];
                                    const leftToNose = Math.abs(lx - nx);
                                    const noseToRight = Math.abs(nx - rx);
                                    const turnRatio = leftToNose / (noseToRight || 0.001);

                                    if (turnRatio > 2.2 || turnRatio < 0.45) {
                                        const dir = turnRatio > 2.2 ? "Left" : "Right";
                                        headValEl.innerHTML = `<span class="pill pill-warn">🟡 Head Turn (${dir}) Detected</span>`;
                                        document.getElementById('chkHeadIcon').className = 'chk-icon chk-pass';
                                        document.getElementById('chkHeadIcon').innerText = '✓';
                                    } else {
                                        headValEl.innerHTML = `<span class="pill pill-good">🟢 Centered & Focused</span>`;
                                        document.getElementById('chkFaceIcon').className = 'chk-icon chk-pass';
                                        document.getElementById('chkFaceIcon').innerText = '✓';
                                    }
                                }
                            } else {
                                headValEl.innerHTML = `<span class="pill pill-danger">⚠️ Face Missing from Frame</span>`;
                            }
                        } catch(e) {}
                    }, 1200);

                } catch(err) {
                    alert("Camera error: " + err.message);
                    btnStart.innerText = "▶ Retry Camera Access";
                    btnStart.disabled = false;
                }
            }

            function stopSelfTest() {
                if (localStream) {
                    localStream.getTracks().forEach(t => t.stop());
                    localStream = null;
                }
                if (testInterval) {
                    clearInterval(testInterval);
                }
                document.getElementById('testArea').style.display = 'none';
                document.getElementById('btnStartTest').style.display = 'inline-block';
                document.getElementById('btnStartTest').innerText = '▶ Start Live AI Sensor Test';
                document.getElementById('btnStartTest').disabled = false;
                document.getElementById('btnStopTest').style.display = 'none';
            }
        </script>
    </body>
    </html>
    """
    components.html(test_html, height=440)


# ==============================================================================
# AUTHENTICATION & LOGIN SCREEN (MATCHING USER REFERENCE DESIGN)
# ==============================================================================
def render_auth_page():
    disable_proctoring()
    # MongoDB operates silently in background without showing online pill
    
    col_l, col_center, col_r = st.columns([1, 2.3, 1])
    with col_center:
        try:
            import assets_b64
            logo_src = f"data:image/png;base64,{assets_b64.LOGO_B64}"
        except Exception:
            logo_src = ""

        # Header matching the screenshot exactly with the exact logo image
        st.markdown(f"""
            <div style="text-align: center; margin-top: 26px; margin-bottom: 22px;">
                <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 14px;">
                    <img src="{logo_src}" alt="CareerPath.AI" style="height: 56px; object-fit: contain; image-rendering: -webkit-optimize-contrast;" />
                </div>
                <div style="color: #475569; font-size: 1.25rem; font-weight: 600; letter-spacing: -0.2px;">
                    Enterprise Local AI Resume Optimization &amp; AI-Proctored Assessment
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔒 Sign In", "👤 Create Account"])

        # Tab: Sign In (Matches screenshot Welcome Back form exactly)
        with tab_login:
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                st.markdown("<h3 style='margin-top:0; margin-bottom:16px; font-size: 1.6rem; font-weight:800; color:#0f172a;'>Welcome Back</h3>", unsafe_allow_html=True)
                email = st.text_input("Work Email Address", placeholder="alex@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••••••")
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                submit = st.form_submit_button("Sign In to Portal ➔", use_container_width=True)
                
                if submit:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        with st.spinner("Authenticating credentials..."):
                            success, msg, user = database.authenticate_user(email, password)
                            if success:
                                st.session_state.user = user
                                st.rerun()
                            else:
                                st.error(msg)

        # Tab: Create Account
        with tab_register:
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            with st.form("register_form"):
                st.markdown("<h3 style='margin-top:0; margin-bottom:16px; font-size: 1.6rem; font-weight:800; color:#0f172a;'>Create Profile</h3>", unsafe_allow_html=True)
                reg_name = st.text_input("Full Legal Name", placeholder="Alex Morgan")
                reg_email = st.text_input("Work Email Address", placeholder="alex@company.com")
                reg_password = st.text_input("Password (min 6 characters)", type="password", placeholder="••••••••••••")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••••••")
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                reg_submit = st.form_submit_button("Create Account ➔", use_container_width=True)
                
                if reg_submit:
                    if reg_password != reg_confirm:
                        st.error("Passwords do not match!")
                    else:
                        with st.spinner("Creating profile..."):
                            success, msg, user = database.register_user(reg_name, reg_email, reg_password)
                            if success:
                                st.session_state.user = user
                                st.rerun()
                            else:
                                st.error(msg)


# ==============================================================================
# MAIN APPLICATION INTERFACE (LOGGED IN) - 100% MATCHING USER SCREENSHOT
# ==============================================================================
def render_main_app():
    user = st.session_state.user
    user_name = user.get("name", "User")
    user_initial = (user_name[:1]).upper() if user_name else "U"
    
    # 1. Top Navbar matching media_1791308758811.png
    try:
        import assets_b64
        logo_src = f"data:image/png;base64,{assets_b64.LOGO_B64}"
    except Exception:
        logo_src = ""

    # Navbar Columns: Logo | Nav items (Resume Analyzer, Mock Test, Performance) | User & Sign Out
    c_brand, c_tabs, c_profile, c_logout = st.columns([1.3, 3.3, 0.95, 0.75])
    with c_brand:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; padding-top: 5px;">
                <svg width="26" height="28" viewBox="0 0 26 28" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink: 0;">
                    <path d="M4 0C1.79086 0 0 1.79086 0 4V24C0 26.2091 1.79086 28 4 28H16L26 18V4C26 1.79086 24.2091 0 22 0H4Z" fill="#2563eb"/>
                    <path d="M16 18H26L16 28V18Z" fill="#bfdbfe"/>
                    <rect x="5" y="7" width="7" height="2.5" rx="1.25" fill="white"/>
                    <circle cx="20" cy="7" r="1.5" fill="white"/>
                    <rect x="5" y="13" width="15" height="2.5" rx="1.25" fill="white"/>
                    <rect x="5" y="19" width="8" height="2.5" rx="1.25" fill="white"/>
                </svg>
                <span style="font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.4px; color: #1e293b; line-height: 1; white-space: nowrap;">Resume<span style="color: #2563eb;">Analyzer</span></span>
            </div>
        """, unsafe_allow_html=True)
    
    with c_tabs:
        # 3 Clean Capsule Navigation Pills Matching Screenshot
        t1, t2, t3 = st.columns([1.18, 1.0, 1.05])
        with t1:
            is_active_1 = (st.session_state.nav_page == "📄 Resume Analyzer")
            btn_style_1 = "primary" if is_active_1 else "secondary"
            if st.button("Resume Analyzer", icon=":material/description:", type=btn_style_1, key="nav_resume_analyzer", use_container_width=True):
                st.session_state.nav_page = "📄 Resume Analyzer"
                st.rerun()
        with t2:
            is_active_2 = (st.session_state.nav_page == "📝 Proctored Mock Test")
            btn_style_2 = "primary" if is_active_2 else "secondary"
            if st.button("Mock Test", icon=":material/assignment:", type=btn_style_2, key="nav_mock_test", use_container_width=True):
                st.session_state.nav_page = "📝 Proctored Mock Test"
                st.rerun()
        with t3:
            is_active_3 = (st.session_state.nav_page == "📊 Performance Dashboard")
            btn_style_3 = "primary" if is_active_3 else "secondary"
            if st.button("Performance", icon=":material/bar_chart:", type=btn_style_3, key="nav_performance", use_container_width=True):
                st.session_state.nav_page = "📊 Performance Dashboard"
                st.rerun()

    with c_profile:
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; padding-top: 6px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: #2563eb; color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px;">
                    {user_initial}
                </div>
                <span style="font-weight: 700; font-size: 14px; color: #334155;">{user_name} ▾</span>
            </div>
        """, unsafe_allow_html=True)
        
    with c_logout:
        if st.button("Sign Out", icon=":material/logout:", key="nav_sign_out", use_container_width=True):
            disable_proctoring()
            st.session_state.user = None
            reset_quiz()
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # ==========================================================================
    # 1. RESUME ANALYZER VIEW (100% MATCHING SCREENSHOT)
    # ==========================================================================
    if st.session_state.nav_page == "📄 Resume Analyzer":
        disable_proctoring()

        try:
            import dashboard_assets_b64
            doc_ill_b64 = dashboard_assets_b64.DOC_ILLUSTRATION_B64
            doc_img_tag = f'<img src="data:image/png;base64,{doc_ill_b64}" style="width: 135px; object-fit: contain;" />'
        except Exception:
            doc_img_tag = '<div style="font-size: 72px;">📄</div>'

        # UPPER SECTION: Main Hero Card (Left) + 3 Quick Action Tiles (Right)
        col_hero_left, col_actions_right = st.columns([1.65, 1.0])

        with col_hero_left:
            st.markdown(f"""<div class="dash-main-card">
<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 20px;">
<div>
<div class="badge-ai-assistant">
✨ Your AI-Powered Career Assistant
</div>
<div class="dash-main-title">
Local AI Resume<br>Intelligence Engine
</div>
<div class="dash-main-subtitle">
Analyze your resume with our local AI engine. Get ATS readiness score, identify skill gaps and receive actionable recommendations to boost your career.
</div>
<div class="features-trio">
<div class="feature-trio-item">
<div class="feature-trio-icon">🔒</div>
<div>
<div class="feature-trio-title">100% Private & Local</div>
<div class="feature-trio-desc">Your data stays with you</div>
</div>
</div>
<div class="feature-trio-item">
<div class="feature-trio-icon">🧠</div>
<div>
<div class="feature-trio-title">AI Powered</div>
<div class="feature-trio-desc">Smart analysis & insights</div>
</div>
</div>
<div class="feature-trio-item">
<div class="feature-trio-icon">🛡️</div>
<div>
<div class="feature-trio-title">Verified Profile</div>
<div class="feature-trio-desc">Build your career with confidence</div>
</div>
</div>
</div>
</div>
<div style="padding-top: 10px;">
{doc_img_tag}
</div>
</div>
</div>""", unsafe_allow_html=True)

        with col_actions_right:
            # Action Tile 1: Upload Your Resume (Primary Cyan/Blue Gradient)
            st.markdown("""<div class="action-tile-primary">
<div style="display: flex; align-items: center; gap: 14px;">
<div style="width: 44px; height: 44px; border-radius: 14px; background: rgba(255,255,255,0.22); display: flex; align-items: center; justify-content: center; font-size: 22px;">
☁️
</div>
<div>
<div style="font-weight: 800; font-size: 1.05rem;">Upload Your Resume</div>
<div style="font-size: 0.8rem; opacity: 0.9;">Drag & drop or click to upload (PDF, max 10MB)</div>
</div>
</div>
<div class="arrow-circle-btn">➔</div>
</div>""", unsafe_allow_html=True)

            # Upload Trigger File Input
            uploaded_file = st.file_uploader(
                "Upload Resume (PDF)",
                type=["pdf"],
                label_visibility="collapsed",
                help="PDF is processed locally in-memory."
            )

            # Action Tile 2: View Analysis (Clickable Navigation)
            if st.button("🎯   View Analysis  ➔\nSee your ATS score, skills & recommendations", key="btn_view_analysis", use_container_width=True):
                if not st.session_state.analysis_results:
                    # If not yet analyzed in this session, check recent scan from DB
                    user_scans = database.get_user_resume_history(user["email"], limit=1)
                    if user_scans:
                        st.session_state.analysis_results = user_scans[0]
                        st.session_state.analyzed_skills = user_scans[0].get("skills", [])
                    st.toast("Viewing your latest resume analysis", icon="🎯")
                st.session_state.nav_page = "📄 Resume Analyzer"
                st.rerun()

            # Action Tile 3: Take Mock Test (Clickable Navigation to Exam)
            if st.button("⚡   Take Mock Test  ➔\nPractice with AI proctored tests", key="btn_take_mock_test", use_container_width=True):
                st.session_state.nav_page = "📝 Proctored Mock Test"
                st.rerun()

        # Analyze Trigger Button
        if uploaded_file is not None:
            if st.button("Analyze Uploaded Resume ➔", type="primary", use_container_width=True):
                with st.spinner("Analyzing resume text and extracting technical skills..."):
                    resume_text = extract_text_from_pdf(uploaded_file)
                    if resume_text.strip():
                        analysis = analyze_resume_local(resume_text)
                        st.session_state.analysis_results = analysis
                        st.session_state.analyzed_skills = analysis.get("skills", [])
                        st.session_state.last_filename = uploaded_file.name
                        
                        database.save_resume_scan(
                            user_email=user["email"],
                            filename=uploaded_file.name,
                            skills=analysis["skills"],
                            strengths=analysis["strengths"],
                            suggestions=analysis["suggestions"],
                            word_count=analysis["word_count"],
                            ats_score=analysis["ats_score"]
                        )
                        st.toast("✅ Resume analysis complete & saved!", icon="🎉")
                        st.rerun()

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # LOWER SECTION: Recent Uploads (Left) + Your Career Journey, Powered by AI (Right)
        col_lower_left, col_lower_right = st.columns([1.1, 1.55])

        # Query recent scans from database
        user_scans = database.get_user_resume_history(user["email"], limit=5)
        latest_scan = user_scans[0] if user_scans else None
        
        with col_lower_left:
            scan_filename = latest_scan.get("filename", f"{user_name.lower()}_resume.pdf") if latest_scan else f"{user_name.lower()}_resume.pdf"
            scan_date = latest_scan.get("uploaded_at").strftime("%b %d, %Y") if latest_scan and hasattr(latest_scan.get("uploaded_at"), "strftime") else "Apr 27, 2025"
            
            st.markdown(f"""<div class="dash-lower-card">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
<div style="display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.18rem; color: #0f172a;">
<span>🕒</span> Recent Uploads
</div>
<span style="font-weight: 800; font-size: 0.92rem; color: #2563eb; cursor: pointer;">View All ➔</span>
</div>
<div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center;">
<div style="display: flex; align-items: center; gap: 16px;">
<div style="width: 40px; height: 40px; background: #fee2e2; color: #dc2626; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 12px;">
PDF
</div>
<div>
<div style="font-weight: 800; font-size: 1.05rem; color: #0f172a;">{scan_filename}</div>
<div style="font-size: 0.86rem; color: #64748b; font-weight: 500;">Uploaded on {scan_date} • 2.4 MB</div>
</div>
</div>
<div style="display: flex; align-items: center; gap: 12px;">
<span style="background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; padding: 6px 16px; border-radius: 20px; font-weight: 800; font-size: 0.85rem;">
Analyzed
</span>
<span style="color: #94a3b8; font-size: 18px;">➔</span>
</div>
</div>
</div>""", unsafe_allow_html=True)

        with col_lower_right:
            ats_val = f"{latest_scan.get('ats_score')}%" if latest_scan else "--"
            skills_val = f"{len(latest_scan.get('skills', []))}" if latest_scan else "--"
            recom_val = f"{len(latest_scan.get('suggestions', []))}" if latest_scan else "--"

            st.markdown(f"""<div class="dash-lower-card">
<div style="margin-bottom: 18px;">
<div style="display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.18rem; color: #0f172a;">
<span>✨</span> Your Career Journey, Powered by AI
</div>
<div style="font-size: 0.92rem; color: #64748b; margin-top: 5px; font-weight: 500;">
Smarter analysis. Better insights. A brighter future.
</div>
</div>
<div style="display: flex; gap: 14px; align-items: center;">
<div class="metric-stat-box">
<div style="width: 42px; height: 42px; border-radius: 12px; background: #eff6ff; color: #2563eb; display: flex; align-items: center; justify-content: center; font-size: 20px;">
🎯
</div>
<div>
<div style="font-size: 0.82rem; font-weight: 700; color: #64748b;">ATS Score</div>
<div style="font-size: 1.3rem; font-weight: 900; color: #0f172a;">{ats_val}</div>
</div>
</div>
<div class="metric-stat-box">
<div style="width: 42px; height: 42px; border-radius: 12px; background: #eff6ff; color: #0284c7; display: flex; align-items: center; justify-content: center; font-size: 20px;">
🎓
</div>
<div>
<div style="font-size: 0.82rem; font-weight: 700; color: #64748b;">Skills Matched</div>
<div style="font-size: 1.3rem; font-weight: 900; color: #0f172a;">{skills_val}</div>
</div>
</div>
<div class="metric-stat-box">
<div style="width: 42px; height: 42px; border-radius: 12px; background: #fffbeb; color: #d97706; display: flex; align-items: center; justify-content: center; font-size: 20px;">
💡
</div>
<div>
<div style="font-size: 0.82rem; font-weight: 700; color: #64748b;">Recommendations</div>
<div style="font-size: 1.3rem; font-weight: 900; color: #0f172a;">{recom_val}</div>
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

        # If analysis results are actively loaded, show detailed cards below
        if st.session_state.analysis_results:
            analysis = st.session_state.analysis_results
            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
            
            c_skills, c_feedback = st.columns([1.1, 1.2])
            with c_skills:
                st.markdown("""
                    <div class="glass-panel">
                        <h3 style="margin-top: 0; font-size: 1.3rem; color: #0f172a;">🎯 Extracted Technical Stack</h3>
                        <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 14px;">Verified competencies detected by local AI parser:</p>
                """, unsafe_allow_html=True)
                if analysis["skills"]:
                    pills_html = "".join([f"<span class='tech-pill'>{s}</span>" for s in analysis["skills"]])
                    st.markdown(f"<div style='margin-bottom: 12px;'>{pills_html}</div></div>", unsafe_allow_html=True)
                else:
                    st.info("No standard skills detected.")
                    st.markdown("</div>", unsafe_allow_html=True)

            with c_feedback:
                st.markdown("""
                    <div class="glass-panel">
                        <h3 style="margin-top: 0; font-size: 1.3rem; color: #0f172a;">💡 Actionable Resume Recommendations</h3>
                """, unsafe_allow_html=True)
                for strength in analysis.get("strengths", []):
                    st.markdown(f"<div class='insight-card insight-card-green'>✓ {strength}</div>", unsafe_allow_html=True)
                for item in analysis.get("suggestions", []):
                    st.markdown(f"<div class='insight-card insight-card-amber'>⚠ {item}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)


    # ==========================================================================
    # 2. PROCTORED SKILL ASSESSMENT & SHORTCUT ROADMAP VIEW
    # ==========================================================================
    elif st.session_state.nav_page == "📝 Proctored Mock Test":
        
        # --- STATE A: ROLE SELECTION & PRE-EXAM BRIEF ---
        if not st.session_state.quiz_active and not st.session_state.quiz_finished:
            disable_proctoring()
            st.markdown("""
                <div class="saas-hero">
                    <div class="saas-hero-title">📝 Role-Based Technical Assessment</div>
                    <p class="saas-hero-subtitle">
                        Select your target role. You will receive exactly 15 curated technical questions under real-time AI proctoring rules, followed by a personalized Shortcut Learning Roadmap for your weak areas.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            available_roles = quiz_engine.get_available_roles()

            st.markdown("<h3 style='margin-bottom: 14px; color:#0f172a;'>🎯 Step 1: Select Target Job Role</h3>", unsafe_allow_html=True)
            selected_role = st.selectbox(
                "Select the engineering role you wish to test for:",
                available_roles,
                index=available_roles.index(st.session_state.selected_role) if st.session_state.selected_role in available_roles else 0
            )
            st.session_state.selected_role = selected_role

            st.markdown("""
                <div class="glass-panel" style="margin-top: 18px;">
                    <h3 style="color: #0f172a; margin-top: 0; font-size: 1.3rem;">🛡️ Mandatory Exam Security Rules</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin-top: 14px;">
                        <div style="background: #eff6ff; padding: 16px; border-radius: 14px; border-left: 4px solid #2563eb; border: 1px solid #bfdbfe;">
                            <strong style="color: #1e40af;">🖥️ Fullscreen Required</strong><br>
                            <span style="color:#475569; font-size:0.88rem;">Exiting fullscreen triggers immediate security lockdown.</span>
                        </div>
                        <div style="background: #eff6ff; padding: 16px; border-radius: 14px; border-left: 4px solid #2563eb; border: 1px solid #bfdbfe;">
                            <strong style="color: #1e40af;">⚠️ Tab-Switch Tracking</strong><br>
                            <span style="color:#475569; font-size:0.88rem;">Switching tabs or minimizing triggers security violation flags.</span>
                        </div>
                        <div style="background: #eff6ff; padding: 16px; border-radius: 14px; border-left: 4px solid #2563eb; border: 1px solid #bfdbfe;">
                            <strong style="color: #1e40af;">🚫 Clipboard Disabled</strong><br>
                            <span style="color:#475569; font-size:0.88rem;">Right-click, Copy, Cut, and Paste shortcuts are blocked.</span>
                        </div>
                        <div style="background: #eff6ff; padding: 16px; border-radius: 14px; border-left: 4px solid #2563eb; border: 1px solid #bfdbfe;">
                            <strong style="color: #1e40af;">🗺️ Shortcut Roadmap</strong><br>
                            <span style="color:#475569; font-size:0.88rem;">Post-exam diagnostic identifies weak areas with direct study links.</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            render_proctor_self_test()
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            if st.button(f"Generate 15 Questions & Start Proctored Exam for {selected_role} ➔", type="primary", use_container_width=True):
                # Generate exact 15 questions for the chosen role
                st.session_state.quiz_questions = quiz_engine.generate_test_for_role(selected_role, 15)
                st.session_state.current_q_index = 0
                st.session_state.user_answers = {}
                st.session_state.score = 0
                st.session_state.roadmap_data = None
                st.session_state.quiz_active = True
                st.session_state.quiz_finished = False
                st.session_state.exam_start_time = datetime.now().timestamp()
                st.rerun()

        # --- STATE B: ACTIVE EXAM ROOM WITH PROCTORING ---
        elif st.session_state.quiz_active and not st.session_state.quiz_finished:
            enable_proctoring()
            questions = st.session_state.quiz_questions
            total_q = len(questions)
            curr_idx = st.session_state.current_q_index

            # Calculate remaining time (20 minutes default)
            start_ts = st.session_state.get("exam_start_time", datetime.now().timestamp())
            elapsed = int(datetime.now().timestamp() - start_ts)
            total_duration = 20 * 60
            remaining = max(0, total_duration - elapsed)
            rem_m = remaining // 60
            rem_s = remaining % 60
            answered_cnt = len(st.session_state.user_answers)

            # Exam Header Card in White & Blue
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; background:#ffffff; border:1.5px solid #bfdbfe; border-radius:20px; padding:16px 26px; margin-bottom:18px; box-shadow:0 10px 30px rgba(37,99,235,0.08);">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span class="tech-pill" style="font-size:0.85rem; padding:4px 14px;">{st.session_state.selected_role}</span>
                        <span style="color:#64748b; font-size:0.92rem; font-weight:600;">Proctored Examination</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:18px;">
                        <span style="background:#eff6ff; color:#1d4ed8; border:1.5px solid #93c5fd; padding:6px 16px; border-radius:20px; font-weight:800; font-size:0.92rem; display:inline-flex; align-items:center; gap:6px;">
                            ⏱️ {rem_m:02d}:{rem_s:02d} Remaining
                        </span>
                        <span style="color:#0f172a; font-weight:800; font-size:0.95rem;">Answered: {answered_cnt} / {total_q}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Question Palette (Pill Buttons 1 to 15)
            palette_cols = st.columns(15)
            for i in range(total_q):
                with palette_cols[i]:
                    is_current = (i == curr_idx)
                    is_answered = (i in st.session_state.user_answers)
                    if is_current:
                        btn_label = f"[{i+1}]"
                        b_type = "primary"
                    elif is_answered:
                        btn_label = f"✓{i+1}"
                        b_type = "secondary"
                    else:
                        btn_label = f"{i+1}"
                        b_type = "secondary"
                        
                    if st.button(btn_label, key=f"nav_q_{i}", type=b_type, use_container_width=True):
                        st.session_state.current_q_index = i
                        st.rerun()

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            q_data = questions[curr_idx]

            # Question Card
            st.markdown(f"""
                <div class="glass-panel" style="border-left: 5px solid #2563eb; padding: 28px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="tech-pill" style="font-size:0.85rem; padding:4px 14px;">Topic: {q_data.get('topic', 'Core')}</span>
                        <span style="color:#1d4ed8; font-weight:800; font-size:1.05rem;">Question {curr_idx + 1} of {total_q}</span>
                    </div>
                    <h2 style="margin-top: 18px; font-size: 1.5rem; color: #0f172a; line-height: 1.5;">{q_data['q']}</h2>
                </div>
            """, unsafe_allow_html=True)

            # Radio Option Selection
            saved_ans = st.session_state.user_answers.get(curr_idx, None)
            chosen_option = st.radio(
                "Choose Option:",
                q_data["options"],
                index=saved_ans if saved_ans is not None else None,
                key=f"radio_q_{curr_idx}"
            )

            # Save selection immediately
            if chosen_option is not None:
                st.session_state.user_answers[curr_idx] = q_data["options"].index(chosen_option)

            # Unanswered notice banner if not finished
            unanswered_count = total_q - len(st.session_state.user_answers)
            if unanswered_count > 0:
                st.caption(f"ℹ️ {unanswered_count} question(s) left unanswered. You can navigate between questions using the numbers above.")

            # Navigation buttons
            c_prev, c_clear, c_next, c_submit = st.columns([1, 1, 1.4, 1.6])
            with c_prev:
                if st.button("⬅ Previous", disabled=(curr_idx == 0), use_container_width=True):
                    st.session_state.current_q_index -= 1
                    st.rerun()
            with c_clear:
                if saved_ans is not None:
                    if st.button("Clear Answer ✕", use_container_width=True):
                        st.session_state.user_answers.pop(curr_idx, None)
                        st.rerun()
                else:
                    st.write("")
            with c_next:
                if curr_idx < total_q - 1:
                    if st.button("Next Question ➔", type="primary", use_container_width=True):
                        st.session_state.current_q_index += 1
                        st.rerun()
                else:
                    st.write("")
            with c_submit:
                btn_type = "primary" if curr_idx == total_q - 1 else "secondary"
                if st.button("Submit & Finalize Exam 🏁", type=btn_type, use_container_width=True):
                    # Grade exam
                    correct_count = 0
                    answers_record = []
                    for i, q in enumerate(questions):
                        user_ans = st.session_state.user_answers.get(i, -1)
                        answers_record.append(user_ans)
                        if user_ans == q["ans"]:
                            correct_count += 1
                            
                    st.session_state.score = correct_count
                    
                    # Generate Diagnostic Roadmap
                    roadmap = quiz_engine.build_diagnostic_roadmap(
                        st.session_state.selected_role,
                        questions,
                        answers_record
                    )
                    st.session_state.roadmap_data = roadmap
                    
                    # Save to MongoDB
                    skills_tested = list(set([q.get("topic", "General") for q in questions]))
                    weak_topics = [s["topic"] for s in roadmap.get("roadmap_steps", [])]
                    
                    database.save_test_result(
                        user_email=user["email"],
                        score=correct_count,
                        total=total_q,
                        skills_tested=skills_tested,
                        role=st.session_state.selected_role,
                        weak_topics=weak_topics,
                        roadmap=roadmap.get("roadmap_steps", [])
                    )

                    st.session_state.quiz_active = False
                    st.session_state.quiz_finished = True
                    disable_proctoring()
                    st.rerun()

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            col_forfeit, _ = st.columns([1, 4])
            with col_forfeit:
                if st.button("Forfeit Exam", use_container_width=True):
                    disable_proctoring()
                    reset_quiz()
                    st.rerun()

        # --- STATE C: RESULTS & PERSONALIZED SHORTCUT LEARNING ROADMAP ---
        elif st.session_state.quiz_finished:
            disable_proctoring()
            score = st.session_state.score
            questions = st.session_state.quiz_questions
            total = len(questions)
            pct = round((score / total) * 100, 1) if total > 0 else 0
            roadmap = st.session_state.roadmap_data or {}
            role = st.session_state.selected_role

            st.markdown(f"""
                <div class="saas-hero">
                    <div class="saas-hero-title">📊 Assessment Score & Diagnostic Learning Blueprint</div>
                    <p class="saas-hero-subtitle">
                        Role Tested: <strong>{role}</strong> • Synced with your verified candidate profile.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Benchmark Performance Classification Banner
            if pct >= 80:
                st.markdown("""
                    <div style="background:#f0fdf4; border:1.5px solid #86efac; border-left:5px solid #16a34a; border-radius:16px; padding:18px 24px; margin-bottom:20px;">
                        <h4 style="margin:0 0 6px 0; color:#166534; font-size:1.15rem;">🏆 Senior Competency Level Achieved</h4>
                        <span style="color:#15803d; font-size:0.95rem;">Outstanding technical proficiency demonstrated across architecture, security, and best practices.</span>
                    </div>
                """, unsafe_allow_html=True)
            elif pct >= 60:
                st.markdown("""
                    <div style="background:#eff6ff; border:1.5px solid #93c5fd; border-left:5px solid #2563eb; border-radius:16px; padding:18px 24px; margin-bottom:20px;">
                        <h4 style="margin:0 0 6px 0; color:#1e40af; font-size:1.15rem;">⚡ Proficient Competency Baseline</h4>
                        <span style="color:#1d4ed8; font-size:0.95rem;">Strong engineering grasp. Review the targeted shortcut roadmap steps below to bridge remaining knowledge gaps.</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="background:#fffbeb; border:1.5px solid #fde68a; border-left:5px solid #d97706; border-radius:16px; padding:18px 24px; margin-bottom:20px;">
                        <h4 style="margin:0 0 6px 0; color:#92400e; font-size:1.15rem;">🎯 Foundational Skill Phase</h4>
                        <span style="color:#b45309; font-size:0.95rem;">Follow the personalized shortcut curriculum below to rapidly advance your technical competencies.</span>
                    </div>
                """, unsafe_allow_html=True)

            # Score Cards in White & Blue
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-val">{score} / {total}</div>
                        <div class="metric-lbl">Total Score</div>
                    </div>
                """, unsafe_allow_html=True)
            with s2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-val">{pct}%</div>
                        <div class="metric-lbl">Proficiency Grade</div>
                    </div>
                """, unsafe_allow_html=True)
            with s3:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-val" style="color:#16a34a;">{roadmap.get('strong_count', 0)}</div>
                        <div class="metric-lbl">Mastered Topics</div>
                    </div>
                """, unsafe_allow_html=True)
            with s4:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-val" style="color:#ea580c;">{roadmap.get('weak_count', 0)}</div>
                        <div class="metric-lbl">Areas to Strengthen</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

            # Mastered Strengths
            if roadmap.get("strong_topics"):
                st.markdown("<h3 style='color:#0f172a;'>🏆 Mastered Concepts Matrix</h3>", unsafe_allow_html=True)
                pills = "".join([f"<span class='tech-pill' style='background:#f0fdf4; border-color:#86efac; color:#166534;'>✓ {t}</span>" for t in roadmap["strong_topics"]])
                st.markdown(f"<div style='margin-bottom:24px;'>{pills}</div>", unsafe_allow_html=True)

            # MASS VISUAL MILESTONE ROADMAP SECTION
            steps = roadmap.get("roadmap_steps", [])
            total_steps = len(steps)
            est_total_hours = sum([1.0 if "Hour" in s.get("est_time", "") else 0.4 for s in steps])
            
            st.markdown(f"""
                <div class="glass-panel" style="border: 1.5px solid #bfdbfe; margin-top: 14px; padding: 32px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px; margin-bottom: 8px;">
                        <div>
                            <span class="roadmap-stage-pill stage-foundation" style="font-size: 12px; margin-bottom: 8px;">🚀 Customized Career Blueprint</span>
                            <h2 style="color: #0f172a; margin: 4px 0 0 0; font-size: 1.85rem; font-weight: 900; letter-spacing: -0.6px;">
                                🗺️ Career Mastery Roadmap: {role}
                            </h2>
                            <p style="color: #64748b; font-size: 1rem; margin: 6px 0 0 0;">
                                Precision diagnostic track built from your exam analytics to fast-track senior competence.
                            </p>
                        </div>
                        <div style="display: flex; gap: 12px; align-items: center;">
                            <div style="background: #ffffff; border: 1.5px solid #bfdbfe; border-radius: 16px; padding: 10px 18px; text-align: center; box-shadow: 0 4px 12px rgba(37,99,235,0.06);">
                                <div style="font-size: 1.3rem; font-weight: 900; color: #2563eb;">{total_steps}</div>
                                <div style="font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase;">Milestones</div>
                            </div>
                            <div style="background: #ffffff; border: 1.5px solid #bfdbfe; border-radius: 16px; padding: 10px 18px; text-align: center; box-shadow: 0 4px 12px rgba(37,99,235,0.06);">
                                <div style="font-size: 1.3rem; font-weight: 900; color: #16a34a;">~{round(est_total_hours, 1)}h</div>
                                <div style="font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase;">Est. Sprint</div>
                            </div>
                        </div>
                    </div>

                    <!-- Visual Track Progress -->
                    <div style="margin-top: 20px;">
                        <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 800; color: #475569; margin-bottom: 6px;">
                            <span>🏁 Foundation (Day 1)</span>
                            <span>⚡ Core Competency (Week 1)</span>
                            <span>🏆 Production Mastery (Target)</span>
                        </div>
                        <div class="roadmap-progress-bar">
                            <div class="roadmap-progress-fill" style="width: 100%;"></div>
                        </div>
                    </div>
            """, unsafe_allow_html=True)

            if steps:
                st.markdown('<div class="roadmap-track">', unsafe_allow_html=True)
                for step_idx, step in enumerate(steps, 1):
                    # Classify stage dynamically
                    if step_idx <= 2:
                        stage_label = "STAGE 1 • FOUNDATION"
                        stage_pill_class = "stage-foundation"
                    elif step_idx <= 4:
                        stage_label = "STAGE 2 • CORE ARCHITECTURE"
                        stage_pill_class = "stage-core"
                    else:
                        stage_label = "STAGE 3 • ADVANCED MASTERY"
                        stage_pill_class = "stage-mastery"

                    is_high = "HIGH" in step.get("priority", "")
                    priority_badge = (
                        '<span style="background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.78rem;">🚨 CRITICAL MILESTONE</span>'
                        if is_high else
                        '<span style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.78rem;">⚡ ACCELERATOR</span>'
                    )

                    st.markdown(f"""
                        <div class="roadmap-node">
                            <div class="roadmap-marker">{step_idx}</div>
                            <div class="roadmap-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <span class="roadmap-stage-pill {stage_pill_class}">{stage_label}</span>
                                        {priority_badge}
                                    </div>
                                    <span style="background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem;">
                                        ⏱️ Expected Effort: {step['est_time']}
                                    </span>
                                </div>
                                
                                <h3 style="margin: 0 0 10px 0; font-size: 1.38rem; font-weight: 800; color: #0f172a;">
                                    {step['topic']}
                                </h3>
                                
                                <p style="color: #475569; font-size: 0.96rem; line-height: 1.6; margin: 0 0 14px 0;">
                                    <strong style="color: #0f172a;">Core Concept Breakdown:</strong> {step['explanation']}
                                </p>
                                
                                <div style="background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%); border: 1.5px solid #bfdbfe; border-left: 5px solid #2563eb; border-radius: 12px; padding: 14px 18px; margin-bottom: 16px;">
                                    <div style="font-size: 0.82rem; font-weight: 800; color: #1e40af; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
                                        🧠 Senior Architect Mental Model / Memory Hack
                                    </div>
                                    <div style="font-size: 0.95rem; font-weight: 600; color: #0f172a; line-height: 1.5;">
                                        {step['shortcut_tip']}
                                    </div>
                                </div>
                                
                                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                                    <a href="{step['doc_url']}" target="_blank" style="display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(90deg, #0284c7 0%, #2563eb 50%, #3b82f6 100%); color: #ffffff; text-decoration: none; padding: 10px 22px; border-radius: 12px; font-weight: 800; font-size: 0.88rem; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3); transition: transform 0.2s ease;">
                                        <span>📖 Open Official Documentation &amp; Labs</span> ➔
                                    </a>
                                    <span style="font-size: 0.85rem; font-weight: 700; color: #64748b;">
                                        Diagnostic Source: Missed Question #{step.get('step', step_idx)}
                                    </span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.balloons()
                st.markdown("""
                    <div style="text-align: center; padding: 40px 20px;">
                        <div style="font-size: 54px; margin-bottom: 12px;">🏆</div>
                        <h3 style="color: #16a34a; font-size: 1.6rem; font-weight: 900; margin: 0 0 8px 0;">Flawless Score! Complete Technical Mastery</h3>
                        <p style="color: #475569; max-width: 580px; margin: 0 auto; font-size: 1rem; line-height: 1.6;">
                            You answered all 15 exam questions correctly. No critical conceptual gaps detected. You are ready for live technical interviews in this domain!
                        </p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # DETAILED QUESTION-BY-QUESTION REVIEW
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            with st.expander("🔍 Complete Question-by-Question Diagnostic Review (All 15 Questions)", expanded=False):
                for idx, q in enumerate(questions):
                    user_ans_idx = st.session_state.user_answers.get(idx, -1)
                    is_ans_correct = (user_ans_idx == q["ans"])
                    user_choice_text = q["options"][user_ans_idx] if 0 <= user_ans_idx < len(q["options"]) else "Unanswered"
                    correct_choice_text = q["options"][q["ans"]]
                    
                    status_badge = '<span style="background:#dcfce7; color:#15803d; border:1px solid #86efac; padding:4px 12px; border-radius:14px; font-weight:800; font-size:0.82rem;">✓ Correct (+1 pt)</span>' if is_ans_correct else '<span style="background:#fee2e2; color:#b91c1c; border:1px solid #fca5a5; padding:4px 12px; border-radius:14px; font-weight:800; font-size:0.82rem;">✗ Missed (0 pts)</span>'
                    
                    st.markdown(f"""
                        <div style="background:#ffffff; border:1.5px solid #e2e8f0; border-radius:16px; padding:20px; margin-bottom:14px; box-shadow:0 2px 8px rgba(15,23,42,0.03);">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                <span style="font-weight:800; color:#1d4ed8; font-size:0.95rem;">Question {idx + 1} • {q.get('topic', 'General')}</span>
                                {status_badge}
                            </div>
                            <h4 style="margin:0 0 12px 0; color:#0f172a; font-size:1.05rem;">{q['q']}</h4>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:0.92rem; margin-bottom:12px;">
                                <div style="background:#f8fafc; padding:10px 14px; border-radius:10px; border:1px solid #e2e8f0;">
                                    <strong style="color:#64748b;">Your Selection:</strong><br>
                                    <span style="color:{ '#15803d' if is_ans_correct else '#b91c1c' }; font-weight:700;">{user_choice_text}</span>
                                </div>
                                <div style="background:#eff6ff; padding:10px 14px; border-radius:10px; border:1px solid #bfdbfe;">
                                    <strong style="color:#1e40af;">Correct Answer:</strong><br>
                                    <span style="color:#1d4ed8; font-weight:700;">{correct_choice_text}</span>
                                </div>
                            </div>
                            <div style="background:#f8fafc; padding:12px 14px; border-radius:10px; border:1px solid #e2e8f0; font-size:0.9rem; color:#475569; line-height:1.5;">
                                <strong>Rationale:</strong> {q.get('explanation', '')}<br>
                                <span style="color:#1d4ed8; font-weight:600;">💡 Shortcut: {q.get('shortcut_tip', '')}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            c_retake, c_back = st.columns(2)
            with c_retake:
                if st.button("Take Another Assessment ↺", type="primary", use_container_width=True):
                    reset_quiz()
                    st.rerun()
            with c_back:
                if st.button("Return to Performance Dashboard ➔", use_container_width=True):
                    reset_quiz()
                    st.session_state.nav_page = "📊 Performance Dashboard"
                    st.rerun()

    # ==========================================================================
    # 3. PERFORMANCE DASHBOARD VIEW (FROM MONGODB)
    # ==========================================================================
    elif st.session_state.nav_page == "📊 Performance Dashboard":
        disable_proctoring()
        st.markdown("""
            <div class="saas-hero">
                <div class="saas-hero-title">📊 Candidate Performance & Telemetry</div>
                <p class="saas-hero-subtitle">
                    Comprehensive audit log of historical resume scans, ATS ratings, and proctored technical exam scores.
                </p>
            </div>
        """, unsafe_allow_html=True)

        scans = database.get_user_resume_history(user["email"], limit=15)
        tests = database.get_user_test_history(user["email"], limit=15)

        # 4 High-impact Stat Widgets
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{len(scans)}</div>
                    <div class="metric-lbl">Total Resumes Scanned</div>
                </div>
            """, unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{len(tests)}</div>
                    <div class="metric-lbl">Assessments Completed</div>
                </div>
            """, unsafe_allow_html=True)
        with s3:
            avg_ats = round(sum(s.get("ats_score", 0) for s in scans) / len(scans)) if scans else 0
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{avg_ats}%</div>
                    <div class="metric-lbl">Average ATS Score</div>
                </div>
            """, unsafe_allow_html=True)
        with s4:
            best_score = max((t.get("percentage", 0) for t in tests), default=0) if tests else 0
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{best_score}%</div>
                    <div class="metric-lbl">Highest Exam Score</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        tab_scans, tab_tests = st.tabs(["📄 Resume Scan Log", "📝 Proctored Exam Log"])

        with tab_scans:
            if scans:
                for scan in scans:
                    dt = scan.get("uploaded_at")
                    dt_str = dt.strftime("%Y-%m-%d %H:%M") if hasattr(dt, "strftime") else str(dt)[:16]
                    skills_list = scan.get("skills", [])
                    pills = "".join([f"<span class='tech-pill' style='font-size:0.75rem; padding: 2px 9px;'>{s}</span>" for s in skills_list[:8]])
                    
                    st.markdown(f"""
                        <div class="history-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong style="color: #0f172a; font-size: 1.1rem;">📄 {scan.get('filename', 'Resume.pdf')}</strong>
                                <span style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 4px 14px; border-radius: 20px; font-weight: 800; font-size: 0.85rem;">
                                    ATS: {scan.get('ats_score', 'N/A')}%
                                </span>
                            </div>
                            <div style="color: #64748b; font-size: 0.82rem; margin: 6px 0 10px 0;">Uploaded: {dt_str} • Document Length: {scan.get('word_count', 0)} words</div>
                            <div>{pills}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No resume scan history found for this account. Upload a resume in the Analyzer tab to populate.")

        with tab_tests:
            if tests:
                for test in tests:
                    ts = test.get("timestamp")
                    ts_str = ts.strftime("%Y-%m-%d %H:%M") if hasattr(ts, "strftime") else str(ts)[:16]
                    test_role = test.get("role", "General Engineering")
                    weak_list = test.get("weak_topics", [])
                    weak_pills = "".join([f"<span class='tech-pill' style='font-size:0.75rem; padding:2px 8px; border-color:#fca5a5; background:#fee2e2; color:#b91c1c;'>⚠ {w}</span>" for w in weak_list[:4]])
                    
                    st.markdown(f"""
                        <div class="history-card" style="border-left-color: #2563eb;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong style="color: #0f172a; font-size: 1.1rem;">📝 {test_role} Exam</strong>
                                <span style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 4px 14px; border-radius: 20px; font-weight: 800; font-size: 0.85rem;">
                                    {test.get('score', 0)} / {test.get('total', 0)} ({test.get('percentage', 0)}%)
                                </span>
                            </div>
                            <div style="color: #64748b; font-size: 0.82rem; margin: 6px 0 8px 0;">Completed on: {ts_str}</div>
                            {f"<div style='margin-top:6px;'>Weak Topics Identified: {weak_pills}</div>" if weak_list else ""}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No assessment logs recorded. Take your first proctored test in the Assessment tab.")

    # ==========================================================================
    # 4. DATABASE MONITOR & DIAGNOSTICS VIEW
    # ==========================================================================
    elif st.session_state.nav_page == "⚙️ Database Monitor":
        disable_proctoring()
        st.markdown("""
            <div class="saas-hero">
                <div class="saas-hero-title">⚙️ Enterprise Cluster Telemetry</div>
                <p class="saas-hero-subtitle">
                    Inspect active collections, document volume, and infrastructure connection parameters.
                </p>
            </div>
        """, unsafe_allow_html=True)

        is_connected, msg = database.check_db_connection()
        stats = database.get_db_stats()

        d1, d2, d3 = st.columns(3)
        with d1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val" style="color: { '#16a34a' if is_connected else '#dc2626' }; font-size: 2.5rem;">{ 'ACTIVE 🟢' if is_connected else 'OFFLINE ⚪' }</div>
                    <div class="metric-lbl">Cluster Engine Status</div>
                </div>
            """, unsafe_allow_html=True)
        with d2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val" style="font-size: 2.2rem; color: #1d4ed8;">{stats.get('database', 'career_path_ai')}</div>
                    <div class="metric-lbl">Active Database Name</div>
                </div>
            """, unsafe_allow_html=True)
        with d3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{stats.get('users', 0)}</div>
                    <div class="metric-lbl">Registered Accounts</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 12px; color:#0f172a;'>📦 Collection Document Counts</h3>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
                <div class="glass-panel" style="text-align: center;">
                    <div style="font-size: 2rem;">👥</div>
                    <h4 style="margin: 6px 0; color: #0f172a;">users</h4>
                    <p style="font-size: 2.2rem; font-weight: 800; color: #1d4ed8; margin: 0;">{stats.get('users', 0)}</p>
                    <small style="color: #64748b;">Encrypted bcrypt user profiles</small>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class="glass-panel" style="text-align: center;">
                    <div style="font-size: 2rem;">📄</div>
                    <h4 style="margin: 6px 0; color: #0f172a;">resume_scans</h4>
                    <p style="font-size: 2.2rem; font-weight: 800; color: #1d4ed8; margin: 0;">{stats.get('scans', 0)}</p>
                    <small style="color: #64748b;">Parsed resumes & ATS metrics</small>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
                <div class="glass-panel" style="text-align: center;">
                    <div style="font-size: 2rem;">📝</div>
                    <h4 style="margin: 6px 0; color: #0f172a;">mock_tests</h4>
                    <p style="font-size: 2.2rem; font-weight: 800; color: #1d4ed8; margin: 0;">{stats.get('tests', 0)}</p>
                    <small style="color: #64748b;">Assessment question grades</small>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("""
            <div class="glass-panel" style="margin-top: 14px;">
                <h4 style="margin-top: 0; color: #0f172a;">🔌 Connection Endpoint Details</h4>
        """, unsafe_allow_html=True)
        st.code(f"Server URI: {database.MONGO_URI}\nDatabase: {database.DB_NAME}\nStorage Engine: WiredTiger (MongoDB 7.0 Windows Local)", language="yaml")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Ping & Refresh Cluster Status ↺", type="primary"):
            st.rerun()


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================
if st.session_state.user is None:
    render_auth_page()
else:
    render_main_app()
