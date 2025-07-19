import pandas as pd
import os

# Ensure the 'output' directory exists
def ensure_output_dir(output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

# Read themes from an Excel file
def read_themes_from_excel(file_path):
    """
    Reads story themes from an Excel file.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        list: List of themes.
    """
    try:
        df = pd.read_excel(file_path)
        themes = df['Theme'].tolist()  # Assuming 'Theme' is the column name
        return themes
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

# Write a story to a text file
def write_story_to_txt(story, output_path, filename):
    """
    Writes a generated story to a text file.

    Args:
        story (str): The story text.
        output_path (str): Path to the output directory.
        filename (str): Name of the output file (e.g., 'story1.txt').
    """
    ensure_output_dir(output_path)
    file_path = os.path.join(output_path, filename)
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(story)
        print(f"Story saved to {file_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")

# Write themes to a new Excel file (optional, for debugging)
def write_themes_to_excel(themes, output_path, filename):
    """
    Writes a list of themes to a new Excel file.

    Args:
        themes (list): List of themes.
        output_path (str): Path to the output directory.
        filename (str): Name of the output file (e.g., 'generated_themes.xlsx').
    """
    ensure_output_dir(output_path)
    file_path = os.path.join(output_path, filename)
    try:
        df = pd.DataFrame(themes, columns=['Theme'])
        df.to_excel(file_path, index=False)
        print(f"Themes saved to {file_path}")
    except Exception as e:
        print(f"Error writing to Excel file: {e}")


################## Test the utility functions ##################
# from file_utils import read_themes_from_excel

# # Path to the Excel file containing themes
# excel_file_path = 'data/input/peom_themes.xlsx'

# # Read themes from the Excel file
# themes = read_themes_from_excel(excel_file_path)

# # Print the themes to verify
# if themes:
#     print("Themes read from Excel file:")
#     for i, theme in enumerate(themes, start=1):
#         print(f"{i}. {theme}")
# else:
#     print("No themes found or an error occurred.")
