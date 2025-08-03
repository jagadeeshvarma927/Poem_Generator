import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.file_utils import ensure_output_dir
from src.utils.file_utils import ensure_output_dir
from PIL import Image
import google.generativeai as genai
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables at the start.
load_dotenv()

# Load HF_TOKEN from environment variable
HF_TOKEN = os.getenv('HF_TOKEN')
if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set.")

# Configure the HuggingFace Inference Client
client = InferenceClient(
    provider="replicate",
    api_key=HF_TOKEN,
)

def generate_image_from_text(prompt, output_path, filename):
    """
    Generates an image based on the given text prompt using Gemini's image generation model.

    Args:
        prompt (str): Text prompt for image generation.
        output_path (str): Directory to save the generated image.
        filename (str): Name of the output image file (e.g., 'image.png').

    Returns:
        str: Path to the saved image file or None on failure.
    """
    ensure_output_dir(output_path)
    file_path = os.path.join(output_path, filename)

    # Use HuggingFace InferenceClient to generate image
    model_name = "stabilityai/stable-diffusion-3.5-large"
    print(f"Using model: {model_name}")

    try:
        image = client.text_to_image(
            prompt,
            model=model_name,
        )
        image.save(file_path)
        # Verify that the saved file is a valid image.
        Image.open(file_path).verify()
        print(f"Image successfully saved to {file_path}")
        return file_path
    except Exception as e:
        print(f"An error occurred during image generation with {model_name}: {e}")
        return None

def generate_enhanced_prompt(story_text):
    """
    Creates an enhanced prompt for better image generation using a text model.
    
    Args:
        story_text (str): The story text to create a prompt from.
    
    Returns:
        str: An enhanced prompt for image generation.
    """
    # Using a capable text model to generate a descriptive prompt.
    text_model = genai.GenerativeModel('models/gemini-2.5-pro')
    
    enhancement_prompt = f"""
    Based on this children's story excerpt, create a detailed and vivid visual description for an image generation model. The description should be a single paragraph and include details about the characters, their appearance, the setting, colors, mood, and a child-friendly art style like 'storybook illustration' or 'cartoon'.

    Story: "{story_text[:500]}..."
    """
    
    try:
        response = text_model.generate_content(enhancement_prompt)
        # It's good practice to access the text from the parts of the response.
        if response.parts:
            return response.parts[0].text.strip()
        return f"A colorful and child-friendly illustration of a scene from the story: {story_text[:200]}..."
    except Exception as e:
        print(f"Error enhancing prompt: {e}")
        return f"A colorful and child-friendly illustration of a scene from the story: {story_text[:200]}..."

def generate_images_for_stories(stories_dir, output_dir, image_per_story=1):
    """
    Generates images for stories saved in the stories directory.

    Args:
        stories_dir (str): Directory containing story text files.
        output_dir (str): Directory to save the generated images.
        image_per_story (int): Number of images to generate per story.
    """
    ensure_output_dir(output_dir)

    for filename in os.listdir(stories_dir):
        if filename.endswith('.txt'):
            story_path = os.path.join(stories_dir, filename)
            
            try:
                with open(story_path, 'r', encoding='utf-8') as file:
                    story = file.read()
            except Exception as e:
                print(f"Error reading story file {filename}: {e}")
                continue

            print(f"Processing story: {filename}")
            enhanced_prompt = generate_enhanced_prompt(story)
            print(f"Generated prompt: {enhanced_prompt[:150]}...")

            for i in range(image_per_story):
                image_filename = f"{os.path.splitext(filename)[0]}_image_{i+1}.png"
                result = generate_image_from_text(enhanced_prompt, output_dir, image_filename)
                
                if result:
                    print(f"✓ Successfully generated image: {image_filename}")
                else:
                    print(f"✗ Failed to generate image for {filename}")

def test_image_generation():
    """
    Test function to verify image generation is working.
    """
    test_prompt = "A friendly cartoon dragon reading a book in a cozy, magical library filled with colorful books. The style should be that of a children's storybook illustration."
    test_output = "test_output"
    test_filename = "test_image.png"
    
    print("--- Testing Image Generation ---")
    result = generate_image_from_text(test_prompt, test_output, test_filename)
    
    if result:
        print("✓ Image generation test successful!")
    else:
        print("✗ Image generation test failed.")
    print("-----------------------------")
    return bool(result)

def list_available_models():
    """
    Lists available generative models to aid in debugging.
    """
    print("--- Available Generative Models ---")
    try:
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(model.name)
    except Exception as e:
        print(f"Could not list available models: {e}")
    print("-----------------------------------")


if __name__ == "__main__":
    # It's helpful to see which models are available, especially when troubleshooting.
    list_available_models()
    pass
    
    # if test_image_generation():
    #     stories_dir = 'data/output/stories'
    #     images_dir = 'data/output/images'
        
    #     if not os.path.exists(stories_dir):
    #         print(f"Stories directory not found at '{stories_dir}'. Skipping image generation for stories.")
    #     else:
    #         print(f"\nGenerating images for stories in {stories_dir}...")
    #         generate_images_for_stories(stories_dir, images_dir)
    #         print("\nImage generation for stories completed!")