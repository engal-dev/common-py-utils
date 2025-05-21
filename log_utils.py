import os
import logging
from datetime import datetime

def setup_logging(logFilePrefix, loggingLevel=logging.INFO):
    """
    Sets up logging configuration for the application.
    
    Creates a logs directory and configures logging to output both to a timestamped log file
    and the console. The log file name includes the current timestamp.
    
    Args:
        logFilePrefix: String prefix to use in the log filename
        loggingLevel: Logging level to use (default: logging.INFO)
    
    Returns:
        logger: A configured logging.Logger instance ready for use
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/{logFilePrefix}_{timestamp}.log"
    
    # Configure logging to both file and console
    logging.basicConfig(
        level=loggingLevel,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Log file created at: {log_file}")
    return logger