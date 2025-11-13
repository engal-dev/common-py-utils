import os
import json
import logging
import file_utils
import csv

logger = logging.getLogger(__name__)

def initialize_file(file_path, fields):
    """Initialize a csv file."""
    
    directory = os.path.dirname(file_path)
    # Crea la cartella se non esiste
    if not os.path.exists(directory):
        os.makedirs(directory)  
        logger.warning(f"Directory {directory} created.")
    
    file = open(file_path, "w", newline='', encoding="utf-8")
    
    writer = csv.DictWriter(file, fieldnames=fields)
    
    writer.writeheader()
    file.flush()
    
    return file_path, file, writer