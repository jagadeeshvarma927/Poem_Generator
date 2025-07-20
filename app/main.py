import sys
import os
print("Original PYTHONPATH:", sys.path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from dotenv import load_dotenv
from src.utils.file_utils import read_themes_from_excel
from src.story_generator.story_generator import generate_stories_from_themes
from src.image_generator.image_generator import generate_images_for_stories
from src.pdf_generator.pdf_generator import create_pdfs_for_all_stories
from config.config import load_config
from streamlit_option_menu import option_menu
from PyPDF2 import PdfReader
import base64

# Load environment variables
load_dotenv()

# Load configuration
# config = load_config('config/config.yaml')
config = load_config('config/config.yml')

# Streamlit UI Configuration
st.set_page_config(
    page_title="Story Generator App",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("app/style.css")  # Add custom CSS if needed

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Generate Stories", "View PDFs"],
        icons=["house", "pencil", "file-earmark-pdf"],
        menu_icon="cast",
        default_index=0,
    )

# Home page
if selected == "Home":
    st.title("📖 Story Generator App")
    st.write("""
    Welcome to the Story Generator App! This app automates the creation of children's stories based on themes from Indian mythology.
    Simply upload an Excel file with story themes, and the app will generate stories, create illustrations, and compile everything into PDFs.
    """)
    st.image("app/banner.png", use_column_width=True)  # Add a banner image

# Generate Stories page
elif selected == "Generate Stories":
    st.title("🖋️ Generate Stories")
    uploaded_file = st.file_uploader("Upload an Excel file with story themes", type=["xlsx"])

    if uploaded_file is not None:
        # Save the uploaded file
        file_path = os.path.join("data/input", "themes.xlsx")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Trigger the workflow
        if st.button("Generate Stories"):
            with st.spinner("Generating stories, images, and PDFs... This may take a few minutes."):
                # Step 1: Generate stories
                stories_dir = config['output_dirs']['stories']
                generate_stories_from_themes(file_path, stories_dir)

                # Step 2: Generate images
                images_dir = config['output_dirs']['images']
                generate_images_for_stories(stories_dir, images_dir)

                # Step 3: Create PDFs
                pdfs_dir = config['output_dirs']['pdfs']
                create_pdfs_for_all_stories(stories_dir, images_dir, pdfs_dir)

            st.success("Stories, images, and PDFs generated successfully!")


# View PDFs page
elif selected == "View PDFs":
    st.title("📄 View Generated PDFs")
    # Use absolute path for the pdfs directory
    pdf_dir = os.path.abspath(config['output_dirs']['pdfs'])
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_files = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])

    if not pdf_files:
        st.info("No PDFs found. Please generate stories first.")
    else:
        selected_pdf = st.selectbox("Select a PDF to view", pdf_files)
        if selected_pdf:
            pdf_path = os.path.join(pdf_dir, selected_pdf)
            with open(pdf_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            pdf_display = f"""
                <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>
            """
            st.markdown(pdf_display, unsafe_allow_html=True)
            st.download_button("Download PDF", data=open(pdf_path, "rb").read(), file_name=selected_pdf)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px;">
    <p>Made with ❤️ by Jagadeesh Varma I</p>
</div>
""", unsafe_allow_html=True)
