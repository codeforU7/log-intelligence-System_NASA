#!/usr/bin/env python
"""
Start the FastAPI server from the project root.
"""
import os
import sys
import subprocess

# Change to project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)

# Run uvicorn
subprocess.run([
    sys.executable, '-m', 'uvicorn',
    'backend.app:app',
    '--host', '127.0.0.1',
    '--port', '8000'
])
