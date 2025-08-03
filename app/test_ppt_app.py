import os
import sys
import shutil

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
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # CSS file is optional

# Apply custom CSS
local_css("app/style.css")

# Initialize session state for tracking if directories are cleaned
if 'directories_cleaned' not in st.session_state:
    st.session_state.directories_cleaned = False

# Clean up directories only once per session
def initialize_directories():
    if not st.session_state.directories_cleaned:
        # Define output directories
        output_dirs = [
            config['output_dirs']['stories'],
            config['output_dirs']['images'],
            config['output_dirs']['ppts']
        ]
        
        # Add pdfs directory if it exists in config
        if 'pdfs' in config['output_dirs']:
            output_dirs.append(config['output_dirs']['pdfs'])
        
        # Clean and create directories
        for dir_path in output_dirs:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            os.makedirs(dir_path, exist_ok=True)
        
        st.session_state.directories_cleaned = True

# Initialize directories
initialize_directories()

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
    
    # Try to display banner image, but don't fail if it doesn't exist
    try:
        st.image("app/banner.png", use_column_width=True)
    except:
        st.info("Upload an Excel file with story themes to get started!")

# Generate Stories page
elif selected == "Generate Stories":
    st.title("🖋️ Generate Stories")
    uploaded_file = st.file_uploader("Upload an Excel file with story themes", type=["xlsx"])

    if uploaded_file is not None:
        # Ensure input directory exists
        input_dir = "data/input"
        os.makedirs(input_dir, exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join(input_dir, "themes.xlsx")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Define output directories
        stories_dir = config['output_dirs']['stories']
        images_dir = config['output_dirs']['images']
        ppts_dir = config['output_dirs']['ppts']

        # Trigger the workflow
        if st.button("Generate Stories"):
            try:
                with st.spinner("Generating stories, images, and PPTs... This may take a few minutes."):
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Step 1: Generate stories
                    status_text.text("Step 1/5: Generating stories...")
                    progress_bar.progress(20)
                    generate_stories_from_themes(file_path, stories_dir)
                    st.success("✅ Stories generated successfully!")

                    # Step 2: Generate images
                    status_text.text("Step 2/5: Generating images...")
                    progress_bar.progress(40)
                    generate_images_for_stories(stories_dir, images_dir)
                    st.success("✅ Images generated successfully!")

                    # Step 3: Create individual PPTs
                    status_text.text("Step 3/5: Creating individual PPTs...")
                    progress_bar.progress(60)
                    
                    story_files = [f for f in os.listdir(stories_dir) if f.endswith(".txt")]
                    if not story_files:
                        st.error("No story files found!")
                        st.stop()
                    
                    for story_file in story_files:
                        story_path = os.path.join(stories_dir, story_file)
                        create_ppt_for_story(story_path, images_dir, ppts_dir)
                    
                    st.success("✅ Individual PPTs created successfully!")

                    # Step 4: Combine PPTs
                    status_text.text("Step 4/5: Combining PPTs...")
                    progress_bar.progress(80)
                    combined_ppt_path = os.path.join(ppts_dir, "combined_stories.pptx")
                    combine_ppts(ppts_dir, combined_ppt_path)
                    st.success("✅ Combined PPT created successfully!")

                    # Step 5: Completion
                    status_text.text("Step 5/5: Finalizing...")
                    progress_bar.progress(100)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()

                st.success("🎉 All stories, images, and PPTs generated successfully!")
                
                # Show summary
                st.info(f"""
                **Generation Summary:**
                - Stories created: {len([f for f in os.listdir(stories_dir) if f.endswith('.txt')])}
                - Images created: {len([f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])}
                - PPT files created: {len([f for f in os.listdir(ppts_dir) if f.endswith('.pptx')])}
                """)
                
            except Exception as e:
                st.error(f"An error occurred during generation: {str(e)}")
                st.error("Please check your input file and try again.")

# View PPTs page
elif selected == "View PPTs":
    st.title("📄 View Generated PPTs")
    
    ppts_dir = config['output_dirs']['ppts']
    
    # Check if PPT directory exists and has files
    if not os.path.exists(ppts_dir):
        st.warning("No PPT directory found. Please generate stories first.")
    else:
        ppt_files = [f for f in os.listdir(ppts_dir) if f.endswith('.pptx')]
        
        if not ppt_files:
            st.warning("No PPT files found. Please generate stories first.")
        else:
            st.success(f"Found {len(ppt_files)} PPT file(s)")
            
            selected_ppt = st.selectbox("Select a PPT to download", ppt_files)

            if selected_ppt:
                ppt_path = os.path.join(ppts_dir, selected_ppt)
                
                # Show file info
                file_size = os.path.getsize(ppt_path) / (1024 * 1024)  # Size in MB
                st.info(f"File size: {file_size:.2f} MB")
                
                # Download button
                with open(ppt_path, "rb") as f:
                    st.download_button(
                        label=f"📥 Download {selected_ppt}",
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