import logging
import time
from typing import Optional
import requests

logger = logging.getLogger(__name__)

def make_api_request(url: str, method: str = "get", **kwargs) -> Optional[requests.Response]:
    """
    Make an API request with retry logic.
    
    Args:
        url (str): The URL to make the request to
        method (str): HTTP method (get or post)
        **kwargs: Additional arguments to pass to requests
        
    Returns:
        Optional[requests.Response]: The response object if successful, None otherwise
    """
    max_retries = 3
    timeout = 30  # Timeout in seconds
    
    # Add timeout to kwargs if not present
    if 'timeout' not in kwargs:
        kwargs['timeout'] = timeout
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Making {method.upper()} request to {url}")
            logger.debug(f"Request parameters: {kwargs}")
            
            if method.lower() == "get":
                response = requests.get(url, **kwargs)
            else:
                response = requests.post(url, **kwargs)
                
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout:
            logger.warning(f"Request timed out (attempt {attempt+1}/{max_retries})")
            if attempt == max_retries - 1:
                logger.error(f"Request failed after {max_retries} attempts due to timeout")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                logger.error(f"Request failed after {max_retries} attempts due to connection error")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"API request failed (attempt {attempt+1}/{max_retries}): {str(e)}")
            if hasattr(e.response, 'text'):
                logger.warning(f"Response text: {e.response.text}")
            if attempt == max_retries - 1:
                logger.error(f"API request failed after {max_retries} attempts: {str(e)}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff