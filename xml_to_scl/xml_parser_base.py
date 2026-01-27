"""
Base XML parser for TIA Portal exports
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

try:
    from .config import NAMESPACES, DATATYPE_MAPPING
    from .utils import extract_multilingual_text, parse_array_datatype
except ImportError:
    from config import NAMESPACES, DATATYPE_MAPPING
    from utils import extract_multilingual_text, parse_array_datatype

logger = logging.getLogger(__name__)


class XMLParserBase(ABC):
    """Base class for XML parsers"""
    
    def __init__(self, xml_path: Path):
        """
        Initialize parser.
        
        Args:
            xml_path: Path to XML file
        """
        self.xml_path = xml_path
        self.tree: Optional[ET.ElementTree] = None
        self.root: Optional[ET.Element] = None
        self.block_element: Optional[ET.Element] = None
        self.parsed_data: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """
        Parse XML file and extract data.

        Returns:
            Dictionary with parsed data
        """
        try:
            # XXE Protection: Use defusedxml for secure XML parsing
            # This prevents XXE attacks and entity expansion attacks
            try:
                from defusedxml.ElementTree import parse as safe_parse
                self.tree = safe_parse(self.xml_path)
            except ImportError:
                # Fallback: ElementTree (Python 3.8+ has XXE protection by default)
                # defusedxml is recommended but ElementTree is reasonably safe on modern Python
                self.tree = ET.parse(self.xml_path)
            self.root = self.tree.getroot()

            # Find the main block element
            self.block_element = self._find_block_element()
            if self.block_element is None:
                raise ValueError(f"Could not find block element in {self.xml_path}")

            # Extract common attributes
            self._parse_common_attributes()

            # Call specific parser implementation
            self._parse_specific()

            logger.info(f"Successfully parsed {self.xml_path.name}")
            return self.parsed_data

        except FileNotFoundError as e:
            logger.error(f"XML file not found: {self.xml_path}")
            raise
        except ET.ParseError as e:
            logger.error(f"XML parse error in {self.xml_path}: {e}")
            raise
        except ValueError as e:
            logger.error(f"Validation error in {self.xml_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing {self.xml_path}: {e}")
            raise
    
    @abstractmethod
    def _find_block_element(self) -> Optional[ET.Element]:
        """Find the main block element in XML. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _parse_specific(self):
        """Parse block-specific data. Must be implemented by subclasses."""
        pass
    
    def _parse_common_attributes(self):
        """Parse common attributes present in all blocks"""
        if self.block_element is None:
            return
        
        attr_list = self.block_element.find('AttributeList')
        if attr_list is None:
            return
        
        # Extract name
        name_elem = attr_list.find('Name')
        if name_elem is not None:
            self.parsed_data['name'] = name_elem.text
        
        # Extract number (if present)
        number_elem = attr_list.find('Number')
        if number_elem is not None:
            self.parsed_data['number'] = number_elem.text
        
        # Extract access level
        access_elem = attr_list.find('Access')
        if access_elem is not None:
            self.parsed_data['access'] = access_elem.text
        
        # Extract programming language
        lang_elem = attr_list.find('ProgrammingLanguage')
        if lang_elem is not None:
            self.parsed_data['programming_language'] = lang_elem.text
        
        # Extract memory layout
        memory_elem = attr_list.find('MemoryLayout')
        if memory_elem is not None:
            self.parsed_data['memory_layout'] = memory_elem.text
        
        # Extract comments
        self._parse_comments()
    
    def _parse_comments(self):
        """Parse multilingual comments"""
        if self.block_element is None:
            return
        
        # Find Comment element
        comment_elem = self.block_element.find('.//MultilingualText[@CompositionName="Comment"]')
        if comment_elem is not None:
            comment_text = extract_multilingual_text(comment_elem)
            if comment_text:
                self.parsed_data['comment'] = comment_text
        
        # Find Title element
        title_elem = self.block_element.find('.//MultilingualText[@CompositionName="Title"]')
        if title_elem is not None:
            title_text = extract_multilingual_text(title_elem)
            if title_text:
                self.parsed_data['title'] = title_text
    
    def _parse_interface(self) -> Dict[str, List[Dict]]:
        """
        Parse interface sections (Input, Output, InOut, Static, Temp, Constant).
        
        Returns:
            Dictionary with section names as keys and lists of members as values
        """
        interface_data = {}
        
        if self.block_element is None:
            return interface_data
        
        # Find Interface element
        interface_elem = self.block_element.find('AttributeList/Interface')
        if interface_elem is None:
            return interface_data
        
        # Parse Sections
        sections_elem = interface_elem.find('{' + NAMESPACES['sw'] + '}Sections')
        if sections_elem is None:
            # Try without namespace
            sections_elem = interface_elem.find('Sections')
        
        if sections_elem is None:
            return interface_data
        
        # Iterate through sections
        for section in sections_elem.findall('{' + NAMESPACES['sw'] + '}Section'):
            section_name = section.get('Name')
            if section_name:
                members = self._parse_section_members(section)
                if members:
                    interface_data[section_name] = members
        
        # Try without namespace if nothing found
        if not interface_data:
            for section in sections_elem.findall('Section'):
                section_name = section.get('Name')
                if section_name:
                    members = self._parse_section_members(section)
                    if members:
                        interface_data[section_name] = members
        
        return interface_data
    
    def _parse_section_members(self, section: ET.Element) -> List[Dict]:
        """
        Parse members in an interface section.
        
        Args:
            section: Section XML element
            
        Returns:
            List of member dictionaries
        """
        members = []
        
        # Try with namespace
        member_elements = section.findall('{' + NAMESPACES['sw'] + '}Member')
        if not member_elements:
            # Try without namespace
            member_elements = section.findall('Member')
        
        for member in member_elements:
            member_data = self._parse_member(member)
            if member_data:
                members.append(member_data)
        
        return members
    
    def _parse_member(self, member: ET.Element, parent_path: str = "") -> Optional[Dict]:
        """
        Parse a single member element.
        
        Args:
            member: Member XML element
            parent_path: Parent path for nested members
            
        Returns:
            Dictionary with member data
        """
        member_data = {}
        
        # Get name
        name = member.get('Name')
        if not name:
            return None
        
        member_data['name'] = name
        if parent_path:
            member_data['full_path'] = f"{parent_path}.{name}"
        else:
            member_data['full_path'] = name
        
        # Get datatype
        datatype = member.get('Datatype')
        if datatype:
            # Remove HTML entity quotes and regular quotes
            datatype = datatype.replace('&quot;', '').replace('"', '')
            member_data['datatype'] = datatype
            
            # Parse array type
            base_type, array_bounds = parse_array_datatype(datatype)
            if array_bounds:
                member_data['is_array'] = True
                member_data['array_bounds'] = array_bounds
                member_data['base_type'] = base_type
            else:
                member_data['is_array'] = False
        
        # Get version (for FB instances)
        version = member.get('Version')
        if version:
            member_data['version'] = version
        
<<<<<<< HEAD
        # Get start value - try with and without namespace
        start_value_elem = member.find('StartValue')
        if start_value_elem is None:
            # Try with namespace
            start_value_elem = member.find('{' + NAMESPACES.get('sw', '') + '}StartValue')
=======
        # Get start value - try with and without namespace
        start_value_elem = member.find('StartValue')
        if start_value_elem is None:
            # Try with namespace
            start_value_elem = member.find('{' + NAMESPACES.get('sw', '') + '}StartValue')

>>>>>>> origin/claude/verify-xml-parser-cleanup-jmpca
        if start_value_elem is not None and start_value_elem.text:
            member_data['start_value'] = start_value_elem.text
        
        # Get comment
        comment_elem = member.find('Comment')
        if comment_elem is not None:
            comment_text = extract_multilingual_text(comment_elem)
            if comment_text:
                member_data['comment'] = comment_text
        
        # Get attributes
        attr_list = member.find('AttributeList')
        if attr_list is not None:
            attributes = {}
            for attr in attr_list:
                attr_name = attr.get('Name')
                if attr_name:
                    if attr.tag == 'BooleanAttribute':
                        attributes[attr_name] = attr.text.lower() == 'true'
                    else:
                        attributes[attr_name] = attr.text
            
            if attributes:
                member_data['attributes'] = attributes
        
        # Check for nested struct members
        nested_members = []
        
        # Try with namespace first
        nested_elements = member.findall('{' + NAMESPACES['sw'] + '}Member')
        if not nested_elements:
            # Try without namespace
            nested_elements = member.findall('Member')
        
        for nested in nested_elements:
            nested_data = self._parse_member(nested, member_data['full_path'])
            if nested_data:
                nested_members.append(nested_data)
        
        if nested_members:
            member_data['members'] = nested_members
            member_data['is_struct'] = True
        else:
            member_data['is_struct'] = False
        
        return member_data
