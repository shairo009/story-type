import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

class StoryEngine:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = (api_key or os.getenv("OPENCODE_API_KEY") or "").strip()
        self.base_url = (base_url or os.getenv("OPENCODE_BASE_URL") or "https://opencode.ai/zen").strip()
        self.model_name = (os.getenv("OPENCODE_MODEL") or "minimax-m2.5-free").strip()
        
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
        Write a 10-scene Hinglish COMIC story about {topic}.
        The story should be exactly 10 scenes to fit a 30-40 second video.
        
        RULES:
        1. 'narration': The AI narrator explaining the scene in Hinglish (Roman script).
        2. 'dialogue': The exact words characters say in Hinglish (Roman script).
        3. 'image_prompt': Technical English description for a scene. 
        
        CRITICAL CHARACTER & HAIR CONSISTENCY:
        Every single 'image_prompt' MUST include these exact character descriptions if they appear in the scene to prevent blending:
        - Andy: "A young boy named Andy with short CURLY BROWN hair, round glasses, and a white shirt."
        - Mona: "A young girl named Mona with short STRAIGHT BLACK hair and a pink striped shirt."
        
        Return exactly 10 scenes in JSON format.
        """
        
        system_prompt = """You are a Professional Comic Production Director.
Your task is to generate a 10-scene HINGLISH webcomic script.

### PRODUCTION SETTINGS:
- STYLE: Hand-drawn webcomic.
- CHARACTER ANCHOR 1: MONA - Short black hair, pink shirt.
- CHARACTER ANCHOR 2: ANDY - Brown curly hair, white shirt, red tie.

### DIRECTION:
Keep 'image_prompt' under 150 characters. Describe the 4-panel grid simply.
{
  "title": "Hinglish Title",
  "scenes": [
    {
      "narration": "AI Storytelling in Hinglish...", 
      "dialogue": "Character speech in Hinglish...",
      "image_prompt": "English prompt describing 4-panels with Mona and Andy..."
    },
    ...
  ]
}"""
        
        data = {
            "model": self.model_name,
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "system": system_prompt
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
                    print("Error: No text block found in API response. Trying fallback...")
                    return self.fallback_generate_story(topic)
                
                return self.parse_and_clean(content)
            else:
                print(f"Error from OpenCode: {response.status_code} - {response.text}. Using Fallback...")
                return self.fallback_generate_story(topic)
        except Exception as e:
            print(f"Exception during story generation: {e}. Using Fallback...")
            return self.fallback_generate_story(topic)

    def fallback_generate_story(self, topic):
        print("Story Fallback: Pollinations AI...")
        try:
            import urllib.parse
            prompt = f"Write a 10-scene Hinglish comic story about {topic}. Use JSON: " + \
                     "{\"title\": \"Title\", \"scenes\": [{\"narration\": \"Hinglish\", \"dialogue\": \"Hinglish\", \"image_prompt\": \"English description\"}]}"
            url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                return self.parse_and_clean(r.text)
        except Exception as e:
            print(f"Final Fallback Failed: {e}")
        return None

    def parse_and_clean(self, content):
        import re
        # Clean markdown and find the JSON object
        def clean_json_string(s):
            s = re.sub(r'<thinking>.*?</thinking>', '', s, flags=re.DOTALL)
            start = s.find('{')
            end = s.rfind('}')
            if start != -1 and end != -1:
                s = s[start:end+1]
            s = s.replace('"},"{', '"},{"').replace('"}, "{', '"},{"').replace('"} "{', '"},{"')
            return s

        content = clean_json_string(content)
        try:
            data = json.loads(content)
            if "scenes" in data: return data
            if isinstance(data, list): return {"title": "AI Story", "scenes": data}
        except:
            # Aggressive regex recovery
            narrations = re.findall(r'"narration":\s*"(.*?)"', content)
            prompts = re.findall(r'"image_prompt":\s*"(.*?)"', content)
            dialogues = re.findall(r'"dialogue":\s*"(.*?)"', content)
            scenes = []
            for n, d, p in zip(narrations, dialogues, prompts):
                scenes.append({"narration": n, "dialogue": d, "image_prompt": p})
            if scenes: return {"title": "AI Story", "scenes": scenes}
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
