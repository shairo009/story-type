import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# All topics with their next topic for continuity
CURRICULUM = [
    # (level, topic, next_topic, colors, graph_type)
    ("Class 1-5", "Counting & Tables", "Addition & Subtraction", "#00e5ff", "#ff6b35"),
    ("Class 1-5", "Addition & Subtraction", "Multiplication Magic", "#ff6b35", "#00e5ff"),
    ("Class 1-5", "Multiplication Magic", "Division & Fractions", "#a8ff3e", "#ff006e"),
    ("Class 1-5", "Division & Fractions", "Shapes & Geometry", "#ff006e", "#a8ff3e"),
    ("Class 6-8", "Algebra Basics", "Linear Equations", "#7c3aed", "#fbbf24"),
    ("Class 6-8", "Linear Equations", "Square Roots & Powers", "#fbbf24", "#7c3aed"),
    ("Class 6-8", "Square Roots & Powers", "Ratio & Proportion", "#10b981", "#f43f5e"),
    ("Class 9-12", "Quadratic Equations", "Trigonometry", "#f43f5e", "#10b981"),
    ("Class 9-12", "Trigonometry", "Logarithms", "#818cf8", "#fb923c"),
    ("Class 9-12", "Derivatives (Calculus)", "Integration", "#fb923c", "#818cf8"),
    ("Class 9-12", "Integration (Calculus)", "Probability & Stats", "#22d3ee", "#e879f9"),
    ("College", "Linear Algebra: Matrices", "Complex Numbers", "#e879f9", "#22d3ee"),
    ("College", "Complex Numbers", "Differential Equations", "#facc15", "#4ade80"),
    ("College", "Fourier Transform", "Laplace Transform", "#4ade80", "#facc15"),
    ("PhD", "Riemann Hypothesis", "Chaos Theory", "#ff0080", "#00ffcc"),
    ("PhD", "Quantum Mathematics", "String Theory Math", "#00ffcc", "#ff0080"),
]

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
        idx = (day - 1) % len(CURRICULUM)
        level, topic, next_topic, primary, secondary = CURRICULUM[idx]
        prev_topic = CURRICULUM[idx - 1][1] if day > 1 else None

        print(f"Generating lesson Day {day}: [{level}] {topic}")

        prompt = f"""
You are an expert math teacher creating a YouTube Shorts video script.
Level: {level}
Topic: {topic}
Lesson Number: {day}

Generate a complete multi-slide teaching script in Hindi (Roman script/Hinglish).
The video will have 4 slides: Intro, Concept, Graph, Example, Summary.

Return ONLY valid JSON, no markdown:
{{
  "level": "{level}",
  "topic": "{topic}",
  "lesson_num": {day},
  "prev_topic": "{prev_topic or ''}",
  "next_topic": "{next_topic}",
  "primary_color": "{primary}",
  "secondary_color": "{secondary}",
  "title": "Catchy Hindi title for {topic}",
  "intro_text": "Exciting 1-2 sentence intro in Hindi welcoming students",
  "concept_explanation": "3-4 sentence deep explanation of {topic} in Hindi with real-world analogy",
  "equation": "The main formula/equation as text (use ^ for power, integral sign etc.)",
  "graph_label": "What this graph shows",
  "graph_type": "line",
  "graph_labels": ["x1","x2","x3","x4","x5","x6","x7","x8","x9","x10"],
  "graph_data": [list of 10 numbers showing a meaningful pattern for {topic}],
  "key_points": ["3 key insights about {topic} in Hindi"],
  "problem_statement": "Ek real-world problem in Hindi",
  "problem_question": "The specific question to solve",
  "steps": ["Step 1 solution in Hindi", "Step 2", "Step 3"],
  "answer": "Final answer",
  "concept_audio": "Natural Hindi narration for concept slide (30 seconds worth)",
  "graph_audio": "Natural Hindi narration explaining the graph",
  "example_audio": "Natural Hindi narration walking through the example",
  "summary_audio": "Motivating summary in Hindi"
}}
"""

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": self.model_name,
            "max_tokens": 3000,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(f"{self.base_url}/v1/messages", headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                content = result["content"][0]["text"].strip()
                # Clean markdown fences
                for fence in ["```json", "```"]:
                    if fence in content:
                        parts = content.split(fence)
                        content = parts[1] if len(parts) > 1 else parts[0]
                content = content.strip().rstrip("```").strip()
                return json.loads(content)
            else:
                print(f"API error {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

        # Fallback
        return self._fallback(day, level, topic, next_topic, prev_topic, primary, secondary)

    def _fallback(self, day, level, topic, next_topic, prev_topic, primary, secondary):
        return {
            "level": level, "topic": topic, "lesson_num": day,
            "prev_topic": prev_topic or "", "next_topic": next_topic,
            "primary_color": primary, "secondary_color": secondary,
            "title": f"{topic} Seekhein - Lesson {day}",
            "intro_text": f"Namaste dosto! Aaj hum {topic} ki duniya mein enter karte hain. Taiyar ho jaiye!",
            "concept_explanation": f"{topic} ek aisi concept hai jo aapki zindagi mein roz kaam aati hai. Iska logic samajhna bohot simple hai. Aaj hum step by step dekhenge ki ye kaise kaam karta hai.",
            "equation": "a² + b² = c²",
            "graph_label": f"{topic} ka Growth Pattern",
            "graph_type": "line",
            "graph_labels": ["1","2","3","4","5","6","7","8","9","10"],
            "graph_data": [1, 4, 9, 16, 25, 36, 49, 64, 81, 100],
            "key_points": [f"{topic} hamesha consistent pattern follow karta hai", "Isko samajhne se aage ke topics easy ho jaate hain", "Practice se hi mastery aati hai"],
            "problem_statement": "Agar ek square ka side 5 cm hai",
            "problem_question": "Toh uska area kya hoga?",
            "steps": ["Area = side × side", "Area = 5 × 5", "Area = 25 sq cm"],
            "answer": "25 cm²",
            "concept_audio": f"Dosto, aaj hum {topic} seekhenge. {topic} ek bohot hi interesting concept hai jo aapki roz ki zindagi mein kaam aati hai.",
            "graph_audio": f"Is graph mein aap dekh sakte hain ki {topic} ka pattern kitna beautiful hai. Jaise-jaise x badhta hai, y bhi ek specific pattern mein badhta hai.",
            "example_audio": "Ab hum ek practical example solve karte hain. Dhyan se dekhiye, main aapko step by step samjhaunga.",
            "summary_audio": f"Toh aaj humne {topic} seekha. Agar aapko ye video helpful lagi toh subscribe zaroor karein!"
        }


if __name__ == "__main__":
    engine = MathEngine()
    lesson = engine.generate_lesson(1)
    print(json.dumps(lesson, indent=2, ensure_ascii=False))
