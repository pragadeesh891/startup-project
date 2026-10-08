import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import bcrypt

# Default to local MongoDB instance, or configure via environment variable
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "career_path_ai")

_client = None

def get_client():
    """Returns a singleton MongoClient instance with short timeout."""
    global _client
    if _client is None:
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2500)
        except Exception as e:
            print(f"Error initializing MongoClient: {e}")
    return _client

def get_db():
    """Returns the database instance."""
    client = get_client()
    if client:
        return client[DB_NAME]
    return None

def check_db_connection():
    """Pings MongoDB and returns a tuple (is_connected: bool, message: str)."""
    try:
        client = get_client()
        if client is None:
            return False, "Could not initialize client"
        client.admin.command("ping")
        return True, "Connected to MongoDB"
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        return False, f"Connection failed: {e}"
    except Exception as e:
        return False, str(e)

def init_indexes():
    """Ensures unique indexes on users collection."""
    try:
        db = get_db()
        if db is not None:
            db.users.create_index([("email", ASCENDING)], unique=True)
            db.resume_scans.create_index([("user_email", ASCENDING), ("uploaded_at", DESCENDING)])
            db.mock_tests.create_index([("user_email", ASCENDING), ("timestamp", DESCENDING)])
    except Exception as e:
        print(f"Error creating indexes: {e}")

# Call init_indexes on import
try:
    init_indexes()
except Exception:
    pass

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def register_user(name: str, email: str, password: str):
    """
    Registers a new user in MongoDB.
    Returns: (success: bool, message: str, user_dict: dict or None)
    """
    name = name.strip()
    email = email.strip().lower()
    
    if not name:
        return False, "Full Name is required.", None
    if not email or "@" not in email:
        return False, "A valid email address is required.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None
        
    db = get_db()
    if db is None:
        return False, "Database connection unavailable.", None
        
    try:
        existing = db.users.find_one({"email": email})
        if existing:
            return False, "An account with this email already exists.", None
            
        hashed_pw = hash_password(password)
        now = datetime.utcnow()
        user_doc = {
            "name": name,
            "email": email,
            "password_hash": hashed_pw,
            "created_at": now,
            "last_login": now
        }
        res = db.users.insert_one(user_doc)
        user_doc["_id"] = str(res.inserted_id)
        # remove password_hash from return dict
        user_doc.pop("password_hash", None)
        return True, "Registration successful!", user_doc
    except Exception as e:
        return False, f"Database error during registration: {str(e)}", None

def authenticate_user(email: str, password: str):
    """
    Authenticates a user by email and password.
    Returns: (success: bool, message: str, user_dict: dict or None)
    """
    email = email.strip().lower()
    db = get_db()
    if db is None:
        return False, "Database connection unavailable.", None
        
    try:
        user = db.users.find_one({"email": email})
        if not user:
            return False, "No account found with this email.", None
            
        if not verify_password(password, user.get("password_hash", "")):
            return False, "Incorrect password. Please try again.", None
            
        # Update last login
        db.users.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.utcnow()}})
        
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return True, "Login successful!", user
    except Exception as e:
        return False, f"Authentication error: {str(e)}", None

def save_resume_scan(user_email: str, filename: str, skills: list, strengths: list, suggestions: list, word_count: int, ats_score: int):
    """Saves a resume scan result for a user into MongoDB."""
    db = get_db()
    if db is None:
        return False
    try:
        doc = {
            "user_email": user_email.strip().lower(),
            "filename": filename,
            "skills": skills,
            "strengths": strengths,
            "suggestions": suggestions,
            "word_count": word_count,
            "ats_score": ats_score,
            "uploaded_at": datetime.utcnow()
        }
        db.resume_scans.insert_one(doc)
        return True
    except Exception as e:
        print(f"Error saving resume scan: {e}")
        return False

def get_user_resume_history(user_email: str, limit: int = 10):
    """Fetches recent resume scan history for a user from MongoDB."""
    db = get_db()
    if db is None:
        return []
    try:
        cursor = db.resume_scans.find(
            {"user_email": user_email.strip().lower()}
        ).sort("uploaded_at", DESCENDING).limit(limit)
        history = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            history.append(doc)
        return history
    except Exception as e:
        print(f"Error retrieving resume history: {e}")
        return []

def save_test_result(user_email: str, score: int, total: int, skills_tested: list, role: str = "General", weak_topics: list = None, roadmap: list = None):
    """Saves mock test scores and diagnostic roadmap for a user into MongoDB."""
    db = get_db()
    if db is None:
        return False
    try:
        percentage = round((score / total) * 100, 1) if total > 0 else 0
        doc = {
            "user_email": user_email.strip().lower(),
            "role": role,
            "score": score,
            "total": total,
            "percentage": percentage,
            "skills_tested": skills_tested,
            "weak_topics": weak_topics or [],
            "roadmap": roadmap or [],
            "timestamp": datetime.utcnow()
        }
        db.mock_tests.insert_one(doc)
        return True
    except Exception as e:
        print(f"Error saving mock test result: {e}")
        return False

def get_user_test_history(user_email: str, limit: int = 10):
    """Fetches recent mock test history for a user from MongoDB."""
    db = get_db()
    if db is None:
        return []
    try:
        cursor = db.mock_tests.find(
            {"user_email": user_email.strip().lower()}
        ).sort("timestamp", DESCENDING).limit(limit)
        history = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            history.append(doc)
        return history
    except Exception as e:
        print(f"Error retrieving test history: {e}")
        return []

def get_db_stats():
    """Returns database stats for the admin/diagnostic panel."""
    db = get_db()
    if db is None:
        return {"status": "Disconnected", "users": 0, "scans": 0, "tests": 0}
    try:
        users_count = db.users.count_documents({})
        scans_count = db.resume_scans.count_documents({})
        tests_count = db.mock_tests.count_documents({})
        return {
            "status": "Connected",
            "database": DB_NAME,
            "users": users_count,
            "scans": scans_count,
            "tests": tests_count
        }
    except Exception as e:
        return {"status": f"Error: {e}", "users": 0, "scans": 0, "tests": 0}
