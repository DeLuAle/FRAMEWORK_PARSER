"""
Configuration management for XML to SCL parser
"""

import logging
from pathlib import Path
from typing import Dict

# XML Namespaces used in TIA Portal exports
NAMESPACES = {
    'sw': 'http://www.siemens.com/automation/Openness/SW/Interface/v5',
    'flg': 'http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5'
}

# TIA Portal datatype mapping to SCL
DATATYPE_MAPPING = {
    'Bool': 'Bool',
    'Byte': 'Byte',
    'Word': 'Word',
    'DWord': 'DWord',
    'LWord': 'LWord',
    'SInt': 'SInt',
    'Int': 'Int',
    'DInt': 'DInt',
    'LInt': 'LInt',
    'USInt': 'USInt',
    'UInt': 'UInt',
    'UDInt': 'UDInt',
    'ULInt': 'ULInt',
    'Real': 'Real',
    'LReal': 'LReal',
    'Time': 'Time',
    'LTime': 'LTime',
    'Date': 'Date',
    'TOD': 'Time_Of_Day',
    'LTOD': 'LTime_Of_Day',
    'DT': 'Date_And_Time',
    'DTL': 'DTL',
    'LDT': 'LDT',
    'String': 'String',
    'WString': 'WString',
    'Char': 'Char',
    'WChar': 'WChar',
    'Struct': 'Struct',
    'Array': 'Array',
    'Void': 'Void'
}

# SCL reserved keywords that need escaping with quotes
SCL_RESERVED_KEYWORDS = {
    'AND', 'OR', 'XOR', 'NOT', 'MOD', 'DIV',
    'IF', 'THEN', 'ELSE', 'ELSIF', 'END_IF',
    'CASE', 'OF', 'END_CASE',
    'FOR', 'TO', 'BY', 'DO', 'END_FOR',
    'WHILE', 'END_WHILE',
    'REPEAT', 'UNTIL', 'END_REPEAT',
    'FUNCTION', 'FUNCTION_BLOCK', 'END_FUNCTION', 'END_FUNCTION_BLOCK',
    'TYPE', 'END_TYPE', 'STRUCT', 'END_STRUCT',
    'VAR', 'VAR_INPUT', 'VAR_OUTPUT', 'VAR_IN_OUT', 'VAR_TEMP', 'VAR_STAT',
    'END_VAR', 'CONST', 'RETAIN', 'NON_RETAIN',
    'AT', 'BEGIN', 'RETURN', 'EXIT', 'CONTINUE',
    'TRUE', 'FALSE', 'NULL'
}

# Default configuration
DEFAULT_CONFIG = {
    'scl_indent': '   ',  # 3 spaces (TIA Portal standard)
    'preserve_comments': True,
    'extract_language': 'en-US',  # Default language for multilingual texts
    'generate_headers': True,
    'optimize_access': True,
    'log_level': logging.INFO
}



import json
import glob
import os

def load_fb_signatures_from_reference() -> Dict[str, Dict]:
    """
    Dynamically load FB signatures from 'SCL Syntax/scl-reference/functions' JSON files.
    Returns dictionary in format: 
    { 'BlockName': { 'ParamName': 'Type' or ('Type', 'Default') } }
    """
    signatures = {}
    
    # Path relative to this config.py file
    base_dir = Path(__file__).parent
    ref_dir = base_dir / 'SCL Syntax' / 'scl-reference' / 'functions'
    
    # Check if directory exists (in case project structure is different during tests)
    if not ref_dir.exists():
        logging.getLogger(__name__).warning(f"SCL Reference directory not found at {ref_dir}. Using empty signatures.")
        return {}

    # Find all JSON files
    json_files = glob.glob(str(ref_dir / "*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if 'functions' not in data:
                continue
                
            for func in data['functions']:
                block_name = func.get('name')
                if not block_name: continue
                
                params = {}
                if 'parameters' in func:
                    for p in func['parameters']:
                        p_name = p.get('name')
                        p_type = p.get('type', 'Void')
                        p_default = p.get('default')
                        
                        # Store as tuple (Type, Default) if default exists, else just Type
                        if p_default is not None:
                            params[p_name] = (p_type, p_default)
                        else:
                            params[p_name] = p_type
                            
                signatures[block_name] = params
                
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to load signatures from {json_file}: {e}")
            
    return signatures

# Load signatures dynamically
FB_SIGNATURES = load_fb_signatures_from_reference()


# Fallback/Hardcoded Signatures (if loading fails or for critical overrides)
if not FB_SIGNATURES:
    # Minimal fallback for bootstrapping if files are missing
    FB_SIGNATURES = {
        'TON': {'IN': 'Bool', 'PT': 'Time'},
        'CTU': {'CU': 'Bool', 'R': ('Bool', 'FALSE'), 'PV': ('Int', '0')}
    }


class Config:
    """Configuration class for parser settings"""
    
    def __init__(self, **kwargs):
        self.settings = DEFAULT_CONFIG.copy()
        self.settings.update(kwargs)
        
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.settings[key] = value
    
    @property
    def fb_signatures(self) -> Dict[str, Dict]:
        """Get FB signatures mapping"""
        return FB_SIGNATURES
        
    @property
    def indent(self) -> str:
        """Get indentation string"""
        return self.settings['scl_indent']
    
    @property
    def language(self) -> str:
        """Get extraction language"""
        return self.settings['extract_language']


# Global configuration instance
config = Config()
