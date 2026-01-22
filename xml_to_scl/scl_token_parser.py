"""
Parser for TIA Portal SCL Tokenized XML (StructuredText)
"""

import logging
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class SCLTokenParser:
    """Parses StructuredText XML elements into SCL code string"""
    
    def __init__(self, root_element: ET.Element):
        self.root = root_element
        self.buffer = []
        
    def parse(self) -> str:
        """Parse the element and return SCL string"""
        self.buffer = []
        self._parse_element_children(self.root)
        return "".join(self.buffer)
    
    def _parse_element_children(self, element: ET.Element):
        """Recursively parse children of an element"""
        for child in element:
            tag = child.tag.split('}')[-1]
            self._parse_node(child, tag)
            
    def _parse_node(self, node: ET.Element, tag: str):
        """Parse a single node"""
        if tag == 'Token':
            self.buffer.append(node.get('Text', ''))
            
        elif tag == 'Blank':
            count = int(node.get('Num', '1'))
            self.buffer.append(' ' * count)
            
        elif tag == 'NewLine':
            count = int(node.get('Num', '1'))
            self.buffer.append('\n' * count)
            
        elif tag == 'Access':
            self._handle_access(node)
            
        elif tag == 'LineComment':
            self.buffer.append('//')
            self._parse_element_children(node)
            
        elif tag == 'Comment':
            self.buffer.append('(*')
            self._parse_element_children(node)
            self.buffer.append('*)')
            
        elif tag == 'Text':
            if node.text:
                self.buffer.append(node.text)
                
        elif tag == 'Component':
            self.buffer.append(node.get('Name', ''))
            self._parse_element_children(node)
            
        elif tag == 'PredefinedVariable':
             self.buffer.append(node.get('Name', ''))
             
        elif tag == 'Symbol':
             self._parse_element_children(node)
             
        elif tag == 'Constant':
             # Handle GlobalConstant or UserConstant which use Name attribute
             name = node.get('Name')
             if name:
                 self.buffer.append(name)
             self._parse_element_children(node)
             
        elif tag == 'ConstantValue':
             if node.text: self.buffer.append(node.text)
             
        elif tag == 'CallInfo':
             self._handle_call_info(node)
             
        elif tag == 'Parameter':
             self._handle_parameter(node)
             
        else:
            # Fallback: recurse
            self._parse_element_children(node)

    def _handle_access(self, node: ET.Element):
        """Handle Access element"""
        scope = node.get('Scope')

        if scope == 'Call':
            self._parse_element_children(node) # Will hit CallInfo
        elif scope == 'LiteralConstant':
            self._handle_constant(node)
        elif scope == 'PredefinedVariable':
            self._parse_element_children(node) # Will hit PredefinedVariable
        elif scope == 'LocalVariable':
            # Local variables: prefix with #
            self.buffer.append('#')
            self._parse_element_children(node) # Will hit Symbol -> Component
        elif scope == 'GlobalVariable':
            # Global DB variables: first component in quotes, rest with dots
            self._handle_global_variable(node)
        else:
            # Fallback for other scopes
            # Add # prefix for local variables that weren't caught by earlier conditions
            if scope in ['LocalConstant', 'TypedConstant']:
                self.buffer.append('#')

            self._parse_element_children(node) # Will hit Symbol -> Component

    def _handle_constant(self, node: ET.Element):
        """Handle LiteralConstant"""
        # Finds ConstantValue deep inside
        constant = node.find('.//{*}Constant')
        if constant is not None:
            val_node = constant.find('.//{*}ConstantValue')
            if val_node is not None and val_node.text:
                 self.buffer.append(val_node.text)
                 return
        self._parse_element_children(node)

    def _handle_call_info(self, call_info: ET.Element):
        """Handle CallInfo"""
        # Check if Instance exists (FB call)
        instance = call_info.find('.//{*}Instance')
        if instance is None:
             # FC Call? Use Name attribute
             name = call_info.get('Name')
             if name:
                 self.buffer.append(f'"{name}"')
        
        # Recurse children
        self._parse_element_children(call_info)

    def _handle_parameter(self, param_node: ET.Element):
        """Handle Parameter element in a Call"""
        name = param_node.get('Name')
        if name:
            self.buffer.append(name)
        self._parse_element_children(param_node)

    def _handle_global_variable(self, node: ET.Element):
        """
        Handle GlobalVariable Access element.

        Global DB variables format: "FirstComponent".SecondComponent.ThirdComponent
        - First component is wrapped in quotes
        - Subsequent components are separated by dots
        """
        # Find Symbol element
        symbol = node.find('.//{*}Symbol')
        if symbol is None:
            # Fallback if no Symbol found
            self._parse_element_children(node)
            return

        # Extract all Component elements
        components = []
        for child in symbol:
            tag = child.tag.split('}')[-1]
            if tag == 'Component':
                comp_name = child.get('Name')
                if comp_name:
                    components.append(comp_name)

                    # Check for nested array index in Component
                    # Structure: <Component Name="Rest_Ls"><Access><Constant>1</Constant></Access></Component>
                    for sub_elem in child:
                        sub_tag = sub_elem.tag.split('}')[-1]
                        if sub_tag == 'Access':
                            # Found array index - parse it
                            for const_elem in sub_elem:
                                const_tag = const_elem.tag.split('}')[-1]
                                if const_tag == 'Constant':
                                    for const_val in const_elem:
                                        val_tag = const_val.tag.split('}')[-1]
                                        if val_tag == 'ConstantValue':
                                            idx = const_val.text
                                            if idx:
                                                components.append(f'[{idx}]')

        if not components:
            return

        # First component wrapped in quotes
        self.buffer.append(f'"{components[0]}"')

        # Remaining components separated by dots
        for i, comp in enumerate(components[1:], start=1):
            # Check if it's an array index (starts with '[')
            if comp.startswith('['):
                self.buffer.append(comp)
            else:
                self.buffer.append(f'.{comp}')
