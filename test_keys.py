import asyncio
import os
from src.story_engine import StoryEngine
from src.image_engine import ImageEngine
from dotenv import load_dotenv

load_dotenv()

async def test_keys():
    print("--- Testing MiniMax API (Story) ---")
    try:
        se = StoryEngine()
        story = se.generate_story("A futuristic city made of glass")
        if story:
            print("✅ Story Engine is working!")
            print(f"Title: {story['title']}")
            
            print("\n--- Testing Hugging Face API (Image) ---")
            ie = ImageEngine()
            # Test first scene prompt
            prompt = story['scenes'][0]['image_prompt']
            success = ie.generate_image(prompt, "test_image_keys.png")
            if success:
                print("✅ Image Engine is working!")
                print("Test image saved as 'test_image_keys.png'")
            else:
                print("❌ Image Engine failed.")
        else:
            print("❌ Story Engine failed (No output).")
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_keys())
