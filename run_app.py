import streamlit.web.bootstrap as bootstrap
from pathlib import Path

def run():
    frontend_path = Path(__file__).parent / "frontend" / "main.py"
    bootstrap.run(str(frontend_path), "", [], {})
