
import unittest
import xml.etree.ElementTree as ET
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lad_parser import LADLogicParser

class TestPhase1(unittest.TestCase):
    
    def test_slice_access(self):
        """Test parsing of Tag.X0 via Token parsing logic"""
        # Create a mock FlgNet/Parts/Access structure
        xml = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet>
                    <Parts>
                        <Access UId="1" Scope="GlobalVariable">
                            <Symbol>
                                <Component Name="MyTag" />
                                <Token Text="." />
                                <Token Text="%X0" />
                            </Symbol>
                        </Access>
                    </Parts>
                    <Wires />
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """
        root = ET.fromstring(xml)
        parser = LADLogicParser(root)
        parser.parse() # Triggers _parse_parts
        
        part = parser.parts.get('1')
        self.assertIsNotNone(part)
        self.assertEqual(part.get('name'), 'MyTag.%X0')
        print(f"Parsed Name: {part.get('name')}")

    def test_pcontact_instance(self):
        """Test PContact resolution with Instance"""
        xml = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet>
                    <Parts>
                        <Part UId="2" Name="PContact">
                            <Instance>
                                <Component Name="R_TRIG_DB" />
                            </Instance>
                        </Part>
                    </Parts>
                    <Wires>
                         <!-- Dummy wire to check logic resolution -->
                         <Wire UId="10">
                            <NameCon UId="2" Name="out" />
                            <NameCon UId="3" Name="in" />
                         </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """
        root = ET.fromstring(xml)
        parser = LADLogicParser(root)
        parser.parse()
        
        # Manually invoke _resolve_logic_part since we don't have full connection graph for automatic testing
        # We need to simulate the connections dict being populated
        # _parse_wires called in parse() should have populated connections if wires existed.
        # But we need to call _resolve_logic_part('2', 'out')
        
        # Let's see if we can just test _resolve_logic_part directly
        result = parser._resolve_logic_part('2', 'out')
        self.assertEqual(result, '#R_TRIG_DB.Q')
        print(f"Resolved PContact: {result}")

    def test_pcontact_legacy(self):
        """Test PContact resolution without Instance (Legacy)"""
        xml = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet>
                    <Parts>
                        <Part UId="3" Name="PContact">
                           <Negated Name="operand"/>
                        </Part>
                        <Access UId="4" Scope="GlobalVariable">
                            <Symbol><Component Name="MemoryBit"/></Symbol>
                        </Access>
                    </Parts>
                    <Wires>
                        <Wire UId="20">
                             <IdentCon UId="4" />
                             <NameCon UId="3" Name="operand" />
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """
        root = ET.fromstring(xml)
        parser = LADLogicParser(root)
        parser.parse()
        
        # Verify operand connection existence
        # self.assertTrue(parser.connections.get(('3', 'operand')))
        
        result = parser._resolve_logic_part('3', 'out')
        # Expect PosEdge(MemoryBit)
        self.assertEqual(result, 'PosEdge(MemoryBit)')
        print(f"Resolved Legacy PContact: {result}")

if __name__ == '__main__':
    unittest.main()
