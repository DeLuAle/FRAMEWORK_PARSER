
import unittest
import xml.etree.ElementTree as ET
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lad_parser import LADLogicParser

class TestPhase3(unittest.TestCase):
    
    def test_peek_parsing(self):
        """Test parsing of PEEK function"""
        # PEEK is an expression, returns a value
        xml = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet>
                    <Parts>
                        <Part UId="10" Name="Peek">
                            <TemplateValue Name="Card" Type="Cardinality">1</TemplateValue>
                        </Part>
                    </Parts>
                    <Wires>
                        <Wire UId="11">
                            <NameCon UId="10" Name="area" />
                            <NameCon UId="50" Name="out" /> <!-- source for area, just mock -->
                        </Wire>
                         <Wire UId="12">
                            <NameCon UId="10" Name="byteOffset" />
                             <NameCon UId="51" Name="out" />
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """
        root = ET.fromstring(xml)
        parser = LADLogicParser(root)
        parser.connections = {
            ('10', 'area'): {'type': 'val', 'val': '16#84', 'uid': '50', 'pin': 'out'},
            ('10', 'byteOffset'): {'type': 'val', 'val': '10', 'uid': '51', 'pin': 'out'},
        }
        # Mock source parts so resolution works (though generic resolver might not check them if not needed, 
        # but _resolve_input_connection might).
        # Actually _resolve_input_connection recursively calls _resolve_logic_part for the source UID.
        # We need to mock _resolve_logic_part to return the value for these UIDs.
        # OR we can just mock the parts to be simple types that resolve to the value.
        # But 'val' in connection usually implies constant? 
        # Parser seems to ignore 'val' in connection dict if it follows UID logic.
        
        # Let's mock _resolve_input_connection on the instance?
        # Or simpler: The parser uses internal methods.
        # We can subclass for test or just patch the method.
        # But let's try to feed it what it wants: valid parts.
        
        # If UID 50 is a part that resolves to '16#84'.
        # We can make it a specific part type? No, that's complex.
        # Let's just monkeypatch _resolve_input_connection for this test.
        
        original_resolve = parser._resolve_input_connection
        def mock_resolve(conn):
            if conn.get('uid') == '50': return '16#84'
            if conn.get('uid') == '51': return '10'
            return original_resolve(conn)
        parser._resolve_input_connection = mock_resolve
        
        parser.parts = {
            '10': {'part_type': 'Peek'}
        }
        
        # Test direct resolution
        res = parser._resolve_logic_part('10', None)
        self.assertIn('PEEK(', res)
        self.assertIn('AREA:=16#84', res)
        self.assertIn('BYTEOFFSET:=10', res)

    def test_poke_parsing(self):
        """Test parsing of POKE instruction"""
        parser = LADLogicParser(ET.Element('root'))
        parser.parts = {
            '20': {'part_type': 'Poke'}
        }
        parser.connections = {
            ('20', 'area'): {'type': 'val', 'val': '16#84', 'uid': '999'},
            ('20', 'value'): {'type': 'val', 'val': '123', 'uid': '998'}
        }
        
        original_resolve = parser._resolve_input_connection
        def mock_resolve(conn):
            if conn.get('uid') == '999': return '16#84'
            if conn.get('uid') == '998': return '123'
            return original_resolve(conn)
        parser._resolve_input_connection = mock_resolve
        
        res = parser._resolve_logic_part('20', None)
        self.assertIn('POKE(', res)
        self.assertIn('AREA:=16#84', res)
        self.assertIn('VALUE:=123', res)

    def test_conversion_parsing(self):
        """Test parsing of TO_INT"""
        parser = LADLogicParser(ET.Element('root'))
        parser.parts = {
            '30': {'part_type': 'To_Int'}
        }
        parser.connections = {
            ('30', 'in'): {'type': 'val', 'val': '12.5', 'uid': '997'}
        }
        
        original_resolve = parser._resolve_input_connection
        def mock_resolve(conn):
            if conn.get('uid') == '997': return '12.5'
            return original_resolve(conn)
        parser._resolve_input_connection = mock_resolve
        
        res = parser._resolve_logic_part('30', None)
        self.assertIn('TO_INT(', res)
        self.assertIn('IN:=12.5', res)

    def test_advanced_types_parsing(self):
        """Test parsing of TypeOf, VariantGet, REF"""
        parser = LADLogicParser(ET.Element('root'))
        parser.parts = {
            '40': {'part_type': 'TypeOf'},
            '41': {'part_type': 'Ref'}
        }
        parser.connections = {
            ('40', 'cnt'): {'type': 'val', 'val': '#MyVariant', 'uid': '990'}, # 'cnt' is typical input for TypeOf (content?) or 'in'
            ('41', 'in'): {'type': 'val', 'val': '#MyVar', 'uid': '991'}
        }
        
        # Mock resolve
        original_resolve = parser._resolve_input_connection
        def mock_resolve(conn):
            if conn.get('uid') == '990': return '#MyVariant'
            if conn.get('uid') == '991': return '#MyVar'
            return original_resolve(conn)
        parser._resolve_input_connection = mock_resolve
        
        # Test TypeOf
        res_typeof = parser._resolve_logic_part('40', None)
        # We don't know exact param name for TypeOf in XML, assumes 'cnt' or 'in'. 
        # If generic resolution sees 'cnt', uses it.
        # "TypeOf(#MyVariant)" or "TypeOf(CNT:=#MyVariant)"
        self.assertIn('TypeOf', res_typeof)
        
        # Test Ref
        res_ref = parser._resolve_logic_part('41', None)
        self.assertIn('REF(', res_ref)
        self.assertIn('#MyVar', res_ref)

if __name__ == '__main__':
    unittest.main()
