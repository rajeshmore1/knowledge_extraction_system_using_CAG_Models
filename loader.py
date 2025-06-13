import os
from dotenv import load_dotenv
def load_config():
    """
    Load configuration settings with a hardcoded API key.
    
    Returns:
        dict: Configuration dictionary with API key and directories.
    """
    config = {
        "GOOGLE_API_KEY": "AIzaSyA73fIGKKe78J2PGfos4NlSPbVCd_0nTdg",  
        "UPLOAD_DIR": "data",
        "ALLOWED_EXT": {".pdf"},
    }
    if not config["GOOGLE_API_KEY"]:
        raise ValueError("GOOGLE_API_KEY is not set in configuration")
    return config