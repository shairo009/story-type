import os
import asyncio
import json
from playwright.async_api import async_playwright
from jinja2 import Template

class RenderEngine:
    def __init__(self):
        with open("templates/animated_lesson.html", "r", encoding="utf-8") as f:
            self.template = Template(f.read())
        os.makedirs("temp_frames", exist_ok=True)

    async def render_lesson(self, lesson):
        """
        Captures multiple frames at different animation timestamps
        to create a smooth animated video (not a single static pic).
        """
        frame_paths = []

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 720, "height": 1280})

            html = self.template.render(
                class_num=lesson["class_num"],
                lesson_num=lesson["lesson_num"],
                chapter_num=lesson["chapter_num"],
                topic=lesson["topic"],
                title=lesson["title"],
                equation=lesson["equation"],
                steps=lesson["steps"],
                next_lesson_text=lesson["next_lesson_text"],
                primary_color=lesson["primary_color"],
                secondary_color=lesson["secondary_color"]
            )

            await page.set_content(html, wait_until="domcontentloaded")

            # === CAPTURE ANIMATION FRAMES ===
            # Total: ~3.5s animation. Capture every 200ms = ~18 frames
            # This makes a smooth animated-looking video
            print("  Capturing animation frames...")
            for frame_i in range(18):
                await asyncio.sleep(0.2)  # 200ms between frames
                path = f"temp_frames/frame_{frame_i:02d}.png"
                await page.screenshot(path=path)
                frame_paths.append(path)

            await browser.close()

        print(f"  Captured {len(frame_paths)} animation frames")
        return frame_paths
