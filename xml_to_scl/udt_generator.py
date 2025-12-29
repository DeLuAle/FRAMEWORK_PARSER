"""
UDT (User Defined Type) SCL code generator
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from .scl_generator_base import SCLGeneratorBase
    from .utils import escape_scl_identifier
except ImportError:
    from scl_generator_base import SCLGeneratorBase
    from utils import escape_scl_identifier

logger = logging.getLogger(__name__)


class UDTGenerator(SCLGeneratorBase):
    """Generator for UDT SCL code"""
    
    def generate(self, output_path: Optional[Path] = None) -> str:
        """
        Generate SCL code (override to skip header for UDT).
        
        Args:
            output_path: Optional path to write SCL file
            
        Returns:
            Generated SCL code as string
        """
        try:
            self.scl_lines = []
            self.indent_level = 0
            
            # Skip header for UDT - TIA Portal format doesn't include it
            
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
    
    def _generate_specific(self):
        """Generate UDT-specific SCL code"""
        name = self.data.get('name', 'UnknownUDT')
        
        # TYPE declaration with quoted name (TIA Portal format)
        self._add_line(f'TYPE "{name}"')
        
        # Version (must come before comments in TIA Portal format)
        self._generate_version()
        
        # Add comment after VERSION
        if 'title' in self.data or 'comment' in self.data or 'name' in self.data:
            if 'name' in self.data:
                self._add_comment(f"Block: {self.data['name']}")
        
        # STRUCT declaration (indented)
        self._indent()
        self._add_line("STRUCT")
        self._indent()
        
        # Generate members
        members = self.data.get('members', [])
        if members:
            self._generate_struct_members(members, include_values=True)
        else:
            self._add_comment("Empty structure")
        
        # Close STRUCT
        self._dedent()
        self._add_line("END_STRUCT;")
        self._dedent()
        
        # Empty line before END_TYPE
        self._add_line("")
        
        # Close TYPE
        self._add_line("END_TYPE")
        self._add_line("")
    
    def get_file_extension(self) -> str:
        """Get the correct file extension for UDT files"""
        return ".udt"
