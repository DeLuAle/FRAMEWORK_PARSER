"""
PLC Tag Generator - Exports tags to CSV/Text format compatible with TIA Portal Import
"""

import logging
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class PLCTagGenerator:
    """Generates TIA Portal compatible tag import files (SDF/CSV style)."""
    
    def __init__(self, tags: List[Dict[str, str]]):
        self.tags = tags
        
    def generate(self, output_file: Path):
        """
        Generate tag file.
        Format: "Name","Path","DataType","LogicalAddress","Comment",[...others...]
        """
        logger.info(f"Generating tag file: {output_file}")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # SDA/SDF format usually requires specific headers, but simple CSV often works for simple lists.
                # Let's try a standard CSV format: Name, Path, DataType, LogicalAddress, Comment
                # Usually TIA exports have specific headers.
                
                # Header? TIA variable import format usually accepts:
                # Name, Path, DataType, LogicalAddress, Comment
                # But let's check what user wants. Implementation plan said: 
                # "Name; DataType; Address; Comment"
                
                # Let's stick to a simple readable CSV
                f.write("Name;DataType;LogicalAddress;Comment\n")
                
                for tag in self.tags:
                    if tag.get('type') == 'tag':
                        name = tag.get('name', '')
                        dtype = tag.get('data_type', '')
                        addr = tag.get('logical_address', '')
                        comment = tag.get('comment', '').replace('\n', ' ').replace(';', ',')
                        
                        f.write(f"{name};{dtype};{addr};{comment}\n")
                        
                    elif tag.get('type') == 'constant':
                        # Constants might be different?
                        # Name, DataType, Value, Comment
                        name = tag.get('name', '')
                        dtype = tag.get('data_type', '')
                        value = tag.get('value', '').replace(';', ',')
                        comment = tag.get('comment', '').replace('\n', ' ').replace(';', ',')
                        
                        # We use 'CONSTANT' as address marker or similar?
                        # Or just append them with Value in Address field?
                        f.write(f"{name};{dtype};{value};{comment}\n")
                        
            logger.info("Tag generation completed.")
            
        except Exception as e:
            logger.error(f"Failed to generate tag file: {e}")
            raise
