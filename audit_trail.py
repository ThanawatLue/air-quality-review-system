import os
import sys
import json
import hashlib
from datetime import datetime
import getpass

def get_base_path():
    """Resolve the absolute base path whether running as script or frozen executable."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))

LOG_DIR = os.path.join(get_base_path(), "logs")
LOG_FILE = os.path.join(LOG_DIR, "audit_trail.log")

def calculate_entry_hash(timestamp, user, action, prev_hash):
    """Calculates SHA-256 for a single log entry linked to the previous entry."""
    data = f"{timestamp}|{user}|{action}|{prev_hash}"
    return hashlib.sha256(data.encode()).hexdigest()

def log_event(action, details=""):
    """Logs an event with a tamper-evident hash-chain."""
    # GAMP 5: Ensure log directory exists (IQ-TC-02)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # CRR-TC-01: User Identity Capture Verification (Ref: CRR-01)
    # Use getpass.getuser() to reliably get the human/service account identity
    try:
        user = getpass.getuser()
    except Exception:
        user = os.environ.get('USERNAME', 'UNKNOWN_USER')
    
    # Get last entry's hash
    prev_hash = "0" * 64
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    prev_hash = last_entry.get("entry_hash", prev_hash)
        except Exception:
            pass # Fallback to seed hash if file is completely unreadable during parse
    
    entry_hash = calculate_entry_hash(timestamp, user, action, prev_hash)
    
    log_entry = {
        "timestamp": timestamp,
        "user": user,
        "action": action,
        "details": details,
        "prev_hash": prev_hash,
        "entry_hash": entry_hash
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def verify_audit_trail(): # IQ-TC-07: Pre-Flight Integrity Check
    """Verifies the integrity of the entire audit trail hash-chain."""
    if not os.path.exists(LOG_FILE):
        return True, "No log file found. Starting fresh chain."
    
    expected_prev_hash = "0" * 64
    try:
        with open(LOG_FILE, "r") as f:
            for i, line in enumerate(f):
                entry = json.loads(line)
                # 1. Verify links
                if entry["prev_hash"] != expected_prev_hash:
                    return False, f"Broken chain at line {i+1}: Hash mismatch."
                
                # 2. Verify current entry hash
                recalculated_hash = calculate_entry_hash(
                    entry["timestamp"], entry["user"], entry["action"], entry["prev_hash"]
                )
                if entry["entry_hash"] != recalculated_hash:
                    return False, f"Tampered entry at line {i+1}: Integrity check failed."
                
                expected_prev_hash = entry["entry_hash"]
                
        return True, "Audit trail integrity verified."
    except Exception as e:
        return False, f"File format corruption: {str(e)}"
