import subprocess
from dotenv import load_dotenv

load_dotenv()
if __name__ == "__main__":
    cmd = ["celery", "-A", "backend.celery_app.celery", "worker", "--loglevel=info"]
    subprocess.run(cmd)
