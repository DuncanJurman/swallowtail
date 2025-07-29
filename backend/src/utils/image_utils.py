"""Utilities for handling images in CrewAI agents."""

import base64
from pathlib import Path
from typing import Optional
import mimetypes


def convert_local_image_to_data_url(image_path: str) -> Optional[str]:
    """
    Convert a local image file to a data URL that can be processed by LLMs.
    
    Args:
        image_path: Path to the local image file
        
    Returns:
        Data URL string or None if conversion fails
    """
    try:
        path = Path(image_path)
        
        # Check if file exists
        if not path.exists():
            print(f"Image file not found: {image_path}")
            return None
            
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type or not mime_type.startswith('image/'):
            mime_type = 'image/jpeg'  # Default fallback
            
        # Read and encode the image
        with open(path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        # Create data URL
        data_url = f"data:{mime_type};base64,{encoded_string}"
        
        return data_url
        
    except Exception as e:
        print(f"Error converting image to data URL: {e}")
        return None


def process_image_url(url: str) -> str:
    """
    Process an image URL, converting local file:// URLs to data URLs.
    
    Args:
        url: The image URL (can be http://, https://, file://, or local path)
        
    Returns:
        Processed URL suitable for LLM consumption
    """
    # Handle file:// URLs
    if url.startswith('file://'):
        # Extract the path from file:// URL
        local_path = url.replace('file://', '')
        data_url = convert_local_image_to_data_url(local_path)
        return data_url if data_url else url
        
    # Handle absolute local paths
    elif url.startswith('/') or (len(url) > 1 and url[1] == ':'):  # Unix or Windows absolute path
        data_url = convert_local_image_to_data_url(url)
        return data_url if data_url else url
        
    # Return URLs unchanged (http://, https://, data:, etc.)
    else:
        return url