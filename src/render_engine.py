import os
import asyncio
import json
from playwright.async_api import async_playwright
from jinja2 import Template

TEMPLATES = {
    "intro":   "templates/slide_intro.html",
    "concept": "templates/slide_concept.html",
    "graph":   "templates/slide_graph.html",
    "example": "templates/slide_example.html",
    "summary": "templates/slide_summary.html",
}

class RenderEngine:
    def __init__(self):
        self.templates = {}
        for name, path in TEMPLATES.items():
            with open(path, "r", encoding="utf-8") as f:
                self.templates[name] = Template(f.read())
        self.output_dir = "temp_frames"
        os.makedirs(self.output_dir, exist_ok=True)

    async def _screenshot(self, page, html, path, wait=2.5):
        await page.set_content(html, wait_until="networkidle")
        await asyncio.sleep(wait)
        await page.screenshot(path=path, full_page=False)
        print(f"  Frame saved: {path}")

    async def render_lesson(self, lesson):
        pc = lesson["primary_color"]
        sc = lesson["secondary_color"]
        frame_paths = []

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 720, "height": 1280})

            # 1. INTRO SLIDE
            html = self.templates["intro"].render(
                lesson_num=lesson["lesson_num"],
                level=lesson["level"],
                title=lesson["title"],
                intro_text=lesson["intro_text"],
                prev_topic=lesson.get("prev_topic", ""),
                primary_color=pc, secondary_color=sc
            )
            path = os.path.join(self.output_dir, "slide_0_intro.png")
            await self._screenshot(page, html, path, wait=1.5)
            frame_paths.append(path)

            # 2. CONCEPT SLIDE
            html = self.templates["concept"].render(
                topic=lesson["topic"],
                explanation=lesson["concept_explanation"],
                equation=lesson["equation"],
                primary_color=pc, secondary_color=sc
            )
            path = os.path.join(self.output_dir, "slide_1_concept.png")
            await self._screenshot(page, html, path, wait=1.5)
            frame_paths.append(path)

            # 3. GRAPH SLIDE
            html = self.templates["graph"].render(
                graph_label=lesson["graph_label"],
                graph_type=lesson.get("graph_type", "line"),
                graph_labels=json.dumps(lesson["graph_labels"]),
                graph_data=json.dumps(lesson["graph_data"]),
                key_points=lesson["key_points"],
                primary_color=pc, secondary_color=sc
            )
            path = os.path.join(self.output_dir, "slide_2_graph.png")
            await self._screenshot(page, html, path, wait=3.0)  # wait for chart.js
            frame_paths.append(path)

            # 4. EXAMPLE SLIDE
            html = self.templates["example"].render(
                problem_statement=lesson["problem_statement"],
                problem_question=lesson["problem_question"],
                steps=lesson["steps"],
                answer=lesson["answer"],
                primary_color=pc, secondary_color=sc
            )
            path = os.path.join(self.output_dir, "slide_3_example.png")
            await self._screenshot(page, html, path, wait=1.5)
            frame_paths.append(path)

            # 5. SUMMARY SLIDE
            html = self.templates["summary"].render(
                summary=lesson.get("concept_audio", "")[:200],
                next_topic=lesson["next_topic"],
                primary_color=pc, secondary_color=sc
            )
            path = os.path.join(self.output_dir, "slide_4_summary.png")
            await self._screenshot(page, html, path, wait=1.5)
            frame_paths.append(path)

            await browser.close()

        return frame_paths
