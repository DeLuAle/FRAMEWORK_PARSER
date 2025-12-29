"""
FB/FC (Function Block / Function) parser for TIA Portal XML exports
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


class FBFCParser(XMLParserBase):
    """Parser for Function Block (FB) and Function (FC) XML files"""
    
    def _find_block_element(self) -> Optional[ET.Element]:
        """Find the FB or FC element"""
        if self.root is None:
            return None
        
        # Look for SW.Blocks.FB or SW.Blocks.FC
        for child in self.root:
            if 'FB' in child.tag and 'Blocks' in child.tag:
                self.parsed_data['block_type'] = 'FB'
                return child
            elif 'FC' in child.tag and 'Blocks' in child.tag:
                self.parsed_data['block_type'] = 'FC'
                return child
        
        return None
    
    def _parse_specific(self):
        """Parse FB/FC-specific data"""
        if self.block_element is None:
            return
        
        # Parse attributes (MemoryLayout, Author, Family, Version, etc.)
        self._parse_attributes()
        
        # Parse interface to get all sections
        interface_data = self._parse_interface()
        
        # Store all interface sections
        self.parsed_data['interface'] = interface_data
        
        # Get programming language
        prog_lang = self.parsed_data.get('programming_language', '')
        
        # For now, we only parse the interface
        # Logic conversion (LAD/FBD to SCL) will be Phase 2
        if prog_lang in ['LAD', 'FBD', 'F_LAD', 'F_FBD']:
            self.parsed_data['has_graphical_logic'] = True
            
            # Try to parse LAD logic to extract FB calls
            self._parse_lad_logic()
            
            logger.info(f"Block uses {prog_lang} - logic will be placeholder")
        else:
            self.parsed_data['has_graphical_logic'] = False
        
        logger.debug(f"Parsed {self.parsed_data.get('block_type')} '{self.parsed_data.get('name')}' "
                    f"with {len(interface_data)} interface sections")

    def _parse_attributes(self):
        """Parse block attributes like MemoryLayout, Author, Family, Version"""
        attr_list = self.block_element.find('AttributeList')
        if attr_list is None:
            return

        # Simple string attributes
        for attr_name in ['HeaderAuthor', 'HeaderFamily', 'HeaderVersion', 'MemoryLayout', 'ProgrammingLanguage']:
            elem = attr_list.find(attr_name)
            if elem is not None and elem.text:
                # Convert 'HeaderAuthor' -> 'author'
                key = attr_name.replace('Header', '').lower()
                if key == 'memorylayout': key = 'memory_layout'
                if key == 'programminglanguage': key = 'programming_language'
                self.parsed_data[key] = elem.text

        # Extract Version if HeaderVersion is not present/valid, falling back to other means if needed?
        # Sometimes 'Version' is a direct attribute or inside Interface? 
        # Actually TIA XML usually has Interface, MemoryLayout... 
        # Let's check for specific boolean attributes too if needed.
        
        # Check for SetENOAutomatically
        eno_elem = attr_list.find('SetENOAutomatically')
        if eno_elem is not None:
             self.parsed_data['set_eno_automatically'] = (eno_elem.text == 'true')
    
    def _parse_lad_logic(self):
        """Parse LAD/FBD and SCL logic"""
        logger.debug("Starting logic parsing")
        
        try:
            from lad_parser import LADLogicParser
            from scl_token_parser import SCLTokenParser
            from utils import extract_multilingual_text
        except ImportError:
            try:
                from .lad_parser import LADLogicParser
                from .scl_token_parser import SCLTokenParser
                from .utils import extract_multilingual_text
            except ImportError:
                logger.warning("Logic parsers not available")
                return
        
        logger.debug("Logic parsers imported successfully")
        
        # Find CompileUnits
        compile_units = []
        for elem in self.block_element.iter():
            if 'CompileUnit' in elem.tag:
                compile_units.append(elem)
        
        logger.debug(f"Found {len(compile_units)} CompileUnits")
        
        networks = []
        all_fb_calls = [] # For summary/backward compat
        
        for i, compile_unit in enumerate(compile_units):
            # logger.debug(f"Processing CompileUnit {i+1}/{len(compile_units)}")
            network_source = compile_unit.find('.//NetworkSource')
            
            # Find NetworkSource robustly
            if network_source is None:
                for child in compile_unit:
                    if 'NetworkSource' in child.tag:
                        network_source = child
                        break
            
            if network_source is not None:
                # Initialize network info
                network = {
                    'number': i + 1,
                    'type': None
                }
                
                # Extract Title and Comment
                # Note: MultilingualText is usually a child of ObjectList in CompileUnit
                # Structure: CompileUnit -> ObjectList -> MultilingualText
                
                comment_elem = compile_unit.find('.//MultilingualText[@CompositionName="Comment"]')
                if comment_elem is not None:
                    txt = extract_multilingual_text(comment_elem)
                    if txt:
                        network['comment'] = txt
                        
                title_elem = compile_unit.find('.//MultilingualText[@CompositionName="Title"]')
                if title_elem is not None:
                    txt = extract_multilingual_text(title_elem)
                    if txt:
                        network['title'] = txt

                # Check properties
                has_lad = False
                has_scl = False
                scl_elem = None
                
                for child in network_source:
                    if 'FlgNet' in child.tag:
                        has_lad = True
                    elif 'StructuredText' in child.tag:
                        has_scl = True
                        scl_elem = child
                
                if has_lad:
                    try:
                        lad_parser = LADLogicParser(compile_unit)
                        fb_calls = lad_parser.parse()
                        logic_ops = lad_parser._extract_operations()
                        network['type'] = 'LAD'
                        network['fb_calls'] = fb_calls
                        network['logic_ops'] = logic_ops
                        networks.append(network)
                        all_fb_calls.extend(fb_calls)
                    except Exception as e:
                        logger.warning(f"Error parsing LAD logic: {e}", exc_info=True)
                        
                elif has_scl and scl_elem is not None:
                    try:
                        scl_parser = SCLTokenParser(scl_elem)
                        scl_code = scl_parser.parse()
                        network['type'] = 'SCL'
                        network['code'] = scl_code
                        networks.append(network)
                    except Exception as e:
                        logger.warning(f"Error parsing SCL logic: {e}", exc_info=True)
                else:
                    logger.debug("  Empty or unknown network type")

        self.parsed_data['networks'] = networks
        self.parsed_data['fb_calls'] = all_fb_calls # Keep for reference
        
        logger.info(f"Extracted {len(networks)} logic networks ({len(all_fb_calls)} LAD FB calls)")
