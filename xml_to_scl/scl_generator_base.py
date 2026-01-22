"""
Base SCL code generator
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

try:
    from .config import config
    from .utils import escape_scl_identifier, format_scl_comment, format_scl_value
except ImportError:
    from config import config
    from utils import escape_scl_identifier, format_scl_comment, format_scl_value

logger = logging.getLogger(__name__)

# Standard SCL data types that don't need quotes
SCL_STANDARD_TYPES = {
    # Boolean and bit types
    'Bool', 'Byte', 'Word', 'DWord', 'LWord',
    # Integer types
    'SInt', 'Int', 'DInt', 'LInt', 'USInt', 'UInt', 'UDInt', 'ULInt',
    # Real types
    'Real', 'LReal',
    # Time types
    'Time', 'LTime', 'S5Time', 'Date', 'Time_Of_Day', 'TOD', 'Date_And_Time', 'DT', 'DTL',
    # String types
    'String', 'WString', 'Char', 'WChar',
    # Special types
    'Struct', 'Void',
    # Hardware identifiers (system types)
    'HW_DEVICE', 'HW_INTERFACE', 'HW_SUBMODULE', 'HW_HSC', 'HW_PWM', 'HW_ANY',
    # System function types
    'AOM_IDENT', 'CONN_ANY', 'CONN_OUC', 'CONN_PRG', 'DB_ANY', 'DB_DYN', 'DB_WWW',
    'EVENT_ANY', 'EVENT_ATT', 'EVENT_HWINT', 'HW_IOSYSTEM', 'OB_ANY', 'OB_ATT',
    'OB_CYCLIC', 'OB_DELAY', 'OB_DIAG', 'OB_HWINT', 'OB_PCYCLE', 'OB_STARTUP',
    'OB_TIMEERROR', 'OB_TOD', 'PORT', 'RTM',
}


class SCLGeneratorBase(ABC):
    """Base class for SCL code generators"""
    
    def __init__(self, parsed_data: Dict[str, Any]):
        """
        Initialize generator.
        
        Args:
            parsed_data: Parsed data from XML parser
        """
        self.data = parsed_data
        self.scl_lines: List[str] = []
        self.indent_level = 0
        
    def generate(self, output_path: Optional[Path] = None) -> str:
        """
        Generate SCL code.
        
        Args:
            output_path: Optional path to write SCL file
            
        Returns:
            Generated SCL code as string
        """
        try:
            self.scl_lines = []
            self.indent_level = 0
            
            # Generate header
            if config.get('generate_headers', True):
                self._generate_header()
            
            # Call specific generator implementation
            self._generate_specific()
            
            # Join lines
            scl_code = '\n'.join(self.scl_lines)
            
            # Write to file if path provided
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                # Write with UTF-8 BOM encoding for TIA Portal compatibility
                with open(output_path, 'w', encoding='utf-8-sig') as f:
                    f.write(scl_code)
                logger.info(f"Generated SCL file: {output_path}")
            
            return scl_code
            
        except Exception as e:
            logger.error(f"Error generating SCL: {e}")
            raise
    
    @abstractmethod
    def _generate_specific(self):
        """Generate block-specific SCL code. Must be implemented by subclasses."""
        pass
    
    def _generate_header(self):
        """Generate file header comment"""
        if 'name' in self.data:
            self._add_comment(f"Block: {self.data['name']}")
            if 'title' in self.data and self.data['title']:
                self._add_comment(f"Title: {self.data['title']}")
            self._add_line("")
    
    def _add_line(self, line: str = ""):
        """
        Add a line to SCL code.
        
        Args:
            line: Line to add (without indentation)
        """
        if line:
            indent = config.indent * self.indent_level
            self.scl_lines.append(f"{indent}{line}")
        else:
            self.scl_lines.append("")
    
    def _add_comment(self, comment: str):
        """
        Add a comment line.
        
        Args:
            comment: Comment text
        """
        if comment:
            self._add_line(f"// {comment}")
    
    def _add_block_comment(self, comment: str):
        """
        Add a multi-line block comment.
        
        Args:
            comment: Comment text
        """
        if not comment:
            return
        
        lines = comment.split('\n')
        for line in lines:
            if line.strip():
                self._add_comment(line.strip())
    
    def _indent(self):
        """Increase indentation level"""
        self.indent_level += 1
    
    def _dedent(self):
        """Decrease indentation level"""
        self.indent_level = max(0, self.indent_level - 1)
    
    def _generate_member_declaration(self, member: Dict, include_value: bool = True):
        """
        Generate SCL declaration for a member.
        
        Args:
            member: Member data dictionary
            include_value: Whether to include initial value
        """
        name = escape_scl_identifier(member['name'])
        datatype = member.get('datatype', 'Void')
        
        # Handle array types
        if member.get('is_array', False):
            base_type = member.get('base_type', datatype)
            bounds = member.get('array_bounds', '0..0')
            # Standard types don't need quotes
            if base_type in SCL_STANDARD_TYPES:
                datatype_str = f"Array[{bounds}] of {base_type}"
            else:
                # UDT types need quotes
                if not (base_type.startswith('"') and base_type.endswith('"')):
                    base_type = f'"{base_type}"'
                datatype_str = f"Array[{bounds}] of {base_type}"
        else:
            # Standard types don't need quotes
            if datatype in SCL_STANDARD_TYPES:
                datatype_str = datatype
            else:
                # UDT types need quotes
                if not (datatype.startswith('"') and datatype.endswith('"')):
                    datatype = f'"{datatype}"'
                datatype_str = datatype
        
        # Build declaration
        declaration = f"{name} : {datatype_str}"
        
        # Add initial value if present
        if include_value and 'start_value' in member:
            value = format_scl_value(member['start_value'], datatype)
            if value:
                declaration += f" := {value}"
        
        declaration += ";"
        
        # Add comment if present
        if 'comment' in member and config.get('preserve_comments', True):
            comment = member['comment']
            if len(declaration) < 50:
                # Inline comment
                declaration += f"   // {comment}"
            else:
                # Comment on previous line
                self._add_comment(comment)
        
        self._add_line(declaration)
    
    def _generate_struct_members(self, members: List[Dict], include_values: bool = True):
        """
        Generate SCL declarations for struct members (recursive for nested structs).
        
        Args:
            members: List of member dictionaries
            include_values: Whether to include initial values
        """
        for member in members:
            # Check if it's a nested struct
            if member.get('is_struct', False) and 'members' in member:
                # Nested struct
                name = escape_scl_identifier(member['name'])
                self._add_line(f"{name} : Struct")
                self._indent()
                self._generate_struct_members(member['members'], include_values)
                self._dedent()
                self._add_line("END_STRUCT;")
            else:
                # Regular member
                self._generate_member_declaration(member, include_values)
    
    def _generate_attributes(self):
        """Generate block attributes"""
        attributes = []
        
        # Optimized access
        if config.get('optimize_access', True):
            if self.data.get('memory_layout') == 'Optimized':
                attributes.append("S7_Optimized_Access := 'TRUE'")
        
        if attributes:
            self._add_line("{ " + "; ".join(attributes) + " }")
    
    def _generate_version(self):
        """Generate version declaration"""
        # Default version
        self._add_line("VERSION : 0.1")
