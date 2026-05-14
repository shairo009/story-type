import os
import asyncio
import json
from playwright.async_api import async_playwright
from jinja2 import Template

class RenderEngine:
    def __init__(self, template_path="templates/advanced_3d_math.html"):
        with open(template_path, "r", encoding="utf-8") as f:
            self.template_content = f.read()
        self.output_dir = "temp_frames"
        os.makedirs(self.output_dir, exist_ok=True)

    async def render_lesson(self, lesson_data):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 720, "height": 1280})
            
            template = Template(self.template_content)
            
            # We render 1 long take or multiple frames. 
            # For shorts, 1-2 frames with long audio is fine, but we'll do 1 high-quality frame.
            render_data = {
                "level": lesson_data["level"],
                "title": lesson_data["title"],
                "explanation": lesson_data["explanation"],
                "equation": lesson_data["equation"],
                "graph_label": lesson_data["graph_label"],
                "graph_data": json.dumps(lesson_data["graph_data"]),
                "primary_color": lesson_data["visual_prompts"]["primary_color"],
                "secondary_color": lesson_data["visual_prompts"]["secondary_color"]
            }
            
            html = template.render(**render_data)
            await page.set_content(html)
            
            # Wait for Three.js and Chart.js to animate
            await asyncio.sleep(3)
            
            frame_paths = []
            path = os.path.join(self.output_dir, f"advanced_frame.png")
            await page.screenshot(path=path)
            frame_paths.append(path)

            await browser.close()
            return frame_paths

if __name__ == "__main__":
    # Test
    dummy_lesson = {
        "title": "Math Magic Day 1",
        "hook": "Namaste! Aaj hum kuch naya sikhenge.",
        "explanation": "Addition ka matlab hai cheezon ko jodna.",
        "example_problem": "2 + 2 = ?",
        "example_answer": "Sahi jawab hai 4!",
        "cta": "Subscribe for more!",
        "visual_prompts": {"primary_color": "#ff0080", "secondary_color": "#00ffcc"}
    }
    engine = RenderEngine()
    asyncio.run(engine.render_lesson(dummy_lesson))
