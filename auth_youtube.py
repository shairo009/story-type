import os
from src.uploader import YouTubeUploader

def run_auth():
    print("Starting YouTube Authentication...")
    try:
        # Just initializing the class will trigger get_authenticated_service()
        # which handles the browser flow and saves token.json
        uploader = YouTubeUploader()
        print("\n✅ Authentication Successful!")
        print("token.json has been created/updated.")
    except Exception as e:
        print(f"\n❌ Error during authentication: {e}")

if __name__ == "__main__":
    run_auth()
