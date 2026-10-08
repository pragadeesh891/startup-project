import sys
import unittest
import urllib.request

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import database
from quiz_engine import (
    ROLE_QUESTIONS,
    generate_test_for_role,
    build_diagnostic_roadmap
)
from app import analyze_resume_local

print("=" * 65)
print("STARTING COMPLETE CAREERPATH.AI END-TO-END VERIFICATION SUITE")
print("=" * 65)

# TEST 1: MongoDB Connection & User Lifecycle
print("\n[TEST 1] Testing MongoDB Connection & User Lifecycle...")
db = database.get_db()
assert db is not None, "Failed to connect to MongoDB!"
print(f" -> MongoDB Connected Successfully. Database: '{db.name}'")

test_name = "Automated Test User"
test_email = "autotest_verifier@careerpath.ai"
test_password = "SecurePassword123!"

# Clean any existing test document
db.users.delete_many({"email": test_email})
db.mock_tests.delete_many({"user_email": test_email})
db.resume_scans.delete_many({"user_email": test_email})

# Register
success, msg, user_doc = database.register_user(test_name, test_email, test_password)
assert success is True, f"User registration failed: {msg}"
assert user_doc["email"] == test_email
print(f" -> User Registration: PASSED ({msg})")

# Duplicate Prevention
dup_success, dup_msg, _ = database.register_user(test_name, test_email, test_password)
assert dup_success is False, "Duplicate user registration should be rejected!"
print(f" -> Duplicate Account Rejection: PASSED ({dup_msg})")

# Valid Login
auth_ok, auth_msg, auth_user = database.authenticate_user(test_email, test_password)
assert auth_ok is True, f"Authentication with correct credentials failed: {auth_msg}"
assert auth_user["email"] == test_email
print(f" -> Valid Authentication: PASSED ({auth_msg})")

# Invalid Login
fail_ok, fail_msg, _ = database.authenticate_user(test_email, "WrongPassword999")
assert fail_ok is False, "Authentication with wrong password should fail!"
print(f" -> Invalid Password Rejection: PASSED ({fail_msg})")

# System Stats
stats = database.get_db_stats()
print(f" -> Database Stats: {stats}")
assert stats["status"] == "Connected"
assert stats["users"] >= 1

# TEST 2: Quiz Engine & 15 Questions Generation for all 7 Roles
print("\n[TEST 2] Testing Quiz Engine: 15 Questions across all 7 Roles...")
roles = list(ROLE_QUESTIONS.keys())
assert len(roles) == 7, f"Expected 7 roles, found {len(roles)}"
print(f" -> Available Roles ({len(roles)}): {roles}")

for role in roles:
    quiz = generate_test_for_role(role, num=15)
    assert len(quiz) == 15, f"Role '{role}' generated {len(quiz)} questions instead of 15!"
    for idx, q in enumerate(quiz):
        assert "q" in q and len(q["q"]) > 5, f"Missing question text in {role} Q{idx+1}"
        assert "options" in q and len(q["options"]) == 4, f"Options not equal to 4 in {role} Q{idx+1}"
        assert "ans" in q and 0 <= q["ans"] < 4, f"Invalid answer index in {role} Q{idx+1}"
        assert "topic" in q and len(q["topic"]) > 0, f"Topic tag missing in {role} Q{idx+1}"
        assert "doc_url" in q and q["doc_url"].startswith("http"), f"Invalid documentation URL in {role} Q{idx+1}"
        assert "shortcut_tip" in q and len(q["shortcut_tip"]) > 0, f"Shortcut tip missing in {role} Q{idx+1}"
print(" -> All 7 Tech Roles Verified: Each accurately yields 15 validated 4-choice questions with answer keys, topic tags, doc URLs, and shortcut tips!")

# TEST 3: Quiz Evaluation & Diagnostic Shortcut Roadmap Builder
print("\n[TEST 3] Testing Evaluation & Diagnostic Shortcut Roadmap...")
sample_role = roles[0] # e.g. Full Stack Developer
sample_quiz = generate_test_for_role(sample_role, num=15)

# Simulate answering: 9 correct, 6 wrong
simulated_answers = []
score = 0
for i, q in enumerate(sample_quiz):
    if i < 9:
        simulated_answers.append(q["ans"]) # Correct
        score += 1
    else:
        # Wrong choice
        wrong_choice = (q["ans"] + 1) % 4
        simulated_answers.append(wrong_choice)

percentage = round((score / 15) * 100, 1)
print(f" -> Simulated Quiz Score: {score}/15 ({percentage}%)")

roadmap = build_diagnostic_roadmap(sample_role, sample_quiz, simulated_answers)
assert roadmap["weak_count"] > 0, "Weak topics should be identified from incorrect questions!"
assert roadmap["strong_count"] > 0, "Strong topics should be identified from correct questions!"
assert len(roadmap["roadmap_steps"]) > 0, "Actionable roadmap steps should be constructed!"

print(f" -> Strong Topics Count: {roadmap['strong_count']} ({roadmap['strong_topics']})")
print(f" -> Weak Topics / Roadmap Steps Count: {roadmap['weak_count']}")
for stg in roadmap["roadmap_steps"]:
    print(f"    * Step {stg['step']}: [{stg['priority']}] {stg['topic']} (~{stg['est_time']})")
    print(f"      Shortcut Tip: {stg['shortcut_tip']}")
    print(f"      Docs: {stg['doc_url']}")

# TEST 4: Mock Test DB Persistence & History Retrieval
print("\n[TEST 4] Testing Mock Test Persistence in MongoDB...")
test_saved = database.save_test_result(
    user_email=test_email,
    score=score,
    total=15,
    skills_tested=[q["topic"] for q in sample_quiz[:5]],
    role=sample_role,
    weak_topics=[s["topic"] for s in roadmap["roadmap_steps"]],
    roadmap=roadmap["roadmap_steps"]
)
assert test_saved is True, "Failed to save mock test result into MongoDB!"

test_history = database.get_user_test_history(test_email)
assert len(test_history) >= 1, "Mock test history retrieval failed!"
latest_test = test_history[0]
assert latest_test["score"] == score
assert latest_test["role"] == sample_role
assert len(latest_test["weak_topics"]) > 0
print(f" -> Test Result Persisted and Verified in MongoDB: Score {latest_test['score']}/{latest_test['total']} ({latest_test['percentage']}%)")

# TEST 5: Resume Analyzer (ATS Scoring & Insights) & Persistence
print("\n[TEST 5] Testing Local ATS Resume Analyzer & DB Storage...")
sample_resume_text = """
John Doe
Email: john.doe@example.com
Phone: (555) 123-4567
Summary:
Experienced Full Stack Developer with 4+ years building high-performance web applications.
Architected microservices that reduced API latency by 45% for 50,000+ daily active users.
Technical Skills:
Python, Django, FastAPI, React, JavaScript, TypeScript, Docker, Kubernetes, Git, PostgreSQL, MongoDB, Linux, AWS.
Experience:
- Developed and maintained responsive React user interfaces with modern UX state management.
- Built scalable REST APIs using Django and FastAPI connected to PostgreSQL and MongoDB databases.
- Deployed Docker containers and managed CI/CD pipelines on AWS.
"""
scan_results = analyze_resume_local(sample_resume_text)
assert len(scan_results["skills"]) >= 5, f"Expected >= 5 skills, found {scan_results['skills']}"
assert scan_results["ats_score"] >= 70, f"Expected high ATS score, got {scan_results['ats_score']}"
assert len(scan_results["strengths"]) > 0, "Expected strengths identified"
print(f" -> Extracted Skills ({len(scan_results['skills'])}): {scan_results['skills']}")
print(f" -> ATS Score: {scan_results['ats_score']}/100")
print(f" -> Strengths: {scan_results['strengths']}")

# Save scan to MongoDB
scan_saved = database.save_resume_scan(
    user_email=test_email,
    filename="sample_resume.pdf",
    skills=scan_results["skills"],
    strengths=scan_results["strengths"],
    suggestions=scan_results["suggestions"],
    word_count=scan_results["word_count"],
    ats_score=scan_results["ats_score"]
)
assert scan_saved is True, "Failed to save resume scan to MongoDB!"

scan_history = database.get_user_resume_history(test_email)
assert len(scan_history) >= 1, "Resume scan history retrieval failed!"
assert scan_history[0]["ats_score"] == scan_results["ats_score"]
print(f" -> Resume Scan Saved and Verified in MongoDB: ATS Score {scan_history[0]['ats_score']}/100")

# TEST 6: Live Web Server Endpoint Ping & Verification
print("\n[TEST 6] Testing Live Streamlit Server Endpoint (http://localhost:8501)...")
req = urllib.request.Request("http://localhost:8501", headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=5) as response:
        status_code = response.getcode()
        html_bytes = response.read()
        html_content = html_bytes.decode('utf-8')
        assert status_code == 200, f"Streamlit server returned HTTP {status_code}"
        print(f" -> Streamlit Server Status: HTTP {status_code} OK")
        assert "<pre><code>&lt;svg" not in html_content
        print(" -> Verified Clean Markup: No unescaped SVG code leaks in HTML.")
except Exception as e:
    print(f"Server check error: {e}")
    raise e

# Clean up test documents
db.users.delete_many({"email": test_email})
db.mock_tests.delete_many({"user_email": test_email})
db.resume_scans.delete_many({"user_email": test_email})
print(f" -> Test cleanup completed.")

print("\n" + "=" * 65)
print("ALL 6 END-TO-END VERIFICATION TESTS PASSED WITH 100% SUCCESS!")
print("=" * 65)
