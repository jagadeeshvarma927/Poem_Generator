import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your Gemini API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

# Configure the Gemini client
genai.configure(api_key=GOOGLE_API_KEY)

def generate_image(prompt, output_path):
    model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")
    response = model.generate_content(prompt)
    # Find the image part in the response
    for part in response.candidates[0].content.parts:
        if hasattr(part, "mime_type") and part.mime_type.startswith("image/"):
            with open(output_path, "wb") as f:
                f.write(part.inline_data.data)
            print(f"Image saved to {output_path}")
            return
    print("No image found in response.")

if __name__ == "__main__":
    prompt = "A colorful cartoon elephant playing in a sunny field, children's book illustration style"
    output_file = "sample_gemini_image.png"
    generate_image(prompt, output_file)