import os
import re

def append_dir_to_file_name(filename, output_dir=None):
    """Append dir to file name and eventually create directory if not exist."""
    if output_dir:  # None/empty string check
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{filename}")
    return filename

def sanitize_filename(name):
    """Clean a filename from not allowed char. (for Windows)"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

##############################
### READ FILE UTILS
##############################

def load_set_from_file(file_path):
    """Load a set from a file's rows."""
    with open(file_path, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())

##############################
### WRITE FILE UTILS
##############################

def save_row_to_text_file(row, filename, output_dir=None):
    """Save row in a text file."""
    filename = sanitize_filename(append_dir_to_file_name(filename, output_dir))

    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{row}\n")

    print(f"Data saved in the file '{filename}'.")
