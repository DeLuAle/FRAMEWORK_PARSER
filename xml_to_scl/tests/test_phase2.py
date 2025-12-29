
import unittest
import xml.etree.ElementTree as ET
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lad_parser import LADLogicParser

class TestPhase2(unittest.TestCase):
    
    def test_label_parsing(self):
        """Test parsing of Label part"""
        xml = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet>
                    <Parts>
                        <Part UId="10" Name="Label">
                            <TemplateValue Name="Name" Type="Type">MyLabel</TemplateValue>
                        </Part>
                    </Parts>
                    <Wires />
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """
        root = ET.fromstring(xml)
        parser = LADLogicParser(root)
        parser.parse()
        ops = parser._extract_operations()
        
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0]['type'], 'label_definition')
        self.assertEqual(ops[0]['label'], 'MyLabel')

    def test_jump_parsing(self):
        """Test parsing of Jmp part"""
        xml = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet>
                    <Parts>
                        <Part UId="20" Name="Jmp">
                            <TemplateValue Name="Target" Type="Type">DestLabel</TemplateValue>
                        </Part>
                        <Part UId="5" Name="Coil">
                            <TemplateValue Name="Card" Type="Cardinality">1</TemplateValue>
                        </Part>
                    </Parts>
                    <Wires>
                        <Wire UId="30">
                            <!-- Helper wire to see if it picks up Powerrail/True as default if missing -->
                            <NameCon UId="20" Name="en" />
                            <!-- Connected to nothing means default TRUE? Let's assume connected to Powerrail implied -->
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """
        root = ET.fromstring(xml)
        parser = LADLogicParser(root)
        
        # Mock connections for 'en'
        parser.connections = {
            ('20', 'en'): {'type': 'Powerrail', 'uid': '0'}
        }
        
        # Manually part parsing not fully needed if we test _extract_operations on injected parts
        parser.parts = {
            '20': {'part_type': 'Jmp', 'template_values': {'Target': 'DestLabel'}},
            '5': {'part_type': 'Coil'}
        }
        
        ops = parser._extract_operations()
        # Should find Jmp
        jmp = next((op for op in ops if op['type'] == 'jump'), None)
        self.assertIsNotNone(jmp)
        self.assertEqual(jmp['target'], 'DestLabel')
        self.assertEqual(jmp['condition'], 'TRUE')

    def test_return_parsing(self):
        """Test parsing of Return"""
        parser = LADLogicParser(ET.Element('root'))
        parser.parts = {
            '50': {'part_type': 'Return'}
        }
        parser.connections = {} # No connection = True? No, default resolve returns ??? if missing.
        # But our code says: en_expr = self._resolve_input_connection(en_conn) if en_conn else 'TRUE'
        
        ops = parser._extract_operations()
        ret = next((op for op in ops if op['type'] == 'return'), None)
        self.assertIsNotNone(ret)
        self.assertEqual(ret['condition'], 'TRUE')

if __name__ == '__main__':
    unittest.main()
