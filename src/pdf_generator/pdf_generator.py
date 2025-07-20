import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from src.utils.file_utils import ensure_output_dir

def add_text_to_pdf(story, flow):
    """
    Adds formatted text to the PDF.

    Args:
        story (str): The story text to add.
        flow (list): The list of elements to be added to the PDF.
    """
    styles = getSampleStyleSheet()
    paragraphs = story.split('\n\n')  # Split into paragraphs
    for paragraph in paragraphs:
        flow.append(Paragraph(paragraph, styles['Normal']))
        flow.append(Spacer(1, 12))  # Add spacing between paragraphs

def add_image_to_pdf(image_path, flow, width=400, height=300):
    """
    Adds an image to the PDF.

    Args:
        image_path (str): Path to the image file.
        flow (list): The list of elements to be added to the PDF.
        width (int): Width of the image in the PDF.
        height (int): Height of the image in the PDF.
    """
    if os.path.exists(image_path):
        flow.append(Image(image_path, width=width, height=height))
        flow.append(Spacer(1, 12))  # Add spacing after the image
    else:
        print(f"Image not found: {image_path}")

def create_pdf_for_story(story_path, images_dir, output_dir):
    """
    Creates a PDF for a single story, including text and images.

    Args:
        story_path (str): Path to the story text file.
        images_dir (str): Directory containing images for the story.
        output_dir (str): Directory to save the generated PDF.
    """
    ensure_output_dir(output_dir)

    # Extract story name from file path
    story_name = os.path.splitext(os.path.basename(story_path))[0]
    pdf_filename = f"{story_name}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    # Create PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    flow = []

    # Add story text to PDF
    with open(story_path, 'r', encoding='utf-8') as file:
        story = file.read()
        add_text_to_pdf(story, flow)

    # Add images to PDF
    image_prefix = os.path.splitext(story_name)[0]
    for i in range(1, 3):  # Assuming 1-2 images per story
        image_filename = f"{image_prefix}_image_{i}.png"
        image_path = os.path.join(images_dir, image_filename)
        if os.path.exists(image_path):
            add_image_to_pdf(image_path, flow)

    # Build PDF
    doc.build(flow)
    print(f"PDF created: {pdf_path}")

def create_pdfs_for_all_stories(stories_dir, images_dir, output_dir):
    """
    Creates PDFs for all stories in the stories directory.

    Args:
        stories_dir (str): Directory containing story text files.
        images_dir (str): Directory containing images for the stories.
        output_dir (str): Directory to save the generated PDFs.
    """
    ensure_output_dir(output_dir)

    for filename in os.listdir(stories_dir):
        if filename.endswith('.txt'):
            story_path = os.path.join(stories_dir, filename)
            create_pdf_for_story(story_path, images_dir, output_dir)

if __name__ == "__main__":
    # Paths and parameters
    stories_dir = 'data/output/stories'
    images_dir = 'data/output/images'
    pdfs_dir = 'data/output/pdfs'

    # Create PDFs for all stories
    create_pdfs_for_all_stories(stories_dir, images_dir, pdfs_dir)
