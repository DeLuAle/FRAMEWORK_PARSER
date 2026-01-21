"""
Main CLI Application for XML to SCL conversion.
Scans a directory structure, identifies TIA Portal XML files, and converts them to SCL/CSV.
"""

import os
import sys
import argparse
import logging
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET

# Setup path to import local modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from utils import setup_logging
from fbfc_parser import FBFCParser
from fbfc_generator import FBFCGenerator
from db_parser import DBParser
from db_generator import DBGenerator
from udt_parser import UDTParser
from udt_generator import UDTGenerator
from plc_tag_parser import PLCTagParser
from plc_tag_generator import PLCTagGenerator

logger = logging.getLogger(__name__)

def identify_file_type(file_path: Path) -> str:
    """Identify XML file type based on content or filename."""
    try:
        suffix = file_path.suffix.lower()

        # NUOVO: Identifica file SCL da copiare
        if suffix == '.scl':
            return 'scl_copy'

        # Check extension
        if suffix != '.xml':
            return None

        # Check filename patterns first (fastest)
        name = file_path.name.lower()
        if 'tag table' in name:
            return 'tags'
            
        # Peek into XML root
        try:
            # We parse only the start to find the root tag
            for event, elem in ET.iterparse(str(file_path), events=('start',)):
                tag = elem.tag.split('}')[-1] # Remove namespace
                
                if tag == 'PlcUserDataType': # Or ArrayOfPlcUserDataType?
                    return 'udt'
                elif 'PlcUserDataType' in tag: # Catch wrapper
                     return 'udt'
                elif tag == 'GlobalDB' or tag == 'InstanceDB':
                    return 'db'
                elif tag == 'FB':
                    return 'fb'
                elif tag == 'FC':
                    return 'fc'
                elif tag == 'PlcTagTable':
                    return 'tags'
                
                # Check root document type if generic
                if tag == 'Document':
                    continue # Keep looking for children
                    
                # If we find SW.Blocks...
                if 'SW.Blocks.FB' in elem.tag: return 'fb'
                if 'SW.Blocks.FC' in elem.tag: return 'fc'
                if 'SW.Blocks.GlobalDB' in elem.tag or 'SW.Blocks.InstanceDB' in elem.tag: return 'db'
                if 'SW.Types.PlcStruct' in elem.tag: return 'udt' # TIA UDTs
                if 'SW.Tags.PlcTagTable' in elem.tag: return 'tags'

                # If we went deep enough without finding known type, stop
                # (Simple heuristic: if not in first few elements, probably not what we want)
                # But iterparse is stream, so we can just break for optimization if we want,
                # but let's let it run a bit or check children of Document.
                
                # For this implementation, we rely on the Parser classes' robustness too, 
                # but we need to know WHICH parser to call.
                
                # Let's try reading the whole file string for keywords if parsing fails? 
                # No, XML parsing is safer.
                
                pass
                
        except ET.ParseError:
            return None

        # Fallback: Read file content as string with error handling
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(2048) # Read header
                if 'SW.Blocks.FB' in content or 'BlockType="FB"' in content: return 'fb'
                if 'SW.Blocks.FC' in content or 'BlockType="FC"' in content: return 'fc'
                if 'SW.Blocks.GlobalDB' in content or 'SW.Blocks.InstanceDB' in content: return 'db'
                if 'SW.Types.PlcStruct' in content or 'PlcUserDataType' in content: return 'udt'
                if 'SW.Tags.PlcTagTable' in content: return 'tags'
        except UnicodeDecodeError as e:
            logger.warning(f"Encoding error reading {file_path}: {e}")
            return None
        except FileNotFoundError as e:
            logger.debug(f"File not found during identification: {file_path}")
            return None

    except Exception as e:
        logger.debug(f"Error identifying {file_path}: {e}")
        return None
        
    return None

def process_file(file_path: Path, output_dir: Path):
    """Process a single file."""
    ftype = identify_file_type(file_path)
    if not ftype:
        return

    logger.info(f"Processing {ftype.upper()}: {file_path.name}")
    
    try:
        output_file = None

        # NUOVO: Handler per copia file SCL
        if ftype == 'scl_copy':
            # Copia file SCL mantenendo nome e metadata
            output_file = output_dir / file_path.name
            shutil.copy2(file_path, output_file)
            logger.info(f"Copied SCL file to: {output_file}")
            return

        if ftype in ['fb', 'fc']:
            parser = FBFCParser(file_path)
            data = parser.parse()
            generator = FBFCGenerator(data)
            output_file = output_dir / f"{data.get('name', file_path.stem)}.scl"
            generator.generate(output_file)
            
        elif ftype == 'db':
            parser = DBParser(file_path)
            data = parser.parse()
            generator = DBGenerator(data)
            output_file = output_dir / f"{data.get('name', file_path.stem)}.db"
            generator.generate(output_file)
            
        elif ftype == 'udt':
            parser = UDTParser(file_path)
            data = parser.parse()
            generator = UDTGenerator(data)
            output_file = output_dir / f"{data.get('name', file_path.stem)}.udt"
            generator.generate(output_file)
            
        elif ftype == 'tags':
            parser = PLCTagParser()
            tags = parser.parse(file_path)
            # Tag generator works on list of tags
            generator = PLCTagGenerator(tags)
            output_file = output_dir / f"{file_path.stem}.csv"
            generator.generate(output_file)

        if output_file:
            logger.info(f"Generated: {output_file}")

    except FileNotFoundError as e:
        logger.error(f"File not found during processing {file_path.name}: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied accessing {file_path.name}: {e}")
    except ValueError as e:
        logger.error(f"Invalid data format in {file_path.name}: {e}")
    except Exception as e:
        logger.error(f"Failed to process {file_path.name}: {e}")
        # import traceback
        # traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="TIA Portal XML to SCL Converter")
    parser.add_argument("source", nargs='?', default=os.getcwd(), help="Input directory")
    parser.add_argument("--output", "-o", default="output", help="Output directory")
    parser.add_argument("--recursive", "-r", action="store_true", default=True, help="Scan recursively")
    parser.add_argument("--type", choices=['all', 'udt', 'db', 'fb', 'fc', 'tags'], default='all', help="Filter types")
    
    args = parser.parse_args()
    
    setup_logging()
    
    source_path = Path(args.source)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not source_path.exists():
        logger.error(f"Source path not found: {source_path}")
        return

    logger.info(f"Scanning {source_path}...")
    
    files_processed = 0
    
    if source_path.is_file():
        process_file(source_path, output_path)
        files_processed = 1
    else:
        # Walk directory
        for root, dirs, files in os.walk(source_path):
            for file in files:
                if not file.lower().endswith('.xml'):
                    continue
                
                file_path = Path(root) / file
                process_file(file_path, output_path)
                files_processed += 1
                
            if not args.recursive:
                break
                
    logger.info(f"Conversion complete. Processed {files_processed} files.")

if __name__ == "__main__":
    main()
