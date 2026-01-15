import unittest
import logging
import xml.etree.ElementTree as ET
from lad_parser import LADLogicParser
from config import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class TestWeaknessFixes(unittest.TestCase):
    
    def setUp(self):
        # Base XML skeleton
        self.ns = {'flg': 'http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5'}
        ET.register_namespace('flg', self.ns['flg'])
        
    def create_compile_unit(self, parts_xml, wires_xml):
        """Helper to create the ET structure"""
        xml_str = f"""
        <CompileUnit xmlns:flg="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5">
            <AttributeList>
                <NetworkSource>
                    <flg:FlgNet>
                        <flg:Parts>
                            {parts_xml}
                        </flg:Parts>
                        <flg:Wires>
                            {wires_xml}
                        </flg:Wires>
                    </flg:FlgNet>
                </NetworkSource>
            </AttributeList>
        </CompileUnit>
        """
        return ET.fromstring(xml_str)

    def test_w4_w7_system_defaults(self):
        """Verify W4/W7: Default parameters are injected for missing optionals"""
        
        parts = """
        <flg:Part UId="1" Name="TSEND_C">
            <flg:TemplateValue Name="Card" Type="Cardinality">1</flg:TemplateValue>
            <flg:Instance Scope="GlobalVariable" UId="99">
                <flg:Component Name="instTSEND_C" />
            </flg:Instance>
        </flg:Part>
        """
        
        # Wire Powerrail -> TSEND_C.REQ
        wires = """
        <flg:Wire UId="11">
            <flg:Powerrail />
            <flg:NameCon UId="1" Name="REQ" />
        </flg:Wire>
        """
        
        # Create Parser
        root = self.create_compile_unit(parts, wires)
        parser = LADLogicParser(root)
        
        # Parse
        fb_calls = parser.parse()
        
        self.assertEqual(len(fb_calls), 1, "Should find 1 FB call")
        tsend = fb_calls[0]
        self.assertEqual(tsend['fb_type'], 'TSEND_C') 
        
        inputs = tsend['inputs']
        print(f"TSEND_C inputs found: {inputs}")
        
        # Verify explicit wire
        self.assertIn('REQ', inputs)
        
        # Verify injected default (W4/W7 Fix)
        # TSEND_C signature has COM_RST with default 'FALSE'
        self.assertIn('COM_RST', inputs, "Missing default for COM_RST")
        self.assertEqual(inputs['COM_RST'], 'FALSE', "Incorrect default for COM_RST")
        
        # Verify Output defaults are NOT injected
        self.assertNotIn('DONE', inputs, "Should NOT inject default for Output DONE")

    def test_ctu_defaults(self):
        """Verify CTU gets defaults (R := FALSE)"""
        parts = """
        <flg:Part UId="1" Name="CTU">
            <flg:TemplateValue Name="Card" Type="Cardinality">1</flg:TemplateValue>
            <flg:Instance Scope="GlobalVariable" UId="98">
                <flg:Component Name="instCTU" />
            </flg:Instance>
        </flg:Part>
        """
        wires = """
        <!-- Minimal wire to CU -->
        <flg:Wire UId="10">
            <flg:Powerrail />
            <flg:NameCon UId="1" Name="CU" />
        </flg:Wire>
        """
        
        root = self.create_compile_unit(parts, wires)
        parser = LADLogicParser(root)
        fb_calls = parser.parse()
        
        self.assertTrue(len(fb_calls) > 0, "CTU not found")
        inputs = fb_calls[0]['inputs']
        print(f"CTU inputs found: {inputs}")
        
        self.assertIn('R', inputs, "CTU should have R injected")
        self.assertEqual(inputs['R'], 'FALSE')
        self.assertIn('PV', inputs, "CTU should have PV injected")
        self.assertEqual(inputs['PV'], '0')

    def test_n1_expression_builder_enabled(self):
        """Verify N1: Expression Builder feature flag is enabled"""
        from lad_parser import EXPRESSION_BUILDER_AVAILABLE
        self.assertTrue(EXPRESSION_BUILDER_AVAILABLE, "Expression Builder should be enabled (N1 Fix)")

if __name__ == '__main__':
    unittest.main()
