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
        # Levels progression
        levels = ["Primary (Class 1-5)", "Middle (Class 6-8)", "High School (Class 9-12)", "College/University", "PhD/Advanced Research"]
        current_level = levels[(day - 1) % len(levels)]

        # Topics per level
        topics_map = {
            "Primary (Class 1-5)": ["Tables & Counting", "Addition Magic", "Fraction Fun", "Geometric Shapes"],
            "Middle (Class 6-8)": ["Algebra Basics", "Ratio & Proportion", "Square Roots", "Simple Geometry"],
            "High School (Class 9-12)": ["Calculus: Derivatives", "Trigonometry Hacks", "Quadratic Equations", "Probability Laws"],
            "College/University": ["Linear Algebra: Matrices", "Complex Analysis", "Differential Equations", "Number Theory"],
            "PhD/Advanced Research": ["Quantum Math", "Riemann Hypothesis", "String Theory Equations", "Chaos Theory Logic"]
        }
        
        # Select topic based on level and rotation
        topics_pool = topics_map[current_level]
        topic = topics_pool[((day - 1) // len(levels)) % len(topics_pool)]
        
        # Styles for variety
        themes = ["Cyberpunk", "Deep Space", "Abstract Geometric", "Matrix Neon", "Golden Ratio"]
        theme = themes[(day - 1) % len(themes)]

        print(f"Generating ADVANCED Lesson for Day {day}: {topic} ({current_level})...")

        prompt = f"""
        Generate a Professional Advanced Math Lesson script in Hindi (Roman script).
        Level: {current_level}
        Topic: {topic}
        Current Lesson Number: {day}
        
        The content must be academically accurate but presented in a fast-paced, cool way for YouTube Shorts.
        
        JSON Structure:
        {{
          "level": "{current_level}",
          "title": "Advanced {topic}",
          "explanation": "Deep logical explanation in Hindi (Hinglish)",
          "equation": "A beautiful LaTeX-style or text equation (e.g., e=mc^2 or Integral symbols)",
          "graph_label": "What the graph represents",
          "graph_data": [a list of 10-15 numbers for a chart.js line graph],
          "visual_prompts": {{
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
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(f"{self.base_url}/v1/messages", headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                content = result["content"][0]["text"].strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                return json.loads(content)
        except Exception as e:
            print(f"Error generating advanced lesson: {e}")
            return {
                "level": current_level,
                "title": f"The Beauty of {topic}",
                "explanation": f"Dosto, aaj hum {topic} ki gehrayi mein jayenge. Iske peeche ka logic bohot hi simple hai agar aap dhyan se dekhein.",
                "equation": "dy/dx = lim(h->0) [f(x+h) - f(x)]/h",
                "graph_label": "Function Growth",
                "graph_data": [1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
                "visual_prompts": {"primary_color": "#00ff00", "secondary_color": "#00ffff"}
            }


if __name__ == "__main__":
    engine = MathEngine()
    lesson = engine.generate_lesson(1)
    print(json.dumps(lesson, indent=2))
