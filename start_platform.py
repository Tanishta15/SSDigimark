"""
Startup script for MPPSC Integrated Platform
Ensures proper configuration before launching with D drive cache
"""

import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure D drive cache FIRST before any imports
print("🔧 Configuring HuggingFace cache to D drive...")
os.environ['HF_HOME'] = 'D:/huggingface_cache'
os.environ['HF_HUB_CACHE'] = 'D:/huggingface_cache/hub'
os.environ['TRANSFORMERS_CACHE'] = 'D:/huggingface_cache/transformers'
os.environ['HF_DATASETS_CACHE'] = 'D:/huggingface_cache/datasets'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Fix Streamlit torch compatibility issue
os.environ['STREAMLIT_WATCHER_DISABLE_FOLDER_OBSERVER'] = '1'

# Create cache directories if they don't exist
cache_dirs = [
    Path('D:/huggingface_cache'),
    Path('D:/huggingface_cache/hub'),
    Path('D:/huggingface_cache/transformers'),
    Path('D:/huggingface_cache/datasets')
]

for cache_dir in cache_dirs:
    cache_dir.mkdir(parents=True, exist_ok=True)

print(f"✅ HuggingFace cache configured to: {os.environ['HF_HOME']}")

# Import and apply lightweight configuration
print("🔧 Applying lightweight configuration...")
try:
    import lightweight_startup
    print("✅ Lightweight configuration applied")
except ImportError:
    print("⚠️ Lightweight configuration not found")

# Set working directory
os.chdir(current_dir)

# Import and run the main platform
if __name__ == "__main__":
    print("🚀 Starting MPPSC Integrated Platform...")
    print("🌐 Opening on port 8502...")
    
    try:
        import streamlit.web.cli as stlit
        import streamlit.web.bootstrap as bootstrap
        
        # Configure for our specific setup
        sys.argv = [
            "streamlit", 
            "run", 
            "integrated_mppsc_platform.py",
            "--server.port", "8502",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false",
            "--server.allowRunOnSave", "true",
            "--server.fileWatcherType", "none"
        ]
        
        stlit.main()
        
    except Exception as e:
        print(f"❌ Failed to start with streamlit CLI: {e}")
        print("💡 Trying alternative method...")
        
        try:
            # Alternative method
            os.system("streamlit run integrated_mppsc_platform.py --server.port 8502")
        except Exception as e2:
            print(f"❌ Alternative method failed: {e2}")
            print("\n� Manual startup instructions:")
            print("1. Open command prompt")
            print("2. Navigate to: d:\\internship\\Digimark\\integration")
            print("3. Run: streamlit run integrated_mppsc_platform.py --server.port 8502")
            print("4. Open: http://localhost:8502 in your browser")
