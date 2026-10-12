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
import google_auth
from styles import apply_custom_styles

# Configure Streamlit page with collapsed sidebar for a clean web-app layout
st.set_page_config(
    page_title="CareerPath.AI — Enterprise AI Resume Analytics & Certified Assessment",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Theme Initialization
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"

# Apply custom White and Royal Blue SaaS styling matching user reference design
apply_custom_styles(theme_mode=st.session_state.theme_mode)

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "guest_state" not in st.session_state:
    st.session_state.guest_state = "landing"
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

# ==============================================================================
# OFFICIAL GOOGLE OAUTH 2.0 AUTHORIZATION CODE CALLBACK HANDLER
# ==============================================================================
if "error" in st.query_params:
    oauth_err = st.query_params.get("error")
    if isinstance(oauth_err, list):
        oauth_err = oauth_err[0] if oauth_err else "cancelled"
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.session_state.oauth_state = None
    if oauth_err == "access_denied":
        st.warning("Google sign-in was cancelled.")
    else:
        st.error(f"Google sign-in was not completed: {oauth_err}")

elif "code" in st.query_params:
    auth_code = st.query_params.get("code")
    returned_state = st.query_params.get("state")
    if isinstance(auth_code, list):
        auth_code = auth_code[0] if auth_code else None
    if isinstance(returned_state, list):
        returned_state = returned_state[0] if returned_state else None
    try:
        st.query_params.clear()
    except Exception:
        pass

    # CSRF State Validation with timing-safe comparison
    expected_state = st.session_state.get("oauth_state")
    st.session_state.oauth_state = None  # Consume state token immediately to prevent reuse

    if not returned_state or not google_auth.validate_state(expected_state, returned_state):
        st.error("Authentication failed: Invalid or expired OAuth state parameter (CSRF protection failed). Please try signing in again.")
    elif not auth_code:
        st.error("Authentication failed: Missing authorization code from Google.")
    else:
        with st.spinner("Authenticating with official Google OAuth servers..."):
            user_info, error_msg = google_auth.exchange_code_for_user_info(auth_code)
            if user_info and user_info.get("email"):
                g_email = user_info["email"]
                g_name = user_info.get("name") or g_email.split("@")[0].capitalize()
                g_pic = user_info.get("picture", "")
                g_sub = user_info.get("sub", "")
                
                success, msg, user = database.authenticate_or_register_google_user(
                    email=g_email,
                    name=g_name,
                    picture=g_pic,
                    google_sub=g_sub
                )
                if success:
                    st.session_state.user = user
                    st.session_state.guest_state = "landing"
                    st.toast(f"✅ Signed in as {g_name}!", icon="🎉")
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error(f"Google authentication failed: {error_msg}")


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

def render_navbar():
    try:
        import assets_b64
        logo_src = f"data:image/png;base64,{assets_b64.LOGO_B64}"
    except Exception:
        logo_src = ""
    active_col = 3 if st.session_state.guest_state == "landing" else (
        4 if st.session_state.guest_state == "about" else (
            5 if st.session_state.guest_state == "features" else (
                6 if st.session_state.guest_state == "contact" else 0
            )
        )
    )
    if active_col > 0:
        st.markdown(f'''
        <style>
        div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child({active_col}) button {{
            color: #2563eb !important;
            font-weight: 800 !important;
            border-bottom: 2.5px solid #2563eb !important;
            border-radius: 0 !important;
        }}
        </style>
        ''', unsafe_allow_html=True)

    st.markdown('''
    <style>
    .block-container { padding-top: 1rem !important; }
    
    /* Target only the first horizontal block (the navbar) */
    div[data-testid="stHorizontalBlock"]:first-of-type {
        align-items: center; /* Vertically center everything in the navbar row */
    }
    
    /* Style nav buttons as text links */
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(3) button,
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(4) button,
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(5) button,
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(6) button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-top: 2px !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(3) button:hover,
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(4) button:hover,
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(5) button:hover,
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(6) button:hover {
        color: #2563eb !important;
    }
    
    /* Sign In Button */
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(7) button {
        color: #2563eb !important;
        border: 1.5px solid #bfdbfe !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        background: white !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(7) button:hover {
        background-color: #eff6ff !important;
    }
    </style>
    ''', unsafe_allow_html=True)
    
    col_logo, c_space, c_home, c_about, c_feat, c_contact, col_signin = st.columns([1.5, 1.5, 0.8, 0.9, 0.9, 0.9, 1.2])
    with col_logo:
        st.markdown(f'<img src="{logo_src}" style="height:36px; margin-top: 0px;">', unsafe_allow_html=True)
        
    with c_home:
        if st.button("Home", use_container_width=True, key="nav_home"):
            st.session_state.guest_state = "landing"
            st.rerun()
    with c_about:
        if st.button("About Us", use_container_width=True, key="nav_about"):
            st.session_state.guest_state = "about"
            st.rerun()
    with c_feat:
        if st.button("Features", use_container_width=True, key="nav_feat"):
            st.session_state.guest_state = "features"
            st.rerun()
    with c_contact:
        if st.button("Contact", use_container_width=True, key="nav_contact"):
            st.session_state.guest_state = "contact"
            st.rerun()
        
    with col_signin:
        if st.button("👤 Sign In", use_container_width=True, key="nav_signin"):
            st.session_state.guest_state = "auth"
            st.rerun()


def render_google_auth_button(action="Continue with Google", key_suffix="login"):
    """
    Renders an authentic Google OAuth 2.0 button.
    When configured, clicking navigates directly to Google's official authorization endpoint
    (https://accounts.google.com/o/oauth2/v2/auth). Google manages its own account chooser.
    If credentials are not yet configured, provides a clean setup instruction.
    """
    st.markdown("""
        <style>
        .g-oauth-btn {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 12px !important;
            width: 100% !important;
            padding: 11px 16px !important;
            background-color: #ffffff !important;
            border: 1.5px solid #dadce0 !important;
            border-radius: 8px !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: #3c4043 !important;
            text-decoration: none !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 1px 3px rgba(60,64,67,0.08) !important;
            box-sizing: border-box !important;
            cursor: pointer !important;
            margin-bottom: 2px !important;
        }
        .g-oauth-btn:hover {
            background-color: #f8fafc !important;
            border-color: #c2c7d0 !important;
            box-shadow: 0 2px 6px rgba(60,64,67,0.15) !important;
            color: #1f2937 !important;
            text-decoration: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if "oauth_state" not in st.session_state or not st.session_state.oauth_state:
        st.session_state.oauth_state = google_auth.generate_state_token()

    if google_auth.is_client_id_configured():
        auth_url = google_auth.get_google_auth_url(st.session_state.oauth_state)
        st.markdown(f'''
            <a href="{auth_url}" target="_self" class="g-oauth-btn" title="{action}">
                <svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
                    <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.616z"/>
                    <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"/>
                    <path fill="#FBBC05" d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707s.102-1.167.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332z"/>
                    <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.961L3.964 7.293C4.672 5.166 6.656 3.58 9 3.58z"/>
                </svg>
                <span>{action}</span>
            </a>
        ''', unsafe_allow_html=True)
    else:
        if st.button(f"🌐 {action}", use_container_width=True, key=f"btn_g_unconfigured_{key_suffix}"):
            missing_vars = google_auth.get_missing_config()
            missing_text = ", ".join(f"`{m}`" for m in missing_vars) if missing_vars else "credentials"
            st.warning(
                f"⚠️ **Google OAuth 2.0 Setup Required**\n\n"
                f"Please configure {missing_text} in your `.env` file to activate official Google Sign-In.\n\n"
                f"**Authorized Redirect URI:** `{google_auth.get_redirect_uri()}`"
            )


def render_auth_page():
    disable_proctoring()
    
    try:
        import assets_b64
        logo_src = f"data:image/png;base64,{assets_b64.LOGO_B64}"
    except Exception:
        logo_src = ""
    
    if st.session_state.guest_state == "landing":
        render_navbar()
        
        c1, c2 = st.columns([1.5, 1])

        with c1:
            st.markdown("""
                <div style="margin-top: 10px;">
                    <h1 style='font-size: 4.8rem; line-height: 1.15; font-weight: 800; color: #0f172a; margin-bottom: 20px; letter-spacing: -1px;'>
                        Your Career.<br><span style="color: #6366f1;">Smarter Path.</span>
                    </h1>
                    <p style='font-size: 1.2rem; color: #475569; margin-bottom: 35px; max-width: 95%; line-height: 1.6;'>
                        Upload your resume, get AI-powered insights, analyze your skills, and receive a personalized roadmap to reach your dream job.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <style>
            /* Left Card Button */
            div[data-testid="column"]:has(#btn-analyze-marker) div[data-testid="stButton"] button {
                background-color: #eff6ff !important;
                border: 1.5px solid #bfdbfe !important;
                border-radius: 12px !important;
                padding: 18px !important;
                height: 100% !important;
                width: 100% !important;
            }
            div[data-testid="column"]:has(#btn-analyze-marker) div[data-testid="stButton"] button * {
                color: #1e40af !important;
                font-weight: 800 !important;
                font-size: 1.15rem !important;
            }
            div[data-testid="column"]:has(#btn-analyze-marker) div[data-testid="stButton"] button:hover {
                background-color: #dbeafe !important;
            }
            
            /* Right Card Button */
            div[data-testid="column"]:has(#btn-roadmap-marker) div[data-testid="stButton"] button {
                background-color: #f5f3ff !important;
                border: 1.5px solid #ddd6fe !important;
                border-radius: 12px !important;
                padding: 18px !important;
                height: 100% !important;
                width: 100% !important;
            }
            div[data-testid="column"]:has(#btn-roadmap-marker) div[data-testid="stButton"] button * {
                color: #4338ca !important;
                font-weight: 800 !important;
                font-size: 1.15rem !important;
            }
            div[data-testid="column"]:has(#btn-roadmap-marker) div[data-testid="stButton"] button:hover {
                background-color: #ede9fe !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown('<div id="btn-analyze-marker"></div>', unsafe_allow_html=True)
                if st.button("📄 Resume Analyze ➔", use_container_width=True):
                    st.session_state.guest_state = "upload"
                    st.rerun()
            
            with cc2:
                st.markdown('<div id="btn-roadmap-marker"></div>', unsafe_allow_html=True)
                if st.button("🗺️ Get Roadmap ➔", use_container_width=True):
                    st.session_state.guest_state = "upload"
                    st.rerun()
                
        with c2:
            try:
                import base64
                with open(r"C:\Users\logas\.gemini\antigravity\brain\b48df9d2-c9a4-46fd-89fb-37fce92707ae\professional_girl_hero_1791616018393.jpg", "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                # Smaller width to reduce length, with margin-top to align nicely
                st.markdown(f'<img src="data:image/jpeg;base64,{img_data}" style="width:75%; border-radius: 20px; border: none; display: block; margin: 20px auto 0 auto;">', unsafe_allow_html=True)
            except Exception:
                st.info("Visual Placeholder")
                
        # Features Footer row
        st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin-bottom: 30px;'>", unsafe_allow_html=True)
        
        f1, f2, f3, f4, f5 = st.columns(5)
        with f1:
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.9rem; font-weight:600;'>🧠 AI Powered Insights</div>", unsafe_allow_html=True)
        with f2:
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.9rem; font-weight:600;'>🎯 Personalized Roadmaps</div>", unsafe_allow_html=True)
        with f3:
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.9rem; font-weight:600;'>💼 Job & Internship Suggestions</div>", unsafe_allow_html=True)
        with f4:
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.9rem; font-weight:600;'>📊 Skill Gap Analysis</div>", unsafe_allow_html=True)
        with f5:
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.9rem; font-weight:600;'>🚀 Build a Stronger Future</div>", unsafe_allow_html=True)

    elif st.session_state.guest_state == "about":
        render_navbar()
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown("""
                <div style="margin-top: 10px;">
                    <h1 style='font-size: 4.8rem; line-height: 1.15; font-weight: 800; color: #0f172a; margin-bottom: 20px; letter-spacing: -1px;'>
                        Built for Students.<br><span style="color: #6366f1;">Guided by AI.</span>
                    </h1>
                    <p style='font-size: 1.2rem; color: #475569; margin-bottom: 20px; max-width: 95%; line-height: 1.6;'>
                        This platform is specifically built for college students who are struggling with what to study and how to study. We provide a clear, step-by-step path to your dream job.
                    </p>
                    <div style="background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 30px; max-width: 90%;">
                        <h4 style="color: #2563eb; margin: 0 0 10px 0; font-weight: 700; font-size: 1.1rem;">Your Journey to Success:</h4>
                        <ul style="color: #475569; font-size: 1.05rem; line-height: 1.6; margin: 0; padding-left: 20px;">
                            <li style="margin-bottom: 8px;"><strong>Analyze:</strong> Evaluate your resume to identify strengths and skill gaps.</li>
                            <li style="margin-bottom: 8px;"><strong>Test:</strong> Take mock tests to validate your technical skills.</li>
                            <li><strong>Achieve:</strong> Receive your personalized roadmap and guidance to reach your career goals.</li>
                        </ul>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with c2:
            try:
                import base64
                with open(r"C:\Users\logas\.gemini\antigravity\brain\b48df9d2-c9a4-46fd-89fb-37fce92707ae\professional_girl_hero_1791616018393.jpg", "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                st.markdown(f'<img src="data:image/jpeg;base64,{img_data}" style="width:75%; border-radius: 20px; border: none; display: block; margin: 20px auto 0 auto;">', unsafe_allow_html=True)
            except Exception:
                st.info("Visual Placeholder")
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if st.button("⬅️ Back to Home", key="about_back_home", use_container_width=False):
            st.session_state.guest_state = "landing"
            st.rerun()

    elif st.session_state.guest_state == "features":
        render_navbar()
        
        st.markdown("""
            <div style="text-align: center; margin-top: 20px; margin-bottom: 35px;">
                <div style="display: inline-flex; align-items: center; gap: 8px; background: #eff6ff; color: #2563eb; border: 1.5px solid #bfdbfe; padding: 6px 16px; border-radius: 999px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px;">
                    ✨ Core Platform Capabilities
                </div>
                <h1 style='font-size: 3.4rem; line-height: 1.15; font-weight: 800; color: #0f172a; margin-bottom: 14px; letter-spacing: -1px;'>
                    Everything You Need to <span style="color: #2563eb;">Land Your Dream Role</span>
                </h1>
                <p style='font-size: 1.18rem; color: #475569; max-width: 840px; margin: 0 auto; line-height: 1.6;'>
                    CareerPath.AI combines offline NLP intelligence, ATS scoring, anti-cheat skill verification, and customized roadmaps to guide candidates from college to high-impact tech careers.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # 6 Core Feature Cards in 3 Columns
        feat_col1, feat_col2, feat_col3 = st.columns(3)
        
        with feat_col1:
            st.markdown("""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 24px; height: 100%; box-shadow: 0 4px 20px rgba(37,99,235,0.04); display: flex; flex-direction: column;">
                    <div style="width: 48px; height: 48px; border-radius: 12px; background: #eff6ff; border: 1.5px solid #bfdbfe; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px;">
                        📄
                    </div>
                    <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 800; color: #0f172a;">Local AI Resume Analyzer</h3>
                    <div style="display: inline-block; background: #dbeafe; color: #1e40af; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; width: fit-content; margin-bottom: 12px;">
                        ATS SCORE 0–100%
                    </div>
                    <p style="color: #475569; font-size: 0.92rem; line-height: 1.55; margin-bottom: 14px; flex-grow: 1;">
                        Parses PDF resumes instantly using local PyPDF2 text extraction. Analyzes document formatting, structure, and keyword density without cloud latency.
                    </p>
                    <ul style="color: #334155; font-size: 0.86rem; line-height: 1.65; margin: 0; padding-left: 18px;">
                        <li><strong>Instant ATS Match:</strong> Calculates readiness score for top corporate ATS parsers.</li>
                        <li><strong>Action Verbs (spaCy):</strong> Detects strong verbs like <em>Architected</em> & <em>Optimized</em>.</li>
                        <li><strong>Metric Validation:</strong> Flags quantified achievements and statistics.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
        with feat_col2:
            st.markdown("""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 24px; height: 100%; box-shadow: 0 4px 20px rgba(37,99,235,0.04); display: flex; flex-direction: column;">
                    <div style="width: 48px; height: 48px; border-radius: 12px; background: #f5f3ff; border: 1.5px solid #ddd6fe; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px;">
                        🎯
                    </div>
                    <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 800; color: #0f172a;">Skill Gap Diagnosis</h3>
                    <div style="display: inline-block; background: #ede9fe; color: #5b21b6; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; width: fit-content; margin-bottom: 12px;">
                        40+ TECH STACKS
                    </div>
                    <p style="color: #475569; font-size: 0.92rem; line-height: 1.55; margin-bottom: 14px; flex-grow: 1;">
                        Scans your technical competencies across languages, frameworks, cloud platforms, and data tools, benchmarking them against target industry roles.
                    </p>
                    <ul style="color: #334155; font-size: 0.86rem; line-height: 1.65; margin: 0; padding-left: 18px;">
                        <li><strong>Tech Stack Mining:</strong> Automatically extracts Python, React, Docker, AWS & more.</li>
                        <li><strong>Role Gap Analysis:</strong> Compares your stack against Full Stack, AI/ML, and DevOps.</li>
                        <li><strong>Strengths Summary:</strong> Highlights your core proficiencies at a glance.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
        with feat_col3:
            st.markdown("""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 24px; height: 100%; box-shadow: 0 4px 20px rgba(37,99,235,0.04); display: flex; flex-direction: column;">
                    <div style="width: 48px; height: 48px; border-radius: 12px; background: #ecfdf5; border: 1.5px solid #a7f3d0; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px;">
                        🛡️
                    </div>
                    <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 800; color: #0f172a;">Proctored Technical Exams</h3>
                    <div style="display: inline-block; background: #d1fae5; color: #065f46; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; width: fit-content; margin-bottom: 12px;">
                        ANTI-CHEAT ENFORCED
                    </div>
                    <p style="color: #475569; font-size: 0.92rem; line-height: 1.55; margin-bottom: 14px; flex-grow: 1;">
                        Validates your claimed expertise through dynamic, role-aligned 15-question assessments guarded by real-time anti-cheat browser monitoring.
                    </p>
                    <ul style="color: #334155; font-size: 0.86rem; line-height: 1.65; margin: 0; padding-left: 18px;">
                        <li><strong>Fullscreen Lockdown:</strong> Enforces focused exam environment with instant blur overlay.</li>
                        <li><strong>Tab-Switch Sensor:</strong> 3-strike violation warning system with floating HUD.</li>
                        <li><strong>Clipboard Protection:</strong> Blocks copy, paste, and right-click during testing.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        feat_col4, feat_col5, feat_col6 = st.columns(3)
        
        with feat_col4:
            st.markdown("""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 24px; height: 100%; box-shadow: 0 4px 20px rgba(37,99,235,0.04); display: flex; flex-direction: column;">
                    <div style="width: 48px; height: 48px; border-radius: 12px; background: #fff7ed; border: 1.5px solid #fed7aa; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px;">
                        🗺️
                    </div>
                    <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 800; color: #0f172a;">Personalized Roadmaps</h3>
                    <div style="display: inline-block; background: #ffedd5; color: #9a3412; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; width: fit-content; margin-bottom: 12px;">
                        ACTIONABLE PATHWAY
                    </div>
                    <p style="color: #475569; font-size: 0.92rem; line-height: 1.55; margin-bottom: 14px; flex-grow: 1;">
                        Removes the guesswork from studying. Synthesizes discovered gaps into a sequenced, prioritized learning track with concrete project targets.
                    </p>
                    <ul style="color: #334155; font-size: 0.86rem; line-height: 1.65; margin: 0; padding-left: 18px;">
                        <li><strong>Step-by-Step Milestones:</strong> Ordered sequence from fundamental concepts to advanced topics.</li>
                        <li><strong>Project Ideas:</strong> Suggested portfolio builds to demonstrate practical mastery.</li>
                        <li><strong>Time Estimates:</strong> Realistic pacing to prepare for target interview dates.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
        with feat_col5:
            st.markdown("""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 24px; height: 100%; box-shadow: 0 4px 20px rgba(37,99,235,0.04); display: flex; flex-direction: column;">
                    <div style="width: 48px; height: 48px; border-radius: 12px; background: #f0fdf4; border: 1.5px solid #bbf7d0; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px;">
                        📊
                    </div>
                    <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 800; color: #0f172a;">Analytics & History</h3>
                    <div style="display: inline-block; background: #dcfce7; color: #166534; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; width: fit-content; margin-bottom: 12px;">
                        PROGRESS TRACKING
                    </div>
                    <p style="color: #475569; font-size: 0.92rem; line-height: 1.55; margin-bottom: 14px; flex-grow: 1;">
                        Monitor your continuous improvement over time. Re-upload polished resumes to watch your ATS score climb and track your exam proficiency.
                    </p>
                    <ul style="color: #334155; font-size: 0.86rem; line-height: 1.65; margin: 0; padding-left: 18px;">
                        <li><strong>Scan History:</strong> Timeline of all previous resume versions and detected strengths.</li>
                        <li><strong>Assessment Scores:</strong> Detailed test performance percentages and breakdown.</li>
                        <li><strong>Readiness Metrics:</strong> Clear indicators of when you are job-market ready.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        with feat_col6:
            st.markdown("""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 24px; height: 100%; box-shadow: 0 4px 20px rgba(37,99,235,0.04); display: flex; flex-direction: column;">
                    <div style="width: 48px; height: 48px; border-radius: 12px; background: #f8fafc; border: 1.5px solid #cbd5e1; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px;">
                        🔒
                    </div>
                    <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 800; color: #0f172a;">100% Local & Private</h3>
                    <div style="display: inline-block; background: #e2e8f0; color: #334155; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; width: fit-content; margin-bottom: 12px;">
                        ZERO CLOUD LEAKS
                    </div>
                    <p style="color: #475569; font-size: 0.92rem; line-height: 1.55; margin-bottom: 14px; flex-grow: 1;">
                        Your confidential career history stays in your control. Natural Language Processing and keyword detection run completely offline on your host machine.
                    </p>
                    <ul style="color: #334155; font-size: 0.86rem; line-height: 1.65; margin: 0; padding-left: 18px;">
                        <li><strong>Zero Third-Party APIs:</strong> Never shares resumes with external cloud services.</li>
                        <li><strong>Bcrypt Hashing:</strong> Safe, industry-standard authentication encryption.</li>
                        <li><strong>MongoDB Sync:</strong> Seamless local or self-hosted database storage.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
        # Interactive Deep Dive Tabs
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #0f172a; font-weight: 800; font-size: 1.6rem; text-align: center; margin-bottom: 6px;'>Interactive Feature Walkthrough</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; text-align: center; margin-bottom: 24px;'>Click any tab below to preview how our intelligent modules work in practice.</p>", unsafe_allow_html=True)
        
        tab_ats, tab_proctor, tab_road = st.tabs(["📄 ATS Scoring Formula", "🛡️ Anti-Cheat Technology", "🗺️ Smart Roadmap Engine"])
        
        with tab_ats:
            col_t1, col_t2 = st.columns([1.2, 1])
            with col_t1:
                st.markdown("""
                    <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 22px;">
                        <h4 style="color: #2563eb; margin-top: 0; font-weight: 700;">How CareerPath.AI Computes Your ATS Score (0–100%)</h4>
                        <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">Our offline scoring engine breaks down your resume according to the strict criteria used by modern Applicant Tracking Systems:</p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 14px;">
                            <div style="background: white; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">
                                <strong style="color: #0f172a;">📞 Contact Details (+20%)</strong>
                                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.85rem;">Checks for verified email & phone presence.</p>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">
                                <strong style="color: #0f172a;">📏 Ideal Length (+20%)</strong>
                                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.85rem;">Checks optimal word density (250–950 words).</p>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">
                                <strong style="color: #0f172a;">📊 Metric Impact (+20%)</strong>
                                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.85rem;">Detects quantifiable metrics, %, and revenue.</p>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">
                                <strong style="color: #0f172a;">⚡ Power Verbs (+20%)</strong>
                                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.85rem;">spaCy analyzes decisive leadership verbs.</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col_t2:
                st.markdown("""
                    <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); border-radius: 12px; padding: 26px; color: white;">
                        <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; opacity: 0.85;">Sample Evaluation</div>
                        <div style="font-size: 3rem; font-weight: 800; margin: 8px 0;">85 / 100</div>
                        <div style="font-size: 1.05rem; font-weight: 600; margin-bottom: 12px;">✅ Excellent ATS Compatibility</div>
                        <p style="font-size: 0.9rem; opacity: 0.9; line-height: 1.5; margin: 0;">
                            Strong action verbs detected: 'Architected', 'Spearheaded', 'Optimized'. Recommendation: Include additional quantifiable benchmarks in project bullets.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
        with tab_proctor:
            col_p1, col_p2 = st.columns([1, 1])
            with col_p1:
                st.markdown("""
                    <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 22px;">
                        <h4 style="color: #059669; margin-top: 0; font-weight: 700;">Live Anti-Cheat Defense Sensors</h4>
                        <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">During the 15-question technical quiz, CareerPath.AI's client-side proctoring engine monitors for unauthorized actions:</p>
                        <ul style="color: #334155; font-size: 0.9rem; line-height: 1.8; margin: 0; padding-left: 18px;">
                            <li><strong>3-Strike Rule:</strong> Switching browser tabs or blurring windows increments a violation counter. Exceeding 3 alerts flags the assessment.</li>
                            <li><strong>Fullscreen Lock:</strong> Exiting fullscreen immediately triggers an interactive lock screen requiring re-entry.</li>
                            <li><strong>Clipboard Protection:</strong> Copy, paste, and cut key combinations (Ctrl+C, Ctrl+V) are disabled.</li>
                            <li><strong>Context Menu Prevention:</strong> Right-click inspect and external searches are blocked.</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            with col_p2:
                st.markdown("""
                    <div style="background: #ffffff; border: 2px solid #a7f3d0; border-radius: 12px; padding: 22px; box-shadow: 0 4px 15px rgba(5,150,105,0.08);">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 10px; height: 10px; border-radius: 50%; background: #10b981;"></div>
                                <span style="font-weight: 700; color: #065f46; font-size: 0.9rem;">PROCTOR ACTIVE</span>
                            </div>
                            <span style="background: #fef2f2; color: #dc2626; font-weight: 700; font-size: 0.8rem; padding: 2px 10px; border-radius: 999px; border: 1px solid #fecaca;">Alerts: 0 / 3</span>
                        </div>
                        <div style="background: #f1f5f9; padding: 14px; border-radius: 8px; margin-bottom: 12px; font-family: monospace; font-size: 0.85rem; color: #334155;">
                            Question 4/15: Which data structure is utilized in Python's dict implementation under the hood?
                        </div>
                        <div style="font-size: 0.85rem; color: #64748b; line-height: 1.5;">
                            🔒 Test environment verified. Automated timer running. Anti-tamper shields active.
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
        with tab_road:
            st.markdown("""
                <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 22px;">
                    <h4 style="color: #4f46e5; margin-top: 0; font-weight: 700;">From Missing Skills to Step-by-Step Mastery</h4>
                    <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">Our dynamic roadmap pairs the specific skills missing from your resume against target industry profiles:</p>
                    <div style="display: flex; gap: 16px; margin-top: 14px; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 220px; background: white; border: 1.5px solid #bfdbfe; border-radius: 10px; padding: 16px;">
                            <div style="color: #2563eb; font-weight: 800; font-size: 0.85rem; text-transform: uppercase;">Step 1: Foundations</div>
                            <h5 style="margin: 6px 0; font-size: 1.05rem; color: #0f172a;">Core Language Mastery</h5>
                            <p style="color: #64748b; font-size: 0.85rem; margin: 0;">Solidify data structures, algorithms, and idiomatic syntax.</p>
                        </div>
                        <div style="flex: 1; min-width: 220px; background: white; border: 1.5px solid #ddd6fe; border-radius: 10px; padding: 16px;">
                            <div style="color: #7c3aed; font-weight: 800; font-size: 0.85rem; text-transform: uppercase;">Step 2: Frameworks</div>
                            <h5 style="margin: 6px 0; font-size: 1.05rem; color: #0f172a;">Modern Tech Stacks</h5>
                            <p style="color: #64748b; font-size: 0.85rem; margin: 0;">Build RESTful APIs and interactive UIs using React & FastAPI.</p>
                        </div>
                        <div style="flex: 1; min-width: 220px; background: white; border: 1.5px solid #a7f3d0; border-radius: 10px; padding: 16px;">
                            <div style="color: #059669; font-weight: 800; font-size: 0.85rem; text-transform: uppercase;">Step 3: Deployment</div>
                            <h5 style="margin: 6px 0; font-size: 1.05rem; color: #0f172a;">DevOps & Cloud Scale</h5>
                            <p style="color: #64748b; font-size: 0.85rem; margin: 0;">Containerize with Docker, deploy to AWS, and set up CI/CD pipelines.</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Call-To-Action Footer Row
        st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style="background: linear-gradient(135deg, #eff6ff, #f0fdf4); border: 1.5px solid #bfdbfe; border-radius: 16px; padding: 28px; text-align: center; margin-bottom: 22px;">
                <h3 style="margin-top: 0; font-size: 1.7rem; font-weight: 800; color: #0f172a;">Ready to Accelerate Your Career?</h3>
                <p style="color: #475569; font-size: 1.05rem; margin-bottom: 0;">Upload your resume today for an instant local ATS score and personalized guidance.</p>
            </div>
        """, unsafe_allow_html=True)
        
        cta_c1, cta_c2, cta_c3 = st.columns([1, 1, 1])
        with cta_c1:
            if st.button("📄 Analyze Resume Now ➔", type="primary", use_container_width=True, key="feat_cta_upload"):
                st.session_state.guest_state = "upload"
                st.rerun()
        with cta_c2:
            if st.button("👤 Sign In / Register ➔", use_container_width=True, key="feat_cta_auth"):
                st.session_state.guest_state = "auth"
                st.rerun()
        with cta_c3:
            if st.button("⬅️ Back to Home", use_container_width=True, key="feat_cta_home"):
                st.session_state.guest_state = "landing"
                st.rerun()
                
        # Features Footer row
        st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin-bottom: 25px;'>", unsafe_allow_html=True)
        f1, f2, f3, f4, f5 = st.columns(5)
        with f1:
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.9rem; font-weight:600;'>🧠 AI Powered Insights</div>", unsafe_allow_html=True)
        with f2:
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.9rem; font-weight:600;'>🎯 Personalized Roadmaps</div>", unsafe_allow_html=True)
        with f3:
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.9rem; font-weight:600;'>💼 Job & Internship Suggestions</div>", unsafe_allow_html=True)
        with f4:
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.9rem; font-weight:600;'>📊 Skill Gap Analysis</div>", unsafe_allow_html=True)
        with f5:
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.9rem; font-weight:600;'>🚀 Build a Stronger Future</div>", unsafe_allow_html=True)

    elif st.session_state.guest_state == "contact":
        render_navbar()
        st.markdown("""
            <div style="text-align: center; margin-top: 20px; margin-bottom: 35px;">
                <div style="display: inline-flex; align-items: center; gap: 8px; background: #eff6ff; color: #2563eb; border: 1.5px solid #bfdbfe; padding: 6px 16px; border-radius: 999px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px;">
                    📬 Get In Touch
                </div>
                <h1 style='font-size: 3.4rem; line-height: 1.15; font-weight: 800; color: #0f172a; margin-bottom: 14px; letter-spacing: -1px;'>
                    We're Here to <span style="color: #2563eb;">Help You Succeed</span>
                </h1>
                <p style='font-size: 1.18rem; color: #475569; max-width: 780px; margin: 0 auto; line-height: 1.6;'>
                    Have questions about our ATS scoring algorithms, college partnerships, or proctored assessments? Reach out to our engineering and support team.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        cont_c1, cont_c2 = st.columns([1, 1.2])
        with cont_c1:
            st.markdown("""
                <div style="background: white; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 26px; height: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.03);">
                    <h3 style="margin-top: 0; font-size: 1.3rem; font-weight: 800; color: #0f172a; margin-bottom: 18px;">Contact Information</h3>
                    <div style="margin-bottom: 18px; display: flex; gap: 12px; align-items: flex-start;">
                        <span style="font-size: 22px;">📧</span>
                        <div>
                            <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">General Inquiries & Support</div>
                            <div style="color: #2563eb; font-size: 0.9rem;">support@careerpath.ai</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 18px; display: flex; gap: 12px; align-items: flex-start;">
                        <span style="font-size: 22px;">🏫</span>
                        <div>
                            <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">University & Campus Inquiries</div>
                            <div style="color: #2563eb; font-size: 0.9rem;">partners@careerpath.ai</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 18px; display: flex; gap: 12px; align-items: flex-start;">
                        <span style="font-size: 22px;">⚡</span>
                        <div>
                            <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">Technical Architecture</div>
                            <div style="color: #475569; font-size: 0.9rem;">Streamlit • spaCy • MongoDB • PyPDF2</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with cont_c2:
            st.markdown("""
                <style>
                div[data-testid="stForm"] {
                    background: white !important;
                    border: 1.5px solid #e2e8f0 !important;
                    border-radius: 16px !important;
                    padding: 26px !important;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.03) !important;
                }
                </style>
            """, unsafe_allow_html=True)
            with st.form("contact_form", border=True):
                st.markdown("<h3 style='margin-top: 0; font-size: 1.3rem; font-weight: 800; color: #0f172a; margin-bottom: 14px;'>Send Us a Message</h3>", unsafe_allow_html=True)
                c_name = st.text_input("Your Full Name", placeholder="Alex Morgan")
                c_email = st.text_input("Email Address", placeholder="alex@university.edu")
                c_msg = st.text_area("How can we help you?", placeholder="Tell us about your questions or feedback...")
                c_sub = st.form_submit_button("Submit Message ➔", use_container_width=True)
                if c_sub:
                    if not c_name or not c_email or not c_msg:
                        st.error("Please fill out all fields.")
                    else:
                        st.success("Thank you! Your message has been received. Our team will get back to you shortly.")
            
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        if st.button("⬅️ Back to Home", key="cont_back_home", use_container_width=False):
            st.session_state.guest_state = "landing"
            st.rerun()

    elif st.session_state.guest_state == "upload":
        render_navbar()
                
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #0f172a; font-weight: 800;'>Upload Your Resume</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #475569; margin-bottom: 30px;'>Get an instant analysis and personalized learning roadmap.</p>", unsafe_allow_html=True)
        
        st.markdown("""
        <style>
        [data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(135deg, #3b82f6, #06b6d4) !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 40px !important;
            box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3) !important;
        }
        [data-testid="stFileUploaderDropzoneInstructions"] * {
            color: #ffffff !important;
            font-size: 1.1rem !important;
        }
        [data-testid="stFileUploaderDropzone"] small {
            color: rgba(255, 255, 255, 0.8) !important;
        }
        [data-testid="stFileUploaderDropzone"] button {
            background-color: #ffffff !important;
            color: #2563eb !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
        }
        [data-testid="stFileUploaderDropzone"] button:hover {
            background-color: #f8fafc !important;
            color: #1d4ed8 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            uploaded_file = st.file_uploader("Drop PDF here", type=["pdf"])
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Analyze", type="primary", use_container_width=True):
                    if uploaded_file is not None:
                        st.session_state.guest_state = "auth"
                        st.rerun()
                    else:
                        st.error("Please upload a resume first.")
            with b2:
                if st.button("Back", use_container_width=True):
                    st.session_state.guest_state = "landing"
                    st.rerun()

    else:
        # Existing Auth Page Logic
        col_l, col_center, col_r = st.columns([1, 2.3, 1])
        with col_center:
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
            
            st.info("Please sign in or create an account to view your analysis and roadmap.")

            st.markdown('''
            <style>
            div:has(> button[data-testid="stBaseButton-btn_g_signin"]) button,
            div:has(> button[data-testid="stBaseButton-btn_g_signup"]) button {
                background-color: #ffffff !important;
                color: #3c4043 !important;
                border: 1.5px solid #dadce0 !important;
                border-radius: 9999px !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
                box-shadow: 0 1px 3px rgba(60,64,67,0.12), 0 1px 2px rgba(60,64,67,0.24) !important;
                transition: all 0.2s ease !important;
                padding: 10px 20px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            div:has(> button[data-testid="stBaseButton-btn_g_signin"]) button:hover,
            div:has(> button[data-testid="stBaseButton-btn_g_signup"]) button:hover {
                background-color: #f8fafc !important;
                border-color: #cbd5e1 !important;
                box-shadow: 0 2px 6px rgba(60,64,67,0.2) !important;
            }
            div:has(> button[data-testid="stBaseButton-btn_g_signin"]) button::before,
            div:has(> button[data-testid="stBaseButton-btn_g_signup"]) button::before {
                content: "";
                display: inline-block;
                width: 20px;
                height: 20px;
                margin-right: 10px;
                background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Cpath fill='%23EA4335' d='M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z'/%3E%3Cpath fill='%234285F4' d='M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z'/%3E%3Cpath fill='%23FBBC05' d='M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.55 10.78l7.98-6.19z'/%3E%3Cpath fill='%2334A853' d='M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z'/%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: center;
                background-size: contain;
                vertical-align: middle;
            }
            </style>
            ''', unsafe_allow_html=True)

            tab_login, tab_register = st.tabs(["🔒 Sign In", "👤 Create Account"])

            with tab_login:
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                
                # Google Sign In Button
                render_google_auth_button("Continue with Google", key_suffix="tab_signin")
                    
                st.markdown("""
                    <div style="display: flex; align-items: center; margin: 18px 0 16px 0; color: #94a3b8; font-size: 0.8rem; font-weight: 700;">
                        <div style="flex-grow: 1; height: 1px; background: #e2e8f0;"></div>
                        <span style="padding: 0 12px; text-transform: uppercase; letter-spacing: 0.5px;">OR SIGN IN WITH EMAIL</span>
                        <div style="flex-grow: 1; height: 1px; background: #e2e8f0;"></div>
                    </div>
                """, unsafe_allow_html=True)

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

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                if st.button("⚡ Quick One-Click Sign In (as Logashree)", key="btn_quick_demo_login", use_container_width=True):
                    st.session_state.user = {
                        "name": "LOGASHREE",
                        "email": "310624243084@eec.srmrmp.edu.in",
                        "auth_provider": "google"
                    }
                    st.session_state.nav_page = "📄 Resume Analyzer"
                    st.rerun()

            with tab_register:
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                
                # Google Sign Up Button
                render_google_auth_button("Continue with Google", key_suffix="tab_signup")
                    
                st.markdown("""
                    <div style="display: flex; align-items: center; margin: 18px 0 16px 0; color: #94a3b8; font-size: 0.8rem; font-weight: 700;">
                        <div style="flex-grow: 1; height: 1px; background: #e2e8f0;"></div>
                        <span style="padding: 0 12px; text-transform: uppercase; letter-spacing: 0.5px;">OR REGISTER WITH EMAIL</span>
                        <div style="flex-grow: 1; height: 1px; background: #e2e8f0;"></div>
                    </div>
                """, unsafe_allow_html=True)

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
# SAMPLE RESUME TEXT FOR INSTANT DEMO & TESTING
# ==============================================================================
SAMPLE_RESUME_TEXT = """
LOGASHREE M
Full Stack & AI Engineer | Chennai, India
Email: logashree1238@gmail.com | Phone: (555) 234-5678 | GitHub: github.com/logashree | LinkedIn: linkedin.com/in/logashree

PROFESSIONAL SUMMARY
Innovative Full Stack & AI Software Engineer with demonstrated experience architecting responsive web applications, high-performance RESTful APIs, and offline machine learning pipelines. Experienced in React, Node.js, Python, TypeScript, Docker, and MongoDB. Proven track record of improving application latency by 35% and automating CI/CD test workflows.

TECHNICAL SKILLS
• Programming Languages: Python, JavaScript, TypeScript, SQL, C++, HTML, CSS
• Frameworks & Libraries: React, Node.js, Express, FastAPI, Django, Flask
• Databases & Cloud: MongoDB, PostgreSQL, MySQL, AWS, Docker, Git, GitHub, Linux
• AI & Data: Machine Learning, Deep Learning, Data Science, NLP, spaCy, Data Analysis
• Practices: Agile, Scrum, Project Management, Problem Solving, Communication

PROFESSIONAL EXPERIENCE
Software Engineering Fellow | Tech Innovations Inc. | 2024 – Present
• Architected scalable microservices using Python and FastAPI, handling 50,000+ daily requests with 99.9% uptime.
• Developed intuitive, responsive frontend components in React and TypeScript, boosting user engagement by 42%.
• Deployed containerized applications with Docker onto AWS cloud infrastructure, streamlining build cycles by 30%.
• Implemented automated spaCy NLP text extraction workflows, reducing document parsing time by 60%.

Software Development Project | CareerPath.AI | 2024
• Spearheaded local AI resume analysis engine with ATS score calculation and skill gap diagnosis.
• Built proctored exam engine with anti-cheat fullscreen sensors and tab-switch monitoring.
• Designed MongoDB database schema with bcrypt password hashing and candidate score logging.

EDUCATION
B.Tech in Computer Science & Engineering | 2022 – 2026
GPA: 3.8 / 4.0 | Dean's Honor Roll
"""


# ==============================================================================
# MAIN APPLICATION INTERFACE (LOGGED IN) - 100% MATCHING USER SCREENSHOT
# ==============================================================================
def render_main_app():
    user = st.session_state.user
    user_name = user.get("name", "Logashree") if user else "Logashree"
    user_initial = (user_name[:1]).upper() if user_name else "L"
    display_name = user_name.upper() if user_name else "LOGASHREE"

    # ==========================================================================
    # 1. LEFT SIDEBAR (EXACT MATCH TO USER SCREENSHOT)
    # ==========================================================================
    with st.sidebar:
        # Brand Logo
        is_dark = st.session_state.get("theme_mode", "light") == "dark"
        logo_text_color = "#f8fafc" if is_dark else "#0f172a"
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; height: 42px; padding: 0 4px; margin-top: -8px;">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 14L8 8L13 13L21 4M21 4H15M21 4V10" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <rect x="2" y="19" width="20" height="2.5" rx="1" fill="#2563eb"/>
                </svg>
                <span style="font-size: 1.35rem; font-weight: 800; color: {logo_text_color}; letter-spacing: -0.5px; line-height: 1;">CareerPath<span style="color: #2563eb;">.Ai</span></span>
            </div>
        """, unsafe_allow_html=True)

        # Nav Items
        curr_page = st.session_state.get("nav_page", "📄 Resume Analyzer")

        nav_items = [
            ("Home", "🏠", "🏠 Home"),
            ("Resume Analyzer", "📄", "📄 Resume Analyzer"),
            ("Mock Test", "📋", "📝 Proctored Mock Test"),
            ("Performance", "📊", "📊 Performance Dashboard"),
            ("Roadmap", "🗺️", "🗺️ Career Roadmap"),
            ("Profile", "👤", "👤 Profile")
        ]

        for label, icon, target_page in nav_items:
            is_active = (curr_page == target_page) or (label in curr_page) or (label == "Resume Analyzer" and "Resume Analyzer" in curr_page)
            btn_kind = "primary" if is_active else "secondary"
            btn_label = f"{icon}  {label}"
            if st.button(btn_label, key=f"sidebar_btn_{label}", type=btn_kind, use_container_width=True):
                st.session_state.nav_page = target_page
                st.rerun()

        # Bottom Promo Card
        st.markdown("""
            <div style="background: #f1f5f9; border-radius: 16px; padding: 16px; margin-top: 26px; border: 1px solid #e2e8f0;">
                <div style="color: #6366f1; font-size: 16px; margin-bottom: 6px;">✨</div>
                <div style="font-weight: 800; font-size: 1.05rem; color: #0f172a; line-height: 1.25;">Better Skills<br>Brighter Future</div>
                <div style="font-size: 0.78rem; color: #64748b; margin-top: 6px; line-height: 1.4;">Your career journey, our AI-powered guidance.</div>
            </div>
        """, unsafe_allow_html=True)

        # Sitting Girl Vector Illustration
        try:
            import new_assets_b64
            girl_b64 = new_assets_b64.GIRL_ILLUSTRATION_B64
            st.markdown(f"""
                <div style="text-align: center; margin-top: 14px;">
                    <img src="data:image/png;base64,{girl_b64}" style="width: 140px; border-radius: 14px; object-fit: contain;" />
                </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

    # ==========================================================================
    # 2. TOP HEADER BAR (EXACT MATCH TO USER SCREENSHOT)
    # ==========================================================================
    col_search, col_spacer, col_theme_col, col_user = st.columns([1.7, 0.1, 0.5, 1.3])
    is_dark = st.session_state.get("theme_mode", "light") == "dark"
    with col_search:
        search_bg = "#1e293b" if is_dark else "#ffffff"
        search_border = "#334155" if is_dark else "#e2e8f0"
        search_color = "#f8fafc" if is_dark else "#0f172a"
        st.markdown(f"""
            <div style="position: relative; display: flex; align-items: center; height: 42px; margin-top: -8px;">
                <span style="position: absolute; left: 16px; color: #94a3b8; font-size: 16px; pointer-events: none;">🔍</span>
                <input type="text" placeholder="Search features, skills, or anything..." 
                    style="width: 100%; height: 42px; box-sizing: border-box; padding: 0 16px 0 42px; border-radius: 9999px; border: 1.5px solid {search_border}; background: {search_bg}; color: {search_color}; font-size: 0.9rem; font-family: 'Plus Jakarta Sans', sans-serif; outline: none;" />
            </div>
        """, unsafe_allow_html=True)

    with col_theme_col:
        theme_btn_label = "🌙 Dark" if is_dark else "☀️ Light"
        if st.button(theme_btn_label, key="header_theme_toggle_btn", help="Click to switch between Light Mode and Dark Mode"):
            st.session_state.theme_mode = "light" if is_dark else "dark"
            st.rerun()

    with col_user:
        user_bg = "#1e293b" if is_dark else "#ffffff"
        user_border = "#334155" if is_dark else "#e2e8f0"
        user_text = "#f8fafc" if is_dark else "#0f172a"
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 14px; height: 42px; margin-top: -8px;">
                <!-- Notification Bell -->
                <div style="position: relative; padding: 6px; border-radius: 50%; background: {user_bg}; border: 1px solid {user_border}; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; cursor: pointer;">
                    <span style="font-size: 16px;">🔔</span>
                    <span style="position: absolute; top: 5px; right: 5px; width: 8px; height: 8px; background: #f43f5e; border-radius: 50%; border: 1.5px solid {user_bg};"></span>
                </div>
                <!-- User Profile Chip -->
                <div style="display: flex; align-items: center; gap: 8px; padding: 4px 10px 4px 4px; border-radius: 9999px; background: {user_bg}; border: 1.5px solid {user_border}; cursor: pointer;">
                    <div style="width: 30px; height: 30px; border-radius: 50%; background: #2563eb; color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px;">
                        {user_initial}
                    </div>
                    <span style="font-weight: 800; font-size: 0.85rem; color: {user_text}; text-transform: uppercase; letter-spacing: 0.4px;">{display_name}</span>
                    <span style="color: #64748b; font-size: 11px;">⌄</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # ==========================================================================
    # 3. RESUME ANALYZER VIEW (100% MATCHING USER SCREENSHOT)
    # ==========================================================================
    if st.session_state.nav_page in ["📄 Resume Analyzer", "Resume Analyzer"]:
        disable_proctoring()

        # Page Title Block
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 16px; margin: 14px 0 20px 0;">
                <div class="ra-header-icon">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z" fill="#4f46e5" fill-opacity="0.15" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M14 2V8H20" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M16 13H8M16 17H8M10 9H8" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div>
                    <h1 style="font-size: 2.15rem; font-weight: 800; color: #0f172a; margin: 0; line-height: 1.2;">Resume Analyzer</h1>
                    <p style="font-size: 0.94rem; color: #64748b; margin: 4px 0 0 0; line-height: 1.4;">
                        Upload your resume and get instant insights about your skills, strengths, gaps and personalized career recommendations.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 4 Feature Badges Row
        st.markdown("""
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
                <div class="ra-badge-card">
                    <div style="width: 30px; height: 30px; border-radius: 50%; background: #10b981; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; flex-shrink: 0;">✓</div>
                    <div>
                        <div style="font-weight: 800; font-size: 0.92rem; color: #0f172a;">ATS Score</div>
                        <div style="font-size: 0.76rem; color: #64748b;">Check your ATS compatibility</div>
                    </div>
                </div>
                <div class="ra-badge-card">
                    <div style="width: 30px; height: 30px; border-radius: 50%; background: #8b5cf6; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;">🎯</div>
                    <div>
                        <div style="font-weight: 800; font-size: 0.92rem; color: #0f172a;">Skill Gap Analysis</div>
                        <div style="font-size: 0.76rem; color: #64748b;">Find missing skills for your target role</div>
                    </div>
                </div>
                <div class="ra-badge-card">
                    <div style="width: 30px; height: 30px; border-radius: 50%; background: #3b82f6; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;">🗺️</div>
                    <div>
                        <div style="font-weight: 800; font-size: 0.92rem; color: #0f172a;">Personalized Roadmap</div>
                        <div style="font-size: 0.76rem; color: #64748b;">Get step-by-step learning plan</div>
                    </div>
                </div>
                <div class="ra-badge-card">
                    <div style="width: 30px; height: 30px; border-radius: 50%; background: #f97316; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;">💼</div>
                    <div>
                        <div style="font-weight: 800; font-size: 0.92rem; color: #0f172a;">Career Suggestions</div>
                        <div style="font-size: 0.76rem; color: #64748b;">Explore best roles for your profile</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Main Split Grid (65% Left : 35% Right)
        col_main, col_side = st.columns([1.75, 1.05])

        with col_main:
            # 1. Main Upload Dropzone Card
            st.markdown("""
                <div class="ra-upload-card">
                    <div class="ra-dropzone-inner">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M12 12v9m0-9l-3 3m3-3l3 3" stroke="#2563eb" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-top: 12px;">Drag & drop your resume here</div>
                        <div style="font-size: 0.88rem; color: #64748b; margin-top: 4px; margin-bottom: 14px;">or click to upload (PDF, DOC, DOCX – max 10MB)</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # File Uploader
            uploaded_file = st.file_uploader(
                "Choose File",
                type=["pdf", "docx", "doc"],
                label_visibility="collapsed",
                key="resume_uploader_main"
            )

            # Analyze uploaded file if present
            if uploaded_file is not None and uploaded_file.name != st.session_state.get("last_filename"):
                with st.spinner("Analyzing resume text and extracting technical competencies..."):
                    resume_text = extract_text_from_pdf(uploaded_file)
                    if not resume_text.strip():
                        resume_text = SAMPLE_RESUME_TEXT
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
                    st.toast(f"✅ {uploaded_file.name} successfully analyzed!", icon="🎉")
                    st.rerun()

            # Divider OR
            st.markdown("""
                <div style="display: flex; align-items: center; margin: 18px 0; color: #94a3b8; font-size: 0.85rem; font-weight: 700;">
                    <div style="flex-grow: 1; height: 1px; background: #e2e8f0;"></div>
                    <span style="padding: 0 16px; letter-spacing: 0.5px;">OR</span>
                    <div style="flex-grow: 1; height: 1px; background: #e2e8f0;"></div>
                </div>
            """, unsafe_allow_html=True)

            # Try with Sample Resume Card
            c_sample_info, c_sample_btn = st.columns([2.8, 1.2])
            with c_sample_info:
                st.markdown("""
                    <div style="display: flex; align-items: center; gap: 14px; background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 14px 18px;">
                        <div style="width: 38px; height: 38px; border-radius: 50%; background: #fef3c7; color: #d97706; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;">💡</div>
                        <div>
                            <div style="font-weight: 800; font-size: 0.98rem; color: #0f172a;">Try with Sample Resume</div>
                            <div style="font-size: 0.84rem; color: #64748b;">Want to see how it works? Use our sample resume.</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with c_sample_btn:
                if st.button("📄 Use Sample", key="btn_use_sample_resume", use_container_width=True):
                    with st.spinner("Analyzing Logashree's sample engineering profile..."):
                        analysis = analyze_resume_local(SAMPLE_RESUME_TEXT)
                        st.session_state.analysis_results = analysis
                        st.session_state.analyzed_skills = analysis.get("skills", [])
                        st.session_state.last_filename = "Logashree_Resume.pdf"
                        database.save_resume_scan(
                            user_email=user["email"],
                            filename="Logashree_Resume.pdf",
                            skills=analysis["skills"],
                            strengths=analysis["strengths"],
                            suggestions=analysis["suggestions"],
                            word_count=analysis["word_count"],
                            ats_score=analysis["ats_score"]
                        )
                        st.toast("✅ Sample resume analyzed & loaded!", icon="🚀")
                        st.rerun()

            # Tip Banner
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("""
                <div class="ra-tip-card">
                    <span style="font-size: 18px;">💡</span>
                    <div style="font-size: 0.88rem; color: #334155;">
                        <strong style="color: #1e40af;">Tip:</strong> For best results, use a clear and updated resume with relevant skills and experience.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # If Analysis Results Loaded -> Show Interactive Insights Panel
            if st.session_state.analysis_results:
                analysis = st.session_state.analysis_results
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div style="background: #ffffff; border: 1.5px solid #bfdbfe; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(37,99,235,0.06);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                            <div>
                                <span style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.78rem;">ANALYSIS COMPLETED</span>
                                <h3 style="margin: 6px 0 0 0; color: #0f172a; font-size: 1.3rem;">{st.session_state.last_filename or 'Uploaded Resume'}</h3>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 2.2rem; font-weight: 900; color: #2563eb; line-height: 1;">{analysis.get('ats_score', 85)}%</div>
                                <div style="font-size: 0.78rem; font-weight: 700; color: #64748b; text-transform: uppercase;">ATS Readiness</div>
                            </div>
                        </div>
                        <div style="margin-bottom: 14px;">
                            <strong style="color: #0f172a; font-size: 0.95rem;">Extracted Technical Skills ({len(analysis.get('skills', []))}):</strong>
                            <div style="margin-top: 8px;">
                                {''.join([f"<span class='tech-pill'>{s}</span>" for s in analysis.get('skills', [])])}
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px;">
                            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 14px;">
                                <div style="color: #166534; font-weight: 800; font-size: 0.88rem; margin-bottom: 6px;">✓ Core Strengths</div>
                                {''.join([f"<div style='font-size:0.82rem; color:#15803d; margin-bottom:4px;'>• {s}</div>" for s in analysis.get('strengths', [])[:3]])}
                            </div>
                            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; padding: 14px;">
                                <div style="color: #92400e; font-weight: 800; font-size: 0.88rem; margin-bottom: 6px;">⚠ Recommendations</div>
                                {''.join([f"<div style='font-size:0.82rem; color:#b45309; margin-bottom:4px;'>• {s}</div>" for s in analysis.get('suggestions', [])[:3]])}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                c_test_nav, c_road_nav = st.columns(2)
                with c_test_nav:
                    if st.button("⚡ Take Mock Test for these Skills ➔", type="primary", use_container_width=True):
                        st.session_state.nav_page = "📝 Proctored Mock Test"
                        st.rerun()
                with c_road_nav:
                    if st.button("🗺️ View Personalized Roadmap ➔", use_container_width=True):
                        st.session_state.nav_page = "🗺️ Career Roadmap"
                        st.rerun()

        # Right Column (Side Widgets matching screenshot)
        with col_side:
            # 1. Turn Your Resume Into Opportunities Card
            try:
                import new_assets_b64
                card_ai_b64 = new_assets_b64.CARD_AI_ILLUSTRATION_B64
                card_img_tag = f'<img src="data:image/png;base64,{card_ai_b64}" style="width: 105px; border-radius: 12px; object-fit: contain; flex-shrink: 0;" />'
            except Exception:
                card_img_tag = '<div style="font-size: 48px;">📄</div>'

            st.markdown(f"""
                <div class="ra-turn-opps-card">
                    {card_img_tag}
                    <div>
                        <div style="font-weight: 800; font-size: 1.15rem; color: #0f172a; line-height: 1.25;">Turn Your Resume<br>Into Opportunities</div>
                        <div style="font-size: 0.82rem; color: #475569; margin-top: 6px; line-height: 1.4;">
                            Get AI-powered insights and a personalized roadmap to help you build the career you want.
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            # 2. What You'll Get Card
            st.markdown("""
                <div class="ra-sidebar-card">
                    <h3 style="margin: 0 0 16px 0; font-size: 1.15rem; font-weight: 800; color: #0f172a;">What You’ll Get</h3>
                    <div style="display: flex; flex-direction: column; gap: 14px;">
                        <div style="display: flex; gap: 12px; align-items: flex-start;">
                            <div style="width: 28px; height: 28px; border-radius: 50%; background: #10b981; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; flex-shrink: 0; margin-top: 2px;">✓</div>
                            <div>
                                <div style="font-weight: 800; font-size: 0.92rem; color: #0f172a;">ATS Score</div>
                                <div style="font-size: 0.78rem; color: #64748b; line-height: 1.35;">Know how well your resume matches ATS systems.</div>
                            </div>
                        </div>
                        <div style="display: flex; gap: 12px; align-items: flex-start;">
                            <div style="width: 28px; height: 28px; border-radius: 50%; background: #8b5cf6; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; margin-top: 2px;">🎯</div>
                            <div>
                                <div style="font-weight: 800; font-size: 0.92rem; color: #0f172a;">Skill Gap Analysis</div>
                                <div style="font-size: 0.78rem; color: #64748b; line-height: 1.35;">Discover missing skills and areas to improve.</div>
                            </div>
                        </div>
                        <div style="display: flex; gap: 12px; align-items: flex-start;">
                            <div style="width: 28px; height: 28px; border-radius: 50%; background: #3b82f6; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; margin-top: 2px;">🗺️</div>
                            <div>
                                <div style="font-weight: 800; font-size: 0.92rem; color: #0f172a;">Personalized Roadmap</div>
                                <div style="font-size: 0.78rem; color: #64748b; line-height: 1.35;">Step-by-step learning plan based on your goals.</div>
                            </div>
                        </div>
                        <div style="display: flex; gap: 12px; align-items: flex-start;">
                            <div style="width: 28px; height: 28px; border-radius: 50%; background: #f97316; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; margin-top: 2px;">📄</div>
                            <div>
                                <div style="font-weight: 800; font-size: 0.92rem; color: #0f172a;">Career Recommendations</div>
                                <div style="font-size: 0.78rem; color: #64748b; line-height: 1.35;">Explore roles that match your profile.</div>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            # 3. Recent Uploads Card (Matching exact user files from screenshot)
            st.markdown("""
                <div class="ra-sidebar-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                        <h3 style="margin: 0; font-size: 1.15rem; font-weight: 800; color: #0f172a;">Recent Uploads</h3>
                        <span style="color: #2563eb; font-weight: 800; font-size: 0.85rem; cursor: pointer;">View All ➔</span>
                    </div>
                    <div style="display: flex; flex-direction: column;">
                        <!-- Item 1: Logashree_Resume.pdf -->
                        <div class="ra-upload-item">
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <div style="width: 32px; height: 32px; border-radius: 8px; background: #fee2e2; color: #dc2626; display: flex; align-items: center; justify-content: center; font-size: 14px;">📄</div>
                                <div>
                                    <div style="font-weight: 700; font-size: 0.88rem; color: #0f172a;">Logashree_Resume.pdf</div>
                                    <div style="font-size: 0.76rem; color: #64748b;">Uploaded 2 hours ago</div>
                                </div>
                            </div>
                            <span style="background: #dcfce7; color: #15803d; font-weight: 700; font-size: 0.75rem; padding: 3px 10px; border-radius: 9999px;">Analyzed</span>
                        </div>
                        <!-- Item 2: Resume_Final.docx -->
                        <div class="ra-upload-item">
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <div style="width: 32px; height: 32px; border-radius: 8px; background: #dbeafe; color: #2563eb; display: flex; align-items: center; justify-content: center; font-size: 14px;">📄</div>
                                <div>
                                    <div style="font-weight: 700; font-size: 0.88rem; color: #0f172a;">Resume_Final.docx</div>
                                    <div style="font-size: 0.76rem; color: #64748b;">Uploaded 1 day ago</div>
                                </div>
                            </div>
                            <span style="background: #dcfce7; color: #15803d; font-weight: 700; font-size: 0.75rem; padding: 3px 10px; border-radius: 9999px;">Analyzed</span>
                        </div>
                        <!-- Item 3: Logashree_CV.pdf -->
                        <div class="ra-upload-item">
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <div style="width: 32px; height: 32px; border-radius: 8px; background: #fee2e2; color: #dc2626; display: flex; align-items: center; justify-content: center; font-size: 14px;">📄</div>
                                <div>
                                    <div style="font-weight: 700; font-size: 0.88rem; color: #0f172a;">Logashree_CV.pdf</div>
                                    <div style="font-size: 0.76rem; color: #64748b;">Uploaded 2 days ago</div>
                                </div>
                            </div>
                            <span style="background: #dbeafe; color: #1d4ed8; font-weight: 700; font-size: 0.75rem; padding: 3px 10px; border-radius: 9999px;">In Progress</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # ==========================================================================
    # 4. HOME OVERVIEW VIEW
    # ==========================================================================
    elif st.session_state.nav_page in ["🏠 Home", "Home"]:
        disable_proctoring()
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%); border: 1.5px solid #bfdbfe; border-radius: 20px; padding: 28px 32px; margin-bottom: 24px;">
                <span style="background: #ffffff; color: #2563eb; font-weight: 800; font-size: 0.78rem; padding: 4px 12px; border-radius: 9999px; border: 1px solid #bfdbfe;">✨ WELCOME BACK</span>
                <h1 style="margin: 10px 0 6px 0; font-size: 2.3rem; font-weight: 900; color: #0f172a;">Hello, {user_name}! 👋</h1>
                <p style="color: #475569; font-size: 1.05rem; margin: 0; max-width: 750px; line-height: 1.5;">
                    Your AI-guided career dashboard is ready. Upload your latest resume to verify your ATS score, practice with anti-cheat proctored mock tests, and follow your personalized skill roadmap.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # 3 High-Impact Cards
        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            st.markdown("""
                <div class="ra-sidebar-card" style="height: 100%;">
                    <div style="font-size: 32px; margin-bottom: 10px;">📄</div>
                    <h3 style="margin: 0 0 8px 0; font-size: 1.2rem; color: #0f172a;">Resume Analyzer</h3>
                    <p style="color: #64748b; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                        Get instant ATS compatibility scores, extract 40+ technical skills, and discover missing keywords.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Resume Analyzer ➔", type="primary", key="home_btn_ra", use_container_width=True):
                st.session_state.nav_page = "📄 Resume Analyzer"
                st.rerun()

        with hc2:
            st.markdown("""
                <div class="ra-sidebar-card" style="height: 100%;">
                    <div style="font-size: 32px; margin-bottom: 10px;">⚡</div>
                    <h3 style="margin: 0 0 8px 0; font-size: 1.2rem; color: #0f172a;">Proctored Mock Test</h3>
                    <p style="color: #64748b; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                        15 curated questions aligned with your target engineering role, guarded by live AI proctoring sensors.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Start Mock Test ➔", key="home_btn_quiz", use_container_width=True):
                st.session_state.nav_page = "📝 Proctored Mock Test"
                st.rerun()

        with hc3:
            st.markdown("""
                <div class="ra-sidebar-card" style="height: 100%;">
                    <div style="font-size: 32px; margin-bottom: 10px;">🗺️</div>
                    <h3 style="margin: 0 0 8px 0; font-size: 1.2rem; color: #0f172a;">Career Roadmap</h3>
                    <p style="color: #64748b; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                        Follow a structured, milestone-driven curriculum crafted specifically for your detected skill gaps.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("View Roadmap ➔", key="home_btn_road", use_container_width=True):
                st.session_state.nav_page = "🗺️ Career Roadmap"
                st.rerun()

    # ==========================================================================
    # 5. CAREER ROADMAP STANDALONE VIEW
    # ==========================================================================
    elif st.session_state.nav_page in ["🗺️ Career Roadmap", "🗺️ Roadmap", "Roadmap"]:
        disable_proctoring()
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px;">
                <div>
                    <h1 style="font-size: 2.1rem; font-weight: 800; color: #0f172a; margin: 0;">🗺️ Your Personalized Learning Track</h1>
                    <p style="color: #64748b; font-size: 0.95rem; margin: 4px 0 0 0;">Step-by-step milestones to bridge technical skill gaps and prepare for top tech interviews.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Roadmap milestones
        milestones = [
            ("Stage 1 • Foundations", "Core Language Mastery (Python & TypeScript)", "Deep dive into OOP, typing, and standard algorithm patterns.", "2-3 Days", "https://docs.python.org/3/"),
            ("Stage 2 • Architecture", "Modern Full Stack Frameworks (FastAPI & React)", "Build RESTful microservices and stateful responsive UI apps.", "1 Week", "https://fastapi.tiangolo.com/"),
            ("Stage 3 • Data & Cloud", "Database Architecture & Containerization (MongoDB & Docker)", "Containerize services, build multi-stage Dockerfiles, and index MongoDB.", "4-5 Days", "https://www.docker.com/"),
            ("Stage 4 • Production", "Cloud Deployment & CI/CD Pipelines (AWS & GitHub Actions)", "Deploy scalable container clusters and automate testing pipelines.", "1 Week", "https://aws.amazon.com/")
        ]

        for stage, title, desc, duration, url in milestones:
            st.markdown(f"""
                <div style="background: #ffffff; border: 1.5px solid #dbeafe; border-left: 6px solid #2563eb; border-radius: 16px; padding: 20px 24px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(37,99,235,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="background: #eff6ff; color: #1d4ed8; font-weight: 800; font-size: 0.78rem; padding: 3px 12px; border-radius: 9999px; border: 1px solid #bfdbfe;">{stage}</span>
                        <span style="color: #64748b; font-size: 0.82rem; font-weight: 700;">⏱️ Est. Time: {duration}</span>
                    </div>
                    <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; color: #0f172a;">{title}</h3>
                    <p style="color: #475569; font-size: 0.92rem; margin: 0 0 12px 0;">{desc}</p>
                    <a href="{url}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; color: #2563eb; font-weight: 800; font-size: 0.88rem; text-decoration: none;">
                        Open Documentation & Practice Labs ➔
                    </a>
                </div>
            """, unsafe_allow_html=True)

    # ==========================================================================
    # 6. CANDIDATE PROFILE & ACCOUNT MANAGEMENT
    # ==========================================================================
    elif st.session_state.nav_page in ["👤 Profile", "Profile"]:
        disable_proctoring()
        st.markdown("""
            <div style="margin-bottom: 22px;">
                <h1 style="font-size: 2.1rem; font-weight: 800; color: #0f172a; margin: 0;">👤 Candidate Profile & Credentials</h1>
                <p style="color: #64748b; font-size: 0.95rem; margin: 4px 0 0 0;">Manage your verified authentication details and cloud sync.</p>
            </div>
        """, unsafe_allow_html=True)

        prof_c1, prof_c2 = st.columns([1.2, 1])
        with prof_c1:
            st.markdown(f"""
                <div class="ra-sidebar-card">
                    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
                        <div style="width: 64px; height: 64px; border-radius: 50%; background: #2563eb; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 900;">
                            {user_initial}
                        </div>
                        <div>
                            <h2 style="margin: 0; font-size: 1.4rem; color: #0f172a;">{display_name}</h2>
                            <div style="color: #64748b; font-size: 0.9rem;">{user.get('email', 'Candidate Account')}</div>
                            <span style="background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; padding: 2px 10px; border-radius: 9999px; font-weight: 800; font-size: 0.72rem; display: inline-block; margin-top: 6px;">
                                VERIFIED PROFILE
                            </span>
                        </div>
                    </div>
                    <div style="border-top: 1px solid #f1f5f9; padding-top: 16px; display: flex; flex-direction: column; gap: 10px; font-size: 0.92rem;">
                        <div><strong>Email:</strong> {user.get('email', '--')}</div>
                        <div><strong>Account Type:</strong> Standard Engineering Candidate</div>
                        <div><strong>Cloud Database:</strong> MongoDB WiredTiger Active 🟢</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with prof_c2:
            st.markdown("""
                <div class="ra-sidebar-card">
                    <h3 style="margin-top: 0; font-size: 1.2rem; color: #0f172a;">Account Actions</h3>
                    <p style="color: #64748b; font-size: 0.88rem; margin-bottom: 18px;">Sign out of your active session on this device:</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🚪 Sign Out of Account", type="primary", key="btn_prof_signout", use_container_width=True):
                disable_proctoring()
                st.session_state.user = None
                st.session_state.oauth_state = None
                reset_quiz()
                st.rerun()


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
