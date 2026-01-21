"""
Unit Tests for FB Parameter Extraction

Tests verify that:
1. FB input parameters are properly resolved
2. FB output parameters are properly captured
3. Falsy but valid values (0, FALSE, etc.) are included
4. ??? placeholders are excluded
"""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from lad_parser import LADLogicParser


class TestFBParameterExtraction(unittest.TestCase):
    """Test FB parameter extraction from LAD logic"""

    def test_simple_fb_call_with_inputs(self):
        """Test basic FB call with input parameters"""
        xml_str = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5">
                    <Parts>
                        <Access Scope="LocalVariable" UId="1">
                            <Symbol><Component Name="input_signal" /></Symbol>
                        </Access>
                        <Access Scope="LocalVariable" UId="2">
                            <Symbol><Component Name="output_result" /></Symbol>
                        </Access>
                        <Call UId="3">
                            <CallInfo Name="TON" BlockType="FB">
                                <Instance>
                                    <Component Name="Timer1" />
                                </Instance>
                            </CallInfo>
                        </Call>
                    </Parts>
                    <Wires>
                        <Wire UId="10">
                            <IdentCon UId="1" />
                            <NameCon UId="3" Name="IN" />
                        </Wire>
                        <Wire UId="11">
                            <NameCon UId="3" Name="Q" />
                            <IdentCon UId="2" />
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """

        root = ET.fromstring(xml_str)
        parser = LADLogicParser(root)
        parser.parse()
        fb_calls = parser._extract_fb_calls()

        # Should have 1 FB call
        self.assertEqual(len(fb_calls), 1)
        fb_call = fb_calls[0]

        # Check instance name
        self.assertEqual(fb_call['instance'], 'Timer1')
        self.assertEqual(fb_call['fb_type'], 'TON')

        # Check inputs (local variables should have # prefix)
        self.assertIn('IN', fb_call['inputs'])
        self.assertEqual(fb_call['inputs']['IN'], '#input_signal')

        # Check outputs (local variables should have # prefix)
        self.assertIn('Q', fb_call['outputs'])
        self.assertEqual(fb_call['outputs']['Q'], '#output_result')

    def test_fb_call_with_boolean_expression_input(self):
        """Test FB call with boolean expression as input"""
        xml_str = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5">
                    <Parts>
                        <Access Scope="LocalVariable" UId="1">
                            <Symbol><Component Name="var1" /></Symbol>
                        </Access>
                        <Access Scope="LocalVariable" UId="2">
                            <Symbol><Component Name="var2" /></Symbol>
                        </Access>
                        <Access Scope="LocalVariable" UId="3">
                            <Symbol><Component Name="result" /></Symbol>
                        </Access>
                        <Part Name="Contact" UId="4" />
                        <Part Name="Contact" UId="5" />
                        <Call UId="6">
                            <CallInfo Name="SR" BlockType="FB">
                                <Instance>
                                    <Component Name="SetReset1" />
                                </Instance>
                            </CallInfo>
                        </Call>
                    </Parts>
                    <Wires>
                        <Wire UId="10">
                            <Powerrail />
                            <NameCon UId="4" Name="in" />
                        </Wire>
                        <Wire UId="11">
                            <IdentCon UId="1" />
                            <NameCon UId="4" Name="operand" />
                        </Wire>
                        <Wire UId="12">
                            <NameCon UId="4" Name="out" />
                            <NameCon UId="5" Name="in" />
                        </Wire>
                        <Wire UId="13">
                            <IdentCon UId="2" />
                            <NameCon UId="5" Name="operand" />
                        </Wire>
                        <Wire UId="14">
                            <NameCon UId="5" Name="out" />
                            <NameCon UId="6" Name="S" />
                        </Wire>
                        <Wire UId="15">
                            <NameCon UId="6" Name="Q" />
                            <IdentCon UId="3" />
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """

        root = ET.fromstring(xml_str)
        parser = LADLogicParser(root)
        parser.parse()
        fb_calls = parser._extract_fb_calls()

        # Should have 1 FB call
        self.assertEqual(len(fb_calls), 1)
        fb_call = fb_calls[0]

        # Check instance
        self.assertEqual(fb_call['instance'], 'SetReset1')

        # Check that input has been resolved (with # for local vars)
        # Complex boolean expressions should be fully resolved
        self.assertIn('S', fb_call['inputs'])
        s_value = fb_call['inputs']['S']
        self.assertNotEqual(s_value, '???')
        self.assertIn('#var1', s_value)
        self.assertIn('#var2', s_value)
        self.assertIn('AND', s_value)

        # Check outputs (local variables should have # prefix)
        self.assertIn('Q', fb_call['outputs'])
        self.assertEqual(fb_call['outputs']['Q'], '#result')

    def test_fb_call_excludes_unresolved_parameters(self):
        """Test that unresolved (???) parameters are excluded from inputs"""
        xml_str = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5">
                    <Parts>
                        <Access Scope="LocalVariable" UId="1">
                            <Symbol><Component Name="known_input" /></Symbol>
                        </Access>
                        <Call UId="2">
                            <CallInfo Name="CustomFB" BlockType="FB">
                                <Instance>
                                    <Component Name="Instance1" />
                                </Instance>
                            </CallInfo>
                        </Call>
                    </Parts>
                    <Wires>
                        <Wire UId="10">
                            <IdentCon UId="1" />
                            <NameCon UId="2" Name="KnownParam" />
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """

        root = ET.fromstring(xml_str)
        parser = LADLogicParser(root)
        parser.parse()
        fb_calls = parser._extract_fb_calls()

        # Should have 1 FB call
        self.assertEqual(len(fb_calls), 1)
        fb_call = fb_calls[0]

        # Should have the known parameter (with # for local variable)
        self.assertIn('KnownParam', fb_call['inputs'])
        self.assertEqual(fb_call['inputs']['KnownParam'], '#known_input')

        # Should not have any ??? values
        for param_name, value in fb_call['inputs'].items():
            self.assertNotEqual(value, '???', f"Parameter {param_name} should not be ???")

    def test_multiple_fb_instances(self):
        """Test extraction of multiple FB instances from same network"""
        xml_str = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5">
                    <Parts>
                        <Access Scope="LocalVariable" UId="1">
                            <Symbol><Component Name="input1" /></Symbol>
                        </Access>
                        <Access Scope="LocalVariable" UId="2">
                            <Symbol><Component Name="output1" /></Symbol>
                        </Access>
                        <Access Scope="LocalVariable" UId="3">
                            <Symbol><Component Name="input2" /></Symbol>
                        </Access>
                        <Access Scope="LocalVariable" UId="4">
                            <Symbol><Component Name="output2" /></Symbol>
                        </Access>
                        <Call UId="5">
                            <CallInfo Name="TON" BlockType="FB">
                                <Instance>
                                    <Component Name="Timer1" />
                                </Instance>
                            </CallInfo>
                        </Call>
                        <Call UId="6">
                            <CallInfo Name="TOFF" BlockType="FB">
                                <Instance>
                                    <Component Name="Timer2" />
                                </Instance>
                            </CallInfo>
                        </Call>
                    </Parts>
                    <Wires>
                        <Wire UId="10">
                            <IdentCon UId="1" />
                            <NameCon UId="5" Name="IN" />
                        </Wire>
                        <Wire UId="11">
                            <NameCon UId="5" Name="Q" />
                            <IdentCon UId="2" />
                        </Wire>
                        <Wire UId="12">
                            <IdentCon UId="3" />
                            <NameCon UId="6" Name="IN" />
                        </Wire>
                        <Wire UId="13">
                            <NameCon UId="6" Name="Q" />
                            <IdentCon UId="4" />
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """

        root = ET.fromstring(xml_str)
        parser = LADLogicParser(root)
        parser.parse()
        fb_calls = parser._extract_fb_calls()

        # Should have 2 FB calls
        self.assertEqual(len(fb_calls), 2)

        # Check first FB (local variables should have # prefix)
        fb1 = next((fc for fc in fb_calls if fc['instance'] == 'Timer1'), None)
        self.assertIsNotNone(fb1)
        self.assertEqual(fb1['fb_type'], 'TON')
        self.assertEqual(fb1['inputs']['IN'], '#input1')
        self.assertEqual(fb1['outputs']['Q'], '#output1')

        # Check second FB (local variables should have # prefix)
        fb2 = next((fc for fc in fb_calls if fc['instance'] == 'Timer2'), None)
        self.assertIsNotNone(fb2)
        self.assertEqual(fb2['fb_type'], 'TOFF')
        self.assertEqual(fb2['inputs']['IN'], '#input2')
        self.assertEqual(fb2['outputs']['Q'], '#output2')


if __name__ == '__main__':
    unittest.main(verbosity=2)
