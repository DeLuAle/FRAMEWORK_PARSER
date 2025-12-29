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
    def indent(self) -> str:
        """Get indentation string"""
        return self.settings['scl_indent']
    
    @property
    def language(self) -> str:
        """Get extraction language"""
        return self.settings['extract_language']


# Global configuration instance
config = Config()
