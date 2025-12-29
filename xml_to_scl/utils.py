"""
Utility functions for XML to SCL parser
"""

import re
import logging
from pathlib import Path
from typing import Optional, List
import xml.etree.ElementTree as ET

try:
    from .config import NAMESPACES, SCL_RESERVED_KEYWORDS, config
except ImportError:
    from config import NAMESPACES, SCL_RESERVED_KEYWORDS, config

logger = logging.getLogger(__name__)


def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def escape_scl_identifier(name: str) -> str:
    """
    Escape SCL identifier if it's a reserved keyword or contains special characters.
    
    Args:
        name: Identifier name
        
    Returns:
        Escaped identifier with quotes if needed
    """
    if not name:
        return '""'
    
    # Check if it's a reserved keyword
    if name.upper() in SCL_RESERVED_KEYWORDS:
        return f'"{name}"'
    
    # Check if it contains special characters (already quoted)
    if name.startswith('"') and name.endswith('"'):
        return name
    
    # Check if it needs quoting (contains spaces or special chars)
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        return f'"{name}"'
    
    return name


def parse_array_datatype(datatype: str) -> tuple[str, Optional[str]]:
    """
    Parse array datatype string.
    
    Args:
        datatype: Datatype string like "Array[1..10] of Int"
        
    Returns:
        Tuple of (base_type, array_bounds) or (datatype, None) if not an array
    """
    array_match = re.match(r'Array\s*\[(.+?)\]\s*of\s+(.+)', datatype, re.IGNORECASE)
    if array_match:
        bounds = array_match.group(1)
        base_type = array_match.group(2)
        return base_type, bounds
    return datatype, None


def extract_multilingual_text(element: ET.Element, language: Optional[str] = None) -> str:
    """
    Extract text from multilingual text element.
    
    Args:
        element: XML element containing MultilingualText
        language: Language code (e.g., 'en-US'). If None, uses config default
        
    Returns:
        Extracted text or empty string
    """
    if element is None:
        return ""
    
    if language is None:
        language = config.language
    
    # Find MultilingualTextItem with matching culture
    for item in element.findall('.//MultilingualTextItem'):
        culture_elem = item.find('AttributeList/Culture')
        text_elem = item.find('AttributeList/Text')
        
        if culture_elem is not None and culture_elem.text == language:
            if text_elem is not None and text_elem.text:
                return text_elem.text
    
    # Fallback: return first non-empty text
    for item in element.findall('.//MultilingualTextItem'):
        text_elem = item.find('AttributeList/Text')
        if text_elem is not None and text_elem.text:
            return text_elem.text
    
    return ""


def format_scl_comment(comment: str, indent_level: int = 0) -> str:
    """
    Format a comment for SCL code.
    
    Args:
        comment: Comment text
        indent_level: Indentation level
        
    Returns:
        Formatted SCL comment
    """
    if not comment:
        return ""
    
    indent = config.indent * indent_level
    
    # Single line comment
    if '\n' not in comment:
        return f"{indent}// {comment}"
    
    # Multi-line comment
    lines = comment.split('\n')
    formatted_lines = [f"{indent}// {line.strip()}" for line in lines if line.strip()]
    return '\n'.join(formatted_lines)


def format_scl_value(value: str, datatype: str) -> str:
    """
    Format a value for SCL initialization.
    
    Args:
        value: Value to format
        datatype: Datatype of the value
        
    Returns:
        Formatted value
    """
    if not value:
        return ""
    
    # Boolean values
    if datatype.lower() == 'bool':
        return value.upper()  # TRUE or FALSE
    
    # String values
    if 'string' in datatype.lower():
        if not value.startswith("'"):
            return f"'{value}'"
        return value
    
    # Time values
    if datatype.lower() in ['time', 'ltime']:
        if not value.upper().startswith('T#') and not value.upper().startswith('TIME#'):
            return f"T#{value}"
        return value
    
    # Date/Time values
    if datatype.lower() in ['date', 'tod', 'ltod', 'dt', 'dtl', 'ldt']:
        return value
    
    # Numeric values
    return value


def get_xml_block_type(root: ET.Element) -> Optional[str]:
    """
    Determine the type of TIA Portal block from XML root element.
    
    Args:
        root: XML root element
        
    Returns:
        Block type: 'UDT', 'DB', 'FB', 'FC', 'TAG_TABLE', 'TECH_OBJECT', or None
    """
    # Check root tag
    for child in root:
        tag = child.tag
        
        if 'PlcStruct' in tag:
            return 'UDT'
        elif 'GlobalDB' in tag or 'InstanceDB' in tag:
            return 'DB'
        elif tag.endswith('FB'):
            return 'FB'
        elif tag.endswith('FC'):
            return 'FC'
        elif 'PlcTagTable' in tag:
            return 'TAG_TABLE'
        elif 'TO_' in tag or 'TechnologyObject' in tag:
            return 'TECH_OBJECT'
    
    return None


def validate_xml_file(file_path: Path) -> bool:
    """
    Validate that file is a valid TIA Portal XML export.

    Args:
        file_path: Path to XML file

    Returns:
        True if valid, False otherwise
    """
    try:
        # XXE Protection: Use defusedxml for secure XML parsing
        try:
            from defusedxml.ElementTree import parse as safe_parse
            tree = safe_parse(file_path)
        except ImportError:
            # Fallback: ElementTree (Python 3.8+ has XXE protection by default)
            tree = ET.parse(file_path)
        root = tree.getroot()

        # Check for Document root and Engineering version
        if root.tag != 'Document':
            logger.warning(f"{file_path}: Root element is not 'Document'")
            return False

        engineering = root.find('Engineering')
        if engineering is None:
            logger.warning(f"{file_path}: Missing 'Engineering' element")
            return False

        return True

    except ET.ParseError as e:
        logger.error(f"{file_path}: XML parse error: {e}")
        return False
    except FileNotFoundError as e:
        logger.error(f"{file_path}: File not found during validation: {e}")
        return False
    except Exception as e:
        logger.error(f"{file_path}: Unexpected validation error: {e}")
        return False


def find_xml_files(directory: Path, recursive: bool = True) -> List[Path]:
    """
    Find all XML files in directory.
    
    Args:
        directory: Directory to search
        recursive: Search recursively
        
    Returns:
        List of XML file paths
    """
    if recursive:
        return list(directory.rglob('*.xml'))
    else:
        return list(directory.glob('*.xml'))
