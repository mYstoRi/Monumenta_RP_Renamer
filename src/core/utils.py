"""Utility functions for the resource pack renamer."""

from pathlib import Path
from typing import Any
import re
import logging

logger = logging.getLogger(__name__)


def reduce_name(name: str) -> str:
    """
    Convert an item name into a file-system compatible format.
    
    Rules:
    1. a-z, 0-9, _ -> unchanged
    2. Capital letters -> lowercase
    3. Space or - -> _
    4. é -> e
    5. ', $, or other signs -> removed
    6. Multiple consecutive _ -> single _
    
    Args:
        name: The original item name (e.g., "Korbaran Shortbow")
        
    Returns:
        Reduced name suitable for filenames (e.g., "korbaran_shortbow")
    """
    output = []
    
    for char in name:
        if char.isalnum():
            output.append(char.lower())
        elif char in (' ', '-'):
            # Only add underscore if the last char wasn't already underscore
            if output and output[-1] != '_':
                output.append('_')
        elif char == 'é':
            output.append('e')
        # All other characters are ignored (', $, etc.)
    
    result = ''.join(output)
    
    # Remove trailing underscores
    result = result.rstrip('_')
    
    return result


def parse_properties(path: Path) -> dict[str, str]:
    """
    Parse a .properties file into a dictionary.
    
    Args:
        path: Path to the .properties file
        
    Returns:
        Dictionary of property key-value pairs
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    properties: dict[str, str] = {}
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Split on first = only
                if '=' in line:
                    key, value = line.split('=', 1)
                    properties[key.strip()] = value.strip()
                else:
                    logger.warning(f"Line {line_num} in {path} has no '=': {line}")
                    
    except UnicodeDecodeError:
        # Try with latin-1 encoding as fallback
        with open(path, 'r', encoding='latin-1') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    properties[key.strip()] = value.strip()
    
    return properties


def get_base_item(properties: dict[str, str]) -> str | None:
    """
    Extract the base item type from properties.
    
    Handles both 'items' and 'matchItems' keys.
    
    Args:
        properties: Parsed properties dictionary
        
    Returns:
        Base item string (e.g., "bow", "leather_helmet") or None
    """
    return properties.get('matchItems') or properties.get('items')


def get_display_name(properties: dict[str, str]) -> str | None:
    """
    Extract the display name from properties.
    
    Args:
        properties: Parsed properties dictionary
        
    Returns:
        Display name string or None
    """
    return properties.get('nbt.plain.display.Name')


def is_replica(properties: dict[str, str]) -> bool:
    """
    Check if the item is a replica based on its display name.
    
    Args:
        properties: Parsed properties dictionary
        
    Returns:
        True if the item name starts with "Replica "
    """
    name = get_display_name(properties)
    return name is not None and name.startswith("Replica ")


def get_item_name(properties: dict[str, str]) -> str | None:
    """
    Get the item name without the "Replica " prefix if present.
    
    Args:
        properties: Parsed properties dictionary
        
    Returns:
        Clean item name or None
    """
    name = get_display_name(properties)
    if name is None:
        return None
    
    if name.startswith("Replica "):
        return name[8:]  # Remove "Replica " prefix
    return name


def find_emissive(base_path: Path) -> Path | None:
    """
    Find the emissive texture file for a given base texture.
    
    Args:
        base_path: Path to the base .png file
        
    Returns:
        Path to the _e.png file if it exists, None otherwise
    """
    emissive_path = base_path.with_name(base_path.stem + "_e.png")
    return emissive_path if emissive_path.exists() else None


def find_mcmeta(texture_path: Path) -> Path | None:
    """
    Find the .mcmeta animation file for a given texture.
    
    Args:
        texture_path: Path to the .png file
        
    Returns:
        Path to the .png.mcmeta file if it exists, None otherwise
    """
    mcmeta_path = texture_path.with_suffix('.png.mcmeta')
    return mcmeta_path if mcmeta_path.exists() else None
