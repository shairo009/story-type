import os
import asyncio
from playwright.async_api import async_playwright
from jinja2 import Template

class RenderEngine:
    def __init__(self, template_path="templates/math_3d.html"):
        with open(template_path, "r", encoding="utf-8") as f:
            self.template_content = f.read()
        self.output_dir = "temp_frames"
        os.makedirs(self.output_dir, exist_ok=True)

    async def render_lesson(self, lesson_data):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 720, "height": 1280})
            
            # Prepare data for Template
            template = Template(self.template_content)
            
            # We will render 4 frames (scenes)
            scenes = ["hook", "explanation", "example_problem", "example_answer"]
            frame_paths = []

            for i, scene_id in enumerate(scenes):
                # Map lesson data to template fields
                render_data = {
                    "title": lesson_data["title"],
                    "day": lesson_data.get("day", 1),
                    "hook": lesson_data["hook"],
                    "explanation": lesson_data["explanation"],
                    "example_answer": lesson_data["example_answer"],
                    "cta": lesson_data["cta"],
                    "problem_display": lesson_data["example_problem"],
                    "primary_color": lesson_data["visual_prompts"]["primary_color"],
                    "secondary_color": lesson_data["visual_prompts"]["secondary_color"]
                }
                
                html = template.render(**render_data)
                await page.set_content(html)
                
                # Switch to the specific step
                if scene_id == "explanation":
                    await page.evaluate("showStep('explanation')")
                elif scene_id == "example_answer":
                    await page.evaluate("showStep('answer')")
                elif scene_id == "example_problem":
                     await page.evaluate("showStep('explanation')") # Keep explanation or just problem

                # Wait for animations to settle
                await asyncio.sleep(1)
                
                path = os.path.join(self.output_dir, f"frame_{i}.png")
                await page.screenshot(path=path)
                frame_paths.append(path)
                print(f"Rendered frame {i}: {scene_id}")

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
