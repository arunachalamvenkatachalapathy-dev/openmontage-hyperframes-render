"""
generate_scenes.py — Generate scene images for the tech explainer video
using Vertex AI Imagen 3 (via Application Default Credentials).
"""
import os
import sys
import time
from pathlib import Path

OUTPUT_DIR = Path("projects/local-agents/assets/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Scene prompts — dark neon cyberpunk aesthetic, cinematic
SCENES = [
    {
        "file": "scene1.jpg",
        "prompt": (
            "Close-up cinematic shot of a hacker's face illuminated by a glowing laptop screen "
            "in a pitch-black room, green terminal code reflecting on their face and glasses, "
            "dramatic rim lighting, cyberpunk aesthetic, photorealistic, 4K, shallow depth of field"
        ),
    },
    {
        "file": "scene2.jpg",
        "prompt": (
            "Dramatic still life of burning US dollar bills surrounding floating holographic API key tokens "
            "and cloud service logos, dark background, orange fire glow contrasting with cool blue digital elements, "
            "cinematic lighting, photorealistic, 4K"
        ),
    },
    {
        "file": "scene3.jpg",
        "prompt": (
            "A glowing custom-built AI server rack sitting on a wooden desk in a cyberpunk room, "
            "blue and purple neon LED lighting, visible circuit boards and cooling fans, "
            "multiple monitors showing neural network visualizations in the background, "
            "photorealistic, 4K, moody atmosphere"
        ),
    },
    {
        "file": "scene4.jpg",
        "prompt": (
            "Futuristic holographic video editing interface floating in mid-air, "
            "glowing neon timeline with video frames arranged in sequence, "
            "a person's hands interacting with the holographic display, "
            "dark room with cyan and magenta accent lighting, photorealistic, 4K"
        ),
    },
    {
        "file": "scene5.jpg",
        "prompt": (
            "Split screen composition: left side showing glowing green code on a dark terminal, "
            "right side showing a cinematic rendered video frame of a futuristic city, "
            "connected by flowing neon data streams, dark background, photorealistic, 4K"
        ),
    },
    {
        "file": "scene6.jpg",
        "prompt": (
            "Epic wide-angle shot of a colossal glowing robot constructing a futuristic city "
            "at lightning speed, sparks flying, cranes and buildings rising, stormy sky with lightning, "
            "blue and gold neon accents, cinematic composition, photorealistic, 4K"
        ),
    },
]


def generate_with_vertex():
    """Generate images using Vertex AI Imagen via ADC."""
    from google import genai
    from google.genai import types

    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "exalted-shape-502013-q5")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    print(f"Initializing Vertex AI client (project={project}, location={location})...")
    client = genai.Client(vertexai=True, project=project, location=location)

    # Try multiple model names in order of preference
    model_names = [
        "imagen-3.0-generate-001",
        "imagen-3.0-fast-generate-001",
        "imagegeneration@006",
        "imagegeneration@005",
    ]

    working_model = None
    for model_name in model_names:
        print(f"  Trying model: {model_name}...")
        try:
            test_result = client.models.generate_images(
                model=model_name,
                prompt="A simple test image of a glowing blue sphere on a black background",
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="9:16",
                    output_mime_type="image/jpeg",
                ),
            )
            if test_result.generated_images:
                working_model = model_name
                # Save the test image as scene1 if it matches
                print(f"  Model {model_name} works!")
                break
            else:
                print(f"  Model {model_name} returned no images.")
        except Exception as e:
            print(f"  Model {model_name} failed: {e}")
            continue

    if not working_model:
        print("\nERROR: No Imagen model is available on your Vertex AI project.")
        print("Please ensure:")
        print("  1. The Vertex AI API is enabled in your GCP project")
        print("  2. Imagen 3 is available in your region")
        print("  3. You have sufficient quota/billing")
        sys.exit(1)

    print(f"\nUsing model: {working_model}")
    print(f"Generating {len(SCENES)} scene images...\n")

    for i, scene in enumerate(SCENES):
        filepath = OUTPUT_DIR / scene["file"]
        print(f"[{i+1}/{len(SCENES)}] Generating {scene['file']}...")
        try:
            result = client.models.generate_images(
                model=working_model,
                prompt=scene["prompt"],
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="9:16",
                    output_mime_type="image/jpeg",
                ),
            )
            if result.generated_images:
                img_bytes = result.generated_images[0].image.image_bytes
                with open(filepath, "wb") as f:
                    f.write(img_bytes)
                size_kb = len(img_bytes) / 1024
                print(f"  Saved {filepath} ({size_kb:.0f} KB)")
            else:
                print(f"  WARNING: No image returned for {scene['file']}")
        except Exception as e:
            print(f"  ERROR generating {scene['file']}: {e}")

        # Rate limit courtesy
        if i < len(SCENES) - 1:
            time.sleep(2)

    print(f"\nDone! Images saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    generate_with_vertex()
