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
        Write a short 5-scene Hinglish COMIC story about {topic}.
        
        RULES:
        1. 'narration': The AI narrator explaining the scene in Hinglish (Roman script, e.g., 'Dono ne gufa dekhi').
        2. 'dialogue': The exact words characters say in Hinglish (Roman script) to be written IN the image.
        3. 'image_prompt': Technical English description for a 4-panel comic grid.
        
        Return exactly 5 scenes in JSON format.
        """
        
        system_prompt = """You are a Professional Comic Production Director.
Your task is to generate a 5-scene HINGLISH webcomic script.

### PRODUCTION SETTINGS:
- STYLE: Hand-drawn minimalist webcomic grid.
- CHARACTER ANCHOR 1: MONA - Short black hair, pink shirt.
- CHARACTER ANCHOR 2: ANDY - Brown curly hair, glasses, white shirt, red tie.

### OUTPUT FORMAT:
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
                    print("Error: No text block found in API response.")
                    return None
                # Clean markdown and find the JSON object
                import re
                
                def clean_json_string(s):
                    # Remove thinking blocks if any
                    s = re.sub(r'<thinking>.*?</thinking>', '', s, flags=re.DOTALL)
                    # Find the first { and last }
                    start = s.find('{')
                    end = s.rfind('}')
                    if start != -1 and end != -1:
                        s = s[start:end+1]
                    
                    # Fix common malformations in arrays of objects
                    s = s.replace('"},"{', '"},{"')
                    s = s.replace('"}, "{', '"},{"')
                    s = s.replace('"} "{', '"},{"')
                    s = s.replace('"},"', '"},{"')
                    
                    # Fix the specific "{" issue
                    s = s.replace('","{', '",{"')
                    s = s.replace('"],"{"', '":[{"')
                    
                    # General cleanup: remove extra quotes around objects
                    s = re.sub(r'("\s*\{)', '{', s)
                    s = re.sub(r'(\}\s*")', '}', s)
                    
                    return s

                content = clean_json_string(content)
                
                try:
                    # Try to parse as JSON first
                    data = json.loads(content)
                    if "scenes" in data:
                        return data
                    # If it's a list, wrap it
                    if isinstance(data, list):
                        return {"title": "AI Story", "scenes": data}
                except json.JSONDecodeError as e:
                    print(f"JSON still invalid after cleaning: {e}")
                
                # Last ditch effort: try to fix with a very aggressive regex
                try:
                    # Extract everything that looks like a narration/image_prompt pair
                    narrations = re.findall(r'"narration":\s*"(.*?)"', content)
                    prompts = re.findall(r'"image_prompt":\s*"(.*?)"', content)
                    title_match = re.search(r'"title":\s*"(.*?)"', content)
                    title = title_match.group(1) if title_match else "AI Story"
                    
                    scenes = []
                    for n, p in zip(narrations, prompts):
                        scenes.append({"narration": n, "image_prompt": p})
                    
                    if len(scenes) > 0:
                        print(f"Recovered {len(scenes)} scenes via regex.")
                        return {"title": title, "scenes": scenes}
                except Exception as ex:
                    print(f"Regex recovery failed: {ex}")
                
                raise ValueError("Could not extract scenes from model output.")
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
