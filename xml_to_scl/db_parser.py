"""
Data Block (DB) parser for TIA Portal XML exports
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


class DBParser(XMLParserBase):
    """Parser for Data Block (GlobalDB/InstanceDB) XML files"""
    
    def _find_block_element(self) -> Optional[ET.Element]:
        """Find the GlobalDB or InstanceDB element"""
        if self.root is None:
            return None
        
        # Look for SW.Blocks.GlobalDB or SW.Blocks.InstanceDB
        for child in self.root:
            if 'GlobalDB' in child.tag or 'InstanceDB' in child.tag:
                self.parsed_data['db_type'] = 'Instance' if 'InstanceDB' in child.tag else 'Global'
                return child
        
        return None
    
    def _parse_specific(self):
        """Parse DB-specific data"""
        if self.block_element is None:
            return
        
        # Parse interface to get DB variables
        interface_data = self._parse_interface()
        
        # DBs typically have a "Static" section
        if 'Static' in interface_data:
            self.parsed_data['variables'] = interface_data['Static']
        else:
            # Get first available section
            for section_name, members in interface_data.items():
                self.parsed_data['variables'] = members
                break
        
        # Check for instance DB specific data
        if self.parsed_data.get('db_type') == 'Instance':
            self._parse_instance_db_data()
        
        logger.debug(f"Parsed DB '{self.parsed_data.get('name')}' with {len(self.parsed_data.get('variables', []))} variables")
    
    def _parse_instance_db_data(self):
        """Parse instance DB specific data (associated FB)"""
        if self.block_element is None:
            return
        
        attr_list = self.block_element.find('AttributeList')
        if attr_list is None:
            return
        
        # Get associated FB name
        instance_of = attr_list.find('InstanceOfName')
        if instance_of is not None and instance_of.text:
            self.parsed_data['instance_of'] = instance_of.text.strip('"')
