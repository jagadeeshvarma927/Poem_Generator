import os
import sys


# Add parent directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from dotenv import load_dotenv
from src.utils.file_utils import read_themes_from_excel
from src.story_generator.story_generator import generate_stories_from_themes
from src.image_generator.image_generator import generate_images_for_stories
from src.ppt_generator.ppt_generator import create_ppt_for_story, combine_ppts
from config.config import load_config
from streamlit_option_menu import option_menu

# Load environment variables
load_dotenv()

# Load configuration
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
        options=["Home", "Generate Stories", "View PPTs"],
        icons=["house", "pencil", "file-ppt"],
        menu_icon="cast",
        default_index=0,
    )

# Home page
if selected == "Home":
    st.title("📖 Story Generator App")
    st.write("""
    Welcome to the Story Generator App! This app automates the creation of children's stories based on themes from Indian mythology. 
    Simply upload an Excel file with story themes, and the app will generate stories, create illustrations, and compile everything into PowerPoint presentations.
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
            with st.spinner("Generating stories, images, and PPTs... This may take a few minutes."):
                # Step 1: Generate stories
                stories_dir = config['output_dirs']['stories']
                generate_stories_from_themes(file_path, stories_dir)

                # Step 2: Generate images
                images_dir = config['output_dirs']['images']
                generate_images_for_stories(stories_dir, images_dir)

                # Step 3: Create PPTs
                ppts_dir = config['output_dirs']['ppts']
                for story_file in os.listdir(stories_dir):
                    if story_file.endswith(".txt"):
                        story_path = os.path.join(stories_dir, story_file)
                        create_ppt_for_story(story_path, images_dir, ppts_dir)

                # Step 4: Combine PPTs
                combined_ppt_path = os.path.join(ppts_dir, "combined_stories.pptx")
                combine_ppts(ppts_dir, combined_ppt_path)

            st.success("Stories, images, and PPTs generated successfully!")

# View PPTs page
elif selected == "View PPTs":
    st.title("📄 View Generated PPTs")
    ppt_files = os.listdir(config['output_dirs']['ppts'])
    selected_ppt = st.selectbox("Select a PPT to download", ppt_files)

    if selected_ppt:
        ppt_path = os.path.join(config['output_dirs']['ppts'], selected_ppt)
        with open(ppt_path, "rb") as f:
            st.download_button(
                label="Download PPTX",
                data=f,
                file_name=selected_ppt,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px;">
    <p>Made with ❤️ by Jagadeesh Varma I</p>
</div>
""", unsafe_allow_html=True)