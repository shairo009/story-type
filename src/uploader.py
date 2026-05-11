import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import json

# Scopes required for uploading videos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

class YouTubeUploader:
    def __init__(self, secrets_file="client_secrets.json", token_file="token.json"):
        self.secrets_file = secrets_file
        self.token_file = token_file
        self.youtube = self.get_authenticated_service()

    def get_authenticated_service(self):
        creds = None
        if os.path.exists(self.token_file):
            creds = google.oauth2.credentials.Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.secrets_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        return build("youtube", "v3", credentials=creds)

    def upload_video(self, file_path, title, description, tags=None, category_id="22"):
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or ["shorts", "ai", "story"],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "public",  # Can be "private" or "unlisted" for testing
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        print(f"Uploading video: {title}...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")

        print(f"Upload complete! Video ID: {response.get('id')}")
        return response.get('id')

if __name__ == "__main__":
    # Test requires local client_secrets.json
    print("Uploader test requires client_secrets.json. Please run main.py for setup.")
