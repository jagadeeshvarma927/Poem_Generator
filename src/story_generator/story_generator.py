import os
import google.generativeai as genai
from src.utils.file_utils import read_themes_from_excel, write_story_to_txt
from dotenv import load_dotenv
load_dotenv()

# Load API key from environment variable
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

# Configure Gemini LLM
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-pro')  # Use Gemini Pro for text generation

def generate_story(theme, target_age="5-12", word_count=200):
    """
    Generates a story based on the given theme using Gemini LLM.

    Args:
        theme (str): The story theme.
        target_age (str): Target age group (default: "5-12").
        word_count (int): Desired word count for the story (default: 200).

    Returns:
        str: Generated story text.
    """
    prompt = f"""
    Generate a short, engaging story for children aged {target_age} based on the following theme:
    Theme: {theme}
    The story should be simple, easy to understand, and around {word_count} words.
    Include a moral or lesson at the end. Use Indian mythological elements from Ramayana or Mahabharata.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating story for theme '{theme}': {e}")
        return ""

def generate_stories_from_themes(input_file, output_dir, target_age="5-12", word_count=200):
    """
    Generates stories for all themes in the input Excel file and saves them as text files.

    Args:
        input_file (str): Path to the Excel file containing themes.
        output_dir (str): Directory to save the generated stories.
        target_age (str): Target age group (default: "5-12").
        word_count (int): Desired word count for each story (default: 200).
    """
    themes = read_themes_from_excel(input_file)
    print(f"Found {len(themes)} themes in the Excel file.")
    if not themes:
        print("No themes found in the Excel file.")
        return

    for i, theme in enumerate(themes, start=1):
        print(f"Generating story for theme {i}: {theme}")
        story = generate_story(theme, target_age, word_count)
        if story:
            filename = f"story_{i}_{theme.replace(' ', '_').lower()}.txt"
            write_story_to_txt(story, output_dir, filename)

if __name__ == "__main__":
    # Paths and parameters
    input_file = 'data/input/peom_themes.xlsx'
    output_dir = 'data/output/stories'
    target_age = "5-12"
    word_count = 300

    # Generate stories
    generate_stories_from_themes(input_file, output_dir, target_age, word_count)
