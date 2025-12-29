"""
Data Block (DB) SCL code generator
"""

import logging
from pathlib import Path
from typing import Dict, Any

try:
    from .scl_generator_base import SCLGeneratorBase
    from .utils import escape_scl_identifier
except ImportError:
    from scl_generator_base import SCLGeneratorBase
    from utils import escape_scl_identifier

logger = logging.getLogger(__name__)


class DBGenerator(SCLGeneratorBase):
    """Generator for Data Block SCL code"""
    
    def _generate_specific(self):
        """Generate DB-specific SCL code"""
        name = escape_scl_identifier(self.data.get('name', 'UnknownDB'))
        db_type = self.data.get('db_type', 'Global')
        
        # DATA_BLOCK declaration
        self._add_line(f"DATA_BLOCK {name}")
        
        # Attributes
        self._generate_attributes()
        
        # Version
        self._generate_version()
        
        # Add title/comment if present
        if 'title' in self.data:
            self._indent()
            self._add_comment(self.data['title'])
            self._dedent()
        
        if 'comment' in self.data:
            self._indent()
            self._add_block_comment(self.data['comment'])
            self._dedent()
        
        # For instance DBs, add instance reference
        if db_type == 'Instance' and 'instance_of' in self.data:
            self._indent()
            instance_of = escape_scl_identifier(self.data['instance_of'])
            self._add_line(f"INSTANCE OF {instance_of}")
            self._dedent()
        
        # Memory retention
        self._indent()
        self._add_line("NON_RETAIN")
        self._dedent()
        
        # VAR section
        self._indent()
        self._add_line("VAR")
        self._indent()
        
        # Generate variables
        variables = self.data.get('variables', [])
        if variables:
            self._generate_struct_members(variables, include_values=False)
        else:
            self._add_comment("Empty data block")
        
        # Close VAR
        self._dedent()
        self._add_line("END_VAR")
        self._dedent()
        
        # BEGIN section (initialization)
        self._add_line("")
        self._add_line("BEGIN")
        
        # Add initialization values if present
        self._generate_initialization(variables)
        
        # Close DATA_BLOCK
        self._add_line("END_DATA_BLOCK")
        self._add_line("")
    
    def _generate_initialization(self, variables: list):
        """
        Generate initialization section for variables with start values.
        
        Args:
            variables: List of variable dictionaries
        """
        has_init = False
        
        for var in variables:
            if 'start_value' in var:
                has_init = True
                self._indent()
                name = escape_scl_identifier(var['name'])
                value = var['start_value']
                self._add_line(f"{name} := {value};")
                self._dedent()
        
        if not has_init:
            self._indent()
            self._add_comment("No initialization required")
            self._dedent()
    
    def get_file_extension(self) -> str:
        """Get the correct file extension for DB files"""
        return ".db"
