import sys
import os
import time
from datetime import datetime, timedelta
import json_utils, log_utils

logger = log_utils.setup_logging(os.path.basename(__file__))

# File input/output
INPUT_FOLDER = "navidrome-playlists"
INPUT_JSON = "manual-add.json"
OUTPUT_JSON = "reversed_"+INPUT_JSON

def reverse_json(json_data):
    """Inverte l'ordine degli elementi in una lista JSON."""
    return list(reversed(json_data))

def main():
    input_path = os.path.join(INPUT_FOLDER, INPUT_JSON)
    output_path = os.path.join(INPUT_FOLDER, OUTPUT_JSON)
    
    input_json = json_utils.load_json_data(input_path)
    reversed_json = reverse_json(input_json)
    json_utils.save_to_json_file(reversed_json, OUTPUT_JSON, INPUT_FOLDER)
    
    logger.info(f"Reversed JSON file saved in {output_path}")
    logger.info(f"Number of processed element: {len(reversed_json)}")

if __name__ == "__main__":
    start_time = time.time()
    start_datetime = datetime.now()
    
    logger.info(f"🚀 Ora inizio: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    main()

    end_time = time.time()
    end_datetime = datetime.now()
    duration = timedelta(seconds=int(end_time - start_time))
    
    # Converti la durata in ore, minuti e secondi
    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60
    seconds = duration.seconds % 60
    
    logger.info(f"✅ Ora fine: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"⏱️ Durata: {hours} ore, {minutes} minuti, {seconds} secondi")