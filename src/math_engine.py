import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class MathEngine:
    def __init__(self):
        self.api_key = (os.getenv("OPENCODE_API_KEY") or "").strip()
        self.base_url = (os.getenv("OPENCODE_BASE_URL") or "https://opencode.ai/zen").strip()
        self.model_name = (os.getenv("OPENCODE_MODEL") or "minimax-m2.5-free").strip()
        self.history_file = "math_history.json"

    def get_current_day(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                try:
                    data = json.load(f)
                    return data.get("current_day", 1)
                except:
                    return 1
        return 1

    def increment_day(self):
        day = self.get_current_day()
        with open(self.history_file, "w") as f:
            json.dump({"current_day": day + 1}, f)

    def generate_lesson(self, day=1):
        # Topics progression
        topics = [
            "Introduction to Numbers (1-10)",
            "Magic of Zero",
            "Simple Addition with Fruits",
            "Subtraction: The Vanishing Act",
            "Multiplication: Fast Addition",
            "Division: Sharing is Caring",
            "Odd vs Even Numbers",
            "Comparing Numbers: Greater or Smaller",
            "Shapes in 3D",
            "Telling Time"
        ]
        
        # Current and Previous topic
        current_idx = (day - 1) % len(topics)
        topic = topics[current_idx]
        prev_topic = topics[current_idx - 1] if day > 1 else None
        
        # Styles for variety
        themes = ["Cyberpunk", "Space Adventure", "Magic Forest", "Neon Ocean", "Vintage Comic"]
        theme = themes[(day - 1) % len(themes)]

        print(f"Generating Lesson for Day {day}: {topic} (Prev: {prev_topic})...")

        continuity_instruction = ""
        if prev_topic:
            continuity_instruction = f"Start with: 'Dosto, pichli video mein humne {prev_topic} sikha tha, aur aaj hum {topic} sikhne wale hain!'"
        else:
            continuity_instruction = f"Start with a warm welcome like 'Namaste! Aaj se hum math ki ek mazedar series shuru kar rahe hain!'"

        prompt = f"""
        Generate a 30-second Math Lesson script for kids in Hindi (Hinglish/Roman script).
        Topic: {topic}
        Current Lesson Number: {day}
        {continuity_instruction}
        
        RULES:
        1. Keep it high energy and fun.
        2. Explain the concept simply in 2-3 sentences.
        3. Provide one practice problem and answer.
        
        JSON Structure:
        {{
          "lesson_number": {day},
          "title": "Lesson {day}: {topic} in Hindi",
          "hook": "The intro sentence recapping previous lesson or welcoming",
          "explanation": "Simple step-by-step explanation in Hindi",
          "example_problem": "Fun math problem",
          "example_answer": "Answer with explanation",
          "cta": "Fun call to action in Hindi to subscribe",
          "visual_prompts": {{
            "background_theme": "{theme}",
            "primary_color": "vibrant hex",
            "secondary_color": "vibrant hex"
          }}
        }}
        """

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(f"{self.base_url}/v1/messages", headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                content = result["content"][0]["text"].strip()
                # Simple cleaning
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                return json.loads(content)
        except Exception as e:
            print(f"Error generating lesson: {e}")
            # Minimal fallback
            return {
                "title": f"Day {day}: Math Magic",
                "hook": "Namaste dosto! Kya aap taiyar hain math ki nayi trick ke liye?",
                "explanation": f"Aaj hum sikhenge {topic} ke baare mein.",
                "example_problem": "Agar aapke paas 2 apple hain aur 1 aur mil jaye, toh kitne honge?",
                "example_answer": "Bilkul sahi, 3 apples!",
                "cta": "Aisi hi mazedar video ke liye Subscribe karein!",
                "visual_prompts": {"background_theme": theme, "primary_color": "#ff0080", "secondary_color": "#00ffcc"}
            }

if __name__ == "__main__":
    engine = MathEngine()
    lesson = engine.generate_lesson(1)
    print(json.dumps(lesson, indent=2))
