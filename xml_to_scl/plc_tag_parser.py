import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Optional

class PLCTagParser:
    """Parser for TIA Portal PLC Tag Table XML exports."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse(self, xml_file: str) -> List[Dict[str, str]]:
        """
        Parse a PLC Tag Table XML file.

        Args:
            xml_file: Path to the .xml file

        Returns:
            List of dictionaries containing tag data (Name, DataType, Address, Comment)
        """
        self.logger.info(f"Parsing PLC tags from: {xml_file}")
        try:
            # XXE Protection: Use defusedxml for secure XML parsing
            try:
                from defusedxml.ElementTree import parse as safe_parse
                tree = safe_parse(xml_file)
            except ImportError:
                # Fallback: ElementTree (Python 3.8+ has XXE protection by default)
                tree = ET.parse(xml_file)
            root = tree.getroot()

            tags = self._parse_tags(root)
            constants = self._parse_constants(root)

            self.logger.info(f"Found {len(tags)} tags and {len(constants)} constants.")
            return tags + constants

        except FileNotFoundError as e:
            self.logger.error(f"PLC tag file not found: {xml_file}")
            raise
        except ET.ParseError as e:
            self.logger.error(f"XML parse error in PLC tags: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to parse PLC tags: {e}")
            raise

    def _parse_tags(self, root: ET.Element) -> List[Dict[str, str]]:
        """Extract PLC Tags."""
        tags = []
        # TIA Portal XML namespace handling might be needed if xmlns is present.
        # Usually TIA exports are namespaceless or use specific schemas.
        # We search for 'SW.Tags.PlcTag'
        
        for tag_elem in root.iter('SW.Tags.PlcTag'):
            tag_data = {
                'type': 'tag',
                'name': '',
                'data_type': '',
                'logical_address': '',
                'comment': ''
            }
            
            # 1. AttributeList
            attr_list = tag_elem.find('AttributeList')
            if attr_list is not None:
                name_node = attr_list.find('Name')
                if name_node is not None:
                    tag_data['name'] = name_node.text
                
                type_node = attr_list.find('DataTypeName')
                if type_node is not None:
                    # Strip quotes if present e.g. "Bool" -> Bool
                    dtype = type_node.text
                    if dtype and (dtype.startswith('"') and dtype.endswith('"')):
                        dtype = dtype[1:-1]
                    tag_data['data_type'] = dtype
                    
                addr_node = attr_list.find('LogicalAddress')
                if addr_node is not None:
                    tag_data['logical_address'] = addr_node.text
            
            # 2. Comments (Multilingual)
            comment = self._extract_comment(tag_elem)
            if comment:
                tag_data['comment'] = comment
                
            if tag_data['name']:
                tags.append(tag_data)
                
        return tags

    def _parse_constants(self, root: ET.Element) -> List[Dict[str, str]]:
        """Extract User Constants."""
        constants = []
        for const_elem in root.iter('SW.Tags.PlcUserConstant'):
            const_data = {
                'type': 'constant',
                'name': '',
                'data_type': '',
                'value': '',
                'comment': ''
            }
            
            attr_list = const_elem.find('AttributeList')
            if attr_list is not None:
                name_node = attr_list.find('Name')
                if name_node is not None:
                    const_data['name'] = name_node.text
                
                type_node = attr_list.find('DataTypeName')
                if type_node is not None:
                    dtype = type_node.text
                    if dtype and (dtype.startswith('"') and dtype.endswith('"')):
                        dtype = dtype[1:-1]
                    const_data['data_type'] = dtype
                    
                val_node = attr_list.find('Value')
                if val_node is not None:
                    const_data['value'] = val_node.text

            comment = self._extract_comment(const_elem)
            if comment:
                const_data['comment'] = comment
                
            if const_data['name']:
                constants.append(const_data)
                
        return constants

    def _extract_comment(self, elem: ET.Element) -> str:
        """Helper to extract comment from MultilingualText"""
        # Structure: ObjectList -> MultilingualText(Comment) -> ObjectList -> MultilingualTextItem -> AttributeList -> Text
        
        # Find ObjectList that acts as container for comments
        # Usually direct child of Tag
        obj_list = elem.find('ObjectList')
        if obj_list is None:
            return ""
            
        comment_obj = None
        for child in obj_list:
            if 'MultilingualText' in child.tag and child.get('CompositionName') == 'Comment':
                comment_obj = child
                break
        
        if comment_obj is None:
            return ""
            
        inner_obj_list = comment_obj.find('ObjectList')
        if inner_obj_list is None:
            return ""
            
        # Prioritize en-US, then any text
        params = {}
        first_text = ""
        
        for item in inner_obj_list:
            if 'MultilingualTextItem' in item.tag:
                attrs = item.find('AttributeList')
                if attrs is not None:
                    culture = attrs.find('Culture').text
                    text_node = attrs.find('Text')
                    text = text_node.text if text_node is not None else ""
                    
                    if text:
                        if not first_text:
                            first_text = text
                        if culture == 'en-US':
                            return text
                            
        return first_text
