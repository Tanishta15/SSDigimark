#!/usr/bin/env python3
"""
Startup script for MPPSC Services Platform
"""

import os
import sys
import subprocess

def run_app():
    """Run the Streamlit application"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up environment
    os.chdir(current_dir)
    
    # Add paths to ensure modules can be imported
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'SSDigimark-master'))
    sys.path.insert(0, os.path.join(current_dir, 'SSDigimark-Question-generator'))
    sys.path.insert(0, os.path.join(current_dir, 'finalflow'))
    
    print("Starting MPPSC Services Platform...")
    print("Working directory:", current_dir)
    print("Main page:", os.path.join(current_dir, 'mainpage.py'))
    
    # Check if mainpage.py exists
    mainpage_path = os.path.join(current_dir, 'mainpage.py')
    if not os.path.exists(mainpage_path):
        print("Error: mainpage.py not found!")
        return
    
    print("All checks passed. Starting Streamlit...")
    print("-" * 50)
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            mainpage_path,
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ], check=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    run_app()
