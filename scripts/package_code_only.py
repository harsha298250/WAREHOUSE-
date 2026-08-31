"""
scripts/package_code_only.py

Generates a clean code_only.zip archive excluding database backups, dumps,
runtime logs, environment secrets, and binary database files.
"""
import os
import zipfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_ZIP = os.path.join(PROJECT_ROOT, "code_only.zip")

# Explicit exclusion patterns
EXCLUDE_DIRS = {
    ".git", ".pytest_cache", ".venv", "venv", "env", "ENV",
    "__pycache__", "build", "dist", "htmlcov", "mysql_data", "pg_data"
}

EXCLUDE_PREFIXES = (
    "data/backups",
    "data/exports",
    "data/raw",
    "data/processed",
    "backup_before_final_cleanup",
    "safe_backup_files",
    "scratch"
)

EXCLUDE_EXTENSIONS = (
    ".pyc", ".pyo", ".pyd", ".db", ".log", ".gz", ".tmp", ".zip"
)

EXCLUDE_EXACT_FILES = {
    ".env", "code_only.zip", "warehouse.db"
}


def is_excluded(rel_path: str) -> bool:
    rel_path_normalized = rel_path.replace("\\", "/")
    
    # Check directory components
    parts = rel_path_normalized.split("/")
    for part in parts:
        if part in EXCLUDE_DIRS or part.endswith(".egg-info"):
            return True
            
    # Check prefix paths
    for prefix in EXCLUDE_PREFIXES:
        if rel_path_normalized == prefix or rel_path_normalized.startswith(prefix + "/"):
            return True

    filename = os.path.basename(rel_path_normalized)
    if filename in EXCLUDE_EXACT_FILES or filename.startswith(".env."):
        return True

    if filename.endswith(EXCLUDE_EXTENSIONS):
        return True

    if filename.startswith("debug_") and filename.endswith(".png"):
        return True

    return False


def build_code_only_zip():
    print(f"Creating code-only package at: {OUTPUT_ZIP}")
    included_files = []
    
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not is_excluded(os.path.relpath(os.path.join(root, d), PROJECT_ROOT))]
            
            for file in files:
                abs_file = os.path.join(root, file)
                rel_file = os.path.relpath(abs_file, PROJECT_ROOT)
                
                if is_excluded(rel_file):
                    continue
                    
                zf.write(abs_file, rel_file)
                included_files.append(rel_file)

    print(f"Code-only package created successfully with {len(included_files)} files.")
    
    # Audit ZIP contents to guarantee zero backup files exist
    with zipfile.ZipFile(OUTPUT_ZIP, "r") as check_zip:
        for name in check_zip.namelist():
            if name.startswith("data/backups/") or "data/backups" in name:
                raise ValueError(f"CRITICAL PACKAGING REGRESSION: Excluded backup file '{name}' was found inside code_only.zip!")
                
    print("[PASS] Verification confirmed: code_only.zip strictly excludes data/backups/*.gz, *.sql, *.json!")


if __name__ == "__main__":
    build_code_only_zip()
