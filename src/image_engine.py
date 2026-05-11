import os
import time
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

class ImageEngine:
    def __init__(self, token=None):
        self.token = token or os.getenv("HF_TOKEN")
        if not self.token:
            raise ValueError("HF_TOKEN not found in environment variables.")
        
        # New InferenceClient is the recommended way to use HF APIs in 2025
        self.client = InferenceClient(api_key=self.token)
        
        # List of models to try in order of preference
        self.models = [
            "black-forest-labs/FLUX.1-schnell",
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5"
        ]

    def generate_image(self, prompt, filename, model_index=0):
        if model_index >= len(self.models):
            print("All models failed for this prompt.")
            return False

        model_id = self.models[model_index]
        print(f"Generating image using {model_id} via InferenceClient...")
        
        try:
            # Using the specific task method for text-to-image
            image = self.client.text_to_image(prompt, model=model_id)
            image.save(filename)
            return True
                
        except Exception as e:
            print(f"Error from {model_id}: {e}")
            if "503" in str(e) or "loading" in str(e).lower():
                print(f"Model {model_id} is loading. Waiting 20 seconds...")
                time.sleep(20)
                return self.generate_image(prompt, filename, model_index)
            else:
                # Try next model
                return self.generate_image(prompt, filename, model_index + 1)

if __name__ == "__main__":
    # Test run
    try:
        engine = ImageEngine()
        success = engine.generate_image("a cute robot eating a pizza, cinematic lighting", "test_robot.png")
        if success:
            print("Image generated successfully!")
    except Exception as e:
        print(f"Test failed: {e}")
