import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

class StoryEngine:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.getenv("OPENCODE_API_KEY")
        self.base_url = base_url or os.getenv("OPENCODE_BASE_URL") or "https://opencode.ai/zen"
        self.model_name = os.getenv("OPENCODE_MODEL") or "minimax-m2.5-free"
        
        if not self.api_key:
            raise ValueError("OPENCODE_API_KEY not found.")

    def generate_story(self, topic="mystery"):
        # OpenCode.ai uses Anthropic protocol
        url = f"{self.base_url}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        prompt = f"""
        Write a compelling 50-word story about {topic} for a YouTube Short.
        Break the story into exactly 5 logical scenes.
        For each scene, provide:
        1. The narration text (what is said).
        2. A highly descriptive image prompt for an AI image generator (Stable Diffusion).
        
        Return the result ONLY as a JSON object with this structure:
        {{
            "title": "Story Title",
            "scenes": [
                {{
                    "narration": "Text for scene 1",
                    "image_prompt": "Detailed image prompt for scene 1"
                }},
                ...
            ]
        }}
        """
        
        data = {
            "model": self.model_name,
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "system": "You are a creative storyteller. Output only raw JSON."
        }
        
        print(f"Generating story using {self.model_name} at {self.base_url}...")
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                content = ""
                for block in result.get("content", []):
                    if block.get("type") == "text":
                        content = block.get("text", "").strip()
                        break
                
                if not content:
                    print("Error: No text block found in API response.")
                    return None
                # Clean markdown and find the JSON object
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                
                return json.loads(content)
            else:
                print(f"Error from OpenCode: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception during story generation: {e}")
            print(f"Raw content was: {content}")
            return None

if __name__ == "__main__":
    # Test run
    try:
        engine = StoryEngine()
        story = engine.generate_story("a mysterious cat in a library")
        if story:
            print(json.dumps(story, indent=2))
    except Exception as e:
        print(f"Test failed: {e}")
