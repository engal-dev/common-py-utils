import os
import logging
import time
from datetime import datetime, timedelta
import file_utils, json_utils, log_utils

logger = log_utils.setup_logging(os.path.basename(__file__), logging.DEBUG)

# File input/output
FIRST_JSON = "navidrome-playlists/Brani preferiti 20250516.json"
SECOND_JSON = "navidrome-playlists/Brani preferiti.json"

REPORT_DIR = "compare_report"

FOUND_FROM_FIRST_FILE = "found_from_first_file.json"
FOUND_FROM_FIRST_FILE_LOG = "found_from_first_file.log"
FOUND_FROM_SECOND_FILE = "found_from_second_file.json"
FOUND_FROM_SECOND_FILE_LOG = "found_from_second_file.log"

ONLY_IN_FIRST_FILE = "only_in_first_file.json"
ONLY_IN_SECOND_FILE = "only_in_second_file.json"
ONLY_IN_FIRST_FILE_LOG = "only_in_first_file.log"
ONLY_IN_SECOND_FILE_LOG = "only_in_second_file.log"

def compare_json(first_json, second_json):
    """Compare elements of json files."""
    found_from_first_file = []
    found_from_second_file = []

    only_in_first_file = []
    only_in_second_file = []

    for first_item in first_json:
        found_match = False
        for second_item in second_json:
            # Confronta tutti i campi dell'oggetto
            if first_item["id"] == second_item["id"]:
                found_from_first_file.append(first_item)
                found_match = True
                break
        
        if not found_match:
            only_in_first_file.append(first_item)

    for second_item in second_json:
        found_match = False
        for first_item in first_json:
            if second_item["id"] == first_item["id"]:
                found_from_second_file.append(second_item)
                found_match = True
                break
        
        if not found_match:
            only_in_second_file.append(second_item)

    return found_from_first_file, found_from_second_file, only_in_first_file, only_in_second_file

def save_list(data, file_path, output_dir=None):
    """Save a list of items in a text file."""
    file_path = file_utils.append_dir_to_file_name(file_path, output_dir)

    with open(file_path, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(
                f"{entry['title']}, {entry['artist']}, {entry['album']}\n"
            )

def main():
    # Load data
    first_json = json_utils.load_json_data(FIRST_JSON)
    second_json = json_utils.load_json_data(SECOND_JSON)

    # Compare files content
    found_from_first_file, found_from_second_file, only_in_first_file, only_in_second_file = compare_json(first_json, second_json)

    # Save report
    if found_from_first_file:
        json_utils.save_to_json_file(found_from_first_file, FOUND_FROM_FIRST_FILE, REPORT_DIR, append=True)
        save_list(found_from_first_file, FOUND_FROM_FIRST_FILE_LOG, output_dir=REPORT_DIR)
    if found_from_second_file:
        json_utils.save_to_json_file(found_from_second_file, FOUND_FROM_SECOND_FILE, REPORT_DIR, append=True)
        save_list(found_from_second_file, FOUND_FROM_SECOND_FILE_LOG, output_dir=REPORT_DIR)
    if only_in_first_file:
        json_utils.save_to_json_file(only_in_first_file, ONLY_IN_FIRST_FILE, REPORT_DIR)
        save_list(only_in_first_file, ONLY_IN_FIRST_FILE_LOG, output_dir=REPORT_DIR)
    if only_in_second_file:
        json_utils.save_to_json_file(only_in_second_file, ONLY_IN_SECOND_FILE, REPORT_DIR)
        save_list(only_in_second_file, ONLY_IN_SECOND_FILE_LOG, output_dir=REPORT_DIR)
    
    logger.info(f"{len(found_from_first_file)} items found from first file. Report in {FOUND_FROM_FIRST_FILE} - {FOUND_FROM_FIRST_FILE_LOG}.")
    logger.info(f"{len(found_from_second_file)} items found from second file. Report in {FOUND_FROM_SECOND_FILE} - {FOUND_FROM_SECOND_FILE_LOG}.")
    logger.info(f"{len(only_in_first_file)} items not found in the second file. Report in {ONLY_IN_FIRST_FILE} - {ONLY_IN_FIRST_FILE_LOG}.")
    logger.info(f"{len(only_in_second_file)} items not found in the first file. Report in {ONLY_IN_SECOND_FILE} - {ONLY_IN_SECOND_FILE_LOG}.")

if __name__ == "__main__":
    start_time = time.time()
    start_datetime = datetime.now()
    
    logger.info(f"🚀 Start time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    main()

    end_time = time.time()
    end_datetime = datetime.now()
    duration = timedelta(seconds=int(end_time - start_time))
    
    # Converti la durata in ore, minuti e secondi
    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60
    seconds = duration.seconds % 60
    
    logger.info(f"✅ End time: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"⏱️ Duration: {hours} hours, {minutes} minutes, {seconds} seconds")
