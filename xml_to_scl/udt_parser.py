"""
UDT (User Defined Type) parser for TIA Portal XML exports
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from .xml_parser_base import XMLParserBase
except ImportError:
    from xml_parser_base import XMLParserBase

logger = logging.getLogger(__name__)


class UDTParser(XMLParserBase):
    """Parser for UDT (PlcStruct) XML files"""
    
    def _find_block_element(self) -> Optional[ET.Element]:
        """Find the PlcStruct element"""
        if self.root is None:
            return None
        
        # Look for SW.Types.PlcStruct
        for child in self.root:
            if 'PlcStruct' in child.tag:
                return child
        
        return None
    
    def _parse_specific(self):
        """Parse UDT-specific data"""
        if self.block_element is None:
            return
        
        # Parse interface to get struct members
        interface_data = self._parse_interface()
        
        # UDTs typically have a "None" section containing the struct members
        if 'None' in interface_data:
            self.parsed_data['members'] = interface_data['None']
        elif 'Static' in interface_data:
            # Some UDTs use Static section
            self.parsed_data['members'] = interface_data['Static']
        else:
            # Get first available section
            for section_name, members in interface_data.items():
                self.parsed_data['members'] = members
                break
        
        logger.debug(f"Parsed UDT '{self.parsed_data.get('name')}' with {len(self.parsed_data.get('members', []))} members")
