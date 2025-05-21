import os
import json
import logging
import file_utils

logger = logging.getLogger(__name__)

def load_json_data(file_path, create_if_not_exists=False):
    """Load data from a JSON file. Create the file and its directory if they don't exist if 'create_if_not_exists' is True."""
    
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory) and create_if_not_exists:
        os.makedirs(directory)  # Crea la cartella se non esiste
        logger.warning(f"Directory {directory} created.")
    
    if not os.path.exists(file_path):
        if create_if_not_exists:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("[]")  # Crea un file JSON vuoto
            logger.warning(f"File {file_path} not found! Created a new empty JSON file.")
        else:
            logger.warning(f"File {file_path} not found!")
            return {}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file = json.load(f)
            logger.debug(f"Successfully loaded {file_path}")
            return file
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return {}

def save_to_json_file(data, filename, output_dir=None, append=False):
    """Save data in a JSON file. Append to existing data if 'append' is True."""
    filename = file_utils.append_dir_to_file_name(file_utils.sanitize_filename(filename), output_dir)

    # If append is set to true, load existing JSON file
    if append and os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            try:
                existing_data = json.load(file)
                # Check if data are of the same type
                if isinstance(existing_data, list) and isinstance(data, list):
                    data = existing_data + data
                elif isinstance(existing_data, dict) and isinstance(data, dict):
                    existing_data.update(data)
                    data = existing_data
                else:
                    raise ValueError("Cannot append: Data types do not match.")
            except json.JSONDecodeError:
                print(f"Warning: Existing file {filename} contains invalid JSON. Overwriting.")
    
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Data saved in the file '{filename}'.")
