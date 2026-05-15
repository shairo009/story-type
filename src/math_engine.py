import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

COLORS = [
    ("#00e5ff", "#ff6b35"), ("#a8ff3e", "#ff006e"), ("#7c3aed", "#fbbf24"),
    ("#f43f5e", "#10b981"), ("#818cf8", "#fb923c"), ("#22d3ee", "#e879f9"),
    ("#facc15", "#4ade80"), ("#ff0080", "#00ffcc"), ("#00ff87", "#60efff"),
    ("#ff4d4d", "#f9ca24"),
]

class MathEngine:
    def __init__(self):
        self.api_key = (os.getenv("OPENCODE_API_KEY") or "").strip()
        self.base_url = (os.getenv("OPENCODE_BASE_URL") or "https://opencode.ai/zen").strip()
        self.model_name = (os.getenv("OPENCODE_MODEL") or "minimax-m2.5-free").strip()
        self.history_file = "math_history.json"

        with open("curriculum.json", "r", encoding="utf-8") as f:
            self.curriculum = json.load(f)["curriculum"]

        print(f"Curriculum loaded: {len(self.curriculum)} lessons total")

    def get_current_day(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                try:
                    return json.load(f).get("current_day", 1)
                except:
                    return 1
        return 1

    def increment_day(self):
        day = self.get_current_day()
        with open(self.history_file, "w") as f:
            json.dump({"current_day": day + 1}, f)

    def get_chapter(self, day):
        idx = (day - 1) % len(self.curriculum)
        return self.curriculum[idx], idx

    def generate_lesson(self, day=1):
        chapter, idx = self.get_chapter(day)
        next_chapter = self.curriculum[(idx + 1) % len(self.curriculum)]
        pc, sc = COLORS[idx % len(COLORS)]

        cls = chapter["class"]
        topic = chapter["topic"]
        chapter_num = chapter["chapter"]
        subtopics = chapter["subtopics"]
        subtopic = subtopics[(day - 1) % len(subtopics)]

        print(f"Day {day}: Class {cls} | Ch.{chapter_num} | {topic} | {subtopic}")

        prompt = f"""You are an expert Indian math teacher for Class {cls} students.
Generate a YouTube Shorts video script teaching: {subtopic} (from Chapter: {topic}, Class {cls} NCERT).

Provide a JSON with these EXACT keys (no markdown, valid JSON only):
{{
  "class_num": {cls},
  "lesson_num": {day},
  "chapter_num": {chapter_num},
  "topic": "{topic}",
  "title": "Catchy Hindi title for {subtopic}",
  "equation": "The main formula or concept (1-2 lines, use text symbols like ^, sqrt(), etc.)",
  "steps": [
    "Step 1: Hindi explanation with logic (max 15 words)",
    "Step 2: Hindi explanation with logic (max 15 words)",
    "Step 3: Hindi with a real-world example (max 15 words)",
    "Step 4: Final key takeaway in Hindi (max 15 words)"
  ],
  "graph_data": [list of 8 numbers relevant to {subtopic}],
  "graph_labels": [list of 8 short labels],
  "next_lesson_text": "Agli video: {next_chapter['topic']} (Class {next_chapter['class']})",
  "intro_audio": "30-second natural Hindi narration introducing {subtopic}",
  "main_audio": "60-second teaching in Hindi explaining {subtopic} with logic and example",
  "outro_audio": "15-second energetic Hindi outro with subscribe CTA",
  "primary_color": "{pc}",
  "secondary_color": "{sc}"
}}"""

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": self.model_name,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            r = requests.post(f"{self.base_url}/v1/messages", headers=headers, json=data, timeout=60)
            if r.status_code == 200:
                content = r.json()["content"][0]["text"].strip()
                # Strip markdown fences
                if "```" in content:
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip().rstrip("```").strip()
                return json.loads(content)
        except Exception as e:
            print(f"API error: {e}")

        return self._fallback(day, cls, chapter_num, topic, subtopic, next_chapter, pc, sc)

    def _fallback(self, day, cls, chapter_num, topic, subtopic, next_chapter, pc, sc):
        return {
            "class_num": cls, "lesson_num": day, "chapter_num": chapter_num,
            "topic": topic, "title": f"{subtopic} Seekhein!",
            "equation": f"{subtopic}\n= Aasaan hai!",
            "steps": [
                f"{subtopic} ka matlab samjho",
                "Real life mein iska use dekho",
                "Formula yaad karo: ek baar mein",
                "Practice karo, expert ban jao!"
            ],
            "graph_data": [1, 4, 9, 16, 25, 36, 49, 64],
            "graph_labels": ["1", "2", "3", "4", "5", "6", "7", "8"],
            "next_lesson_text": f"Agli video: {next_chapter['topic']} (Class {next_chapter['class']})",
            "intro_audio": f"Namaste dosto! Aaj Class {cls} mein hum sikhenge {subtopic}.",
            "main_audio": f"Dosto, {subtopic} bohot important concept hai. Chaliye ise step by step samjhte hain.",
            "outro_audio": "Agar aapko ye video helpful lagi toh like aur subscribe zaroor karein!",
            "primary_color": pc, "secondary_color": sc
        }


if __name__ == "__main__":
    e = MathEngine()
    lesson = e.generate_lesson(1)
    print(json.dumps(lesson, indent=2, ensure_ascii=False))
