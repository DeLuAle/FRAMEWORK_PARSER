"""
Unit Tests for Boolean Expression Builder

Tests LAD to SCL boolean expression reconstruction
"""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from lad_parser import LADLogicParser


class TestBooleanExpressionBuilder(unittest.TestCase):
    """Test boolean expression reconstruction from LAD Parts/Wires"""

    def test_simple_contact_coil_rung(self):
        """Test simple: Powerrail -> Contact -> Coil"""
        # Create minimal LAD XML structure
        xml_str = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5">
                    <Parts>
                        <Access Scope="LocalVariable" UId="1">
                            <Symbol>
                                <Component Name="input_var" />
                            </Symbol>
                        </Access>
                        <Access Scope="LocalVariable" UId="2">
                            <Symbol>
                                <Component Name="output_var" />
                            </Symbol>
                        </Access>
                        <Part Name="Contact" UId="3" />
                        <Part Name="Coil" UId="4" />
                    </Parts>
                    <Wires>
                        <Wire UId="10">
                            <Powerrail />
                            <NameCon UId="3" Name="in" />
                        </Wire>
                        <Wire UId="11">
                            <IdentCon UId="1" />
                            <NameCon UId="3" Name="operand" />
                        </Wire>
                        <Wire UId="12">
                            <NameCon UId="3" Name="out" />
                            <NameCon UId="4" Name="in" />
                        </Wire>
                        <Wire UId="13">
                            <IdentCon UId="2" />
                            <NameCon UId="4" Name="operand" />
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """

        root = ET.fromstring(xml_str)
        parser = LADLogicParser(root)
        # Use parse() which internally calls _parse_parts and _parse_wires
        parser.parse()
        ops = parser._extract_operations()

        # Should have 1 assignment: output_var := input_var
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0]['type'], 'assignment')
        self.assertEqual(ops[0]['variable'], 'output_var')
        self.assertNotIn('???', ops[0]['expression'], f"Expression should not contain '???' but got: {ops[0]['expression']}")

    def test_two_contacts_in_series(self):
        """Test: Powerrail -> Contact1 -> Contact2 -> Coil"""
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
                            <Symbol><Component Name="out" /></Symbol>
                        </Access>
                        <Part Name="Contact" UId="4" />
                        <Part Name="Contact" UId="5" />
                        <Part Name="Coil" UId="6" />
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
                            <NameCon UId="6" Name="in" />
                        </Wire>
                        <Wire UId="15">
                            <IdentCon UId="3" />
                            <NameCon UId="6" Name="operand" />
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """

        root = ET.fromstring(xml_str)
        parser = LADLogicParser(root)
        # Use parse() which internally calls _parse_parts and _parse_wires
        parser.parse()
        ops = parser._extract_operations()

        # Should have 1 assignment with AND expression
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0]['type'], 'assignment')
        self.assertEqual(ops[0]['variable'], 'out')
        # Expression should be "var1 AND var2" (or similar)
        expr = ops[0]['expression']
        self.assertNotIn('???', expr, f"Expression should not contain '???' but got: {expr}")
        self.assertIn('var1', expr)
        self.assertIn('var2', expr)
        self.assertIn('AND', expr)

    def test_two_parallel_contacts_with_or(self):
        """Test: Powerrail -> [Contact1, Contact2] -> OR -> Coil"""
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
                            <Symbol><Component Name="out" /></Symbol>
                        </Access>
                        <Part Name="Contact" UId="4" />
                        <Part Name="Contact" UId="5" />
                        <Part Name="O" UId="6">
                            <TemplateValue Name="Card" Type="Cardinality">2</TemplateValue>
                        </Part>
                        <Part Name="Coil" UId="7" />
                    </Parts>
                    <Wires>
                        <Wire UId="10">
                            <Powerrail />
                            <NameCon UId="4" Name="in" />
                            <NameCon UId="5" Name="in" />
                        </Wire>
                        <Wire UId="11">
                            <IdentCon UId="1" />
                            <NameCon UId="4" Name="operand" />
                        </Wire>
                        <Wire UId="12">
                            <NameCon UId="4" Name="out" />
                            <NameCon UId="6" Name="in1" />
                        </Wire>
                        <Wire UId="13">
                            <IdentCon UId="2" />
                            <NameCon UId="5" Name="operand" />
                        </Wire>
                        <Wire UId="14">
                            <NameCon UId="5" Name="out" />
                            <NameCon UId="6" Name="in2" />
                        </Wire>
                        <Wire UId="15">
                            <NameCon UId="6" Name="out" />
                            <NameCon UId="7" Name="in" />
                        </Wire>
                        <Wire UId="16">
                            <IdentCon UId="3" />
                            <NameCon UId="7" Name="operand" />
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """

        root = ET.fromstring(xml_str)
        parser = LADLogicParser(root)
        # Use parse() which internally calls _parse_parts and _parse_wires
        parser.parse()
        ops = parser._extract_operations()

        # Should have 1 assignment with OR expression
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0]['type'], 'assignment')
        self.assertEqual(ops[0]['variable'], 'out')
        expr = ops[0]['expression']
        self.assertNotIn('???', expr, f"Expression should not contain '???' but got: {expr}")
        self.assertIn('var1', expr)
        self.assertIn('var2', expr)
        self.assertIn('OR', expr)

    def test_negated_contact(self):
        """Test: Powerrail -> NOT Contact -> Coil"""
        xml_str = """
        <CompileUnit>
            <NetworkSource>
                <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5">
                    <Parts>
                        <Access Scope="LocalVariable" UId="1">
                            <Symbol><Component Name="input_var" /></Symbol>
                        </Access>
                        <Access Scope="LocalVariable" UId="2">
                            <Symbol><Component Name="output_var" /></Symbol>
                        </Access>
                        <Part Name="Contact" UId="3">
                            <Negated Name="operand" />
                        </Part>
                        <Part Name="Coil" UId="4" />
                    </Parts>
                    <Wires>
                        <Wire UId="10">
                            <Powerrail />
                            <NameCon UId="3" Name="in" />
                        </Wire>
                        <Wire UId="11">
                            <IdentCon UId="1" />
                            <NameCon UId="3" Name="operand" />
                        </Wire>
                        <Wire UId="12">
                            <NameCon UId="3" Name="out" />
                            <NameCon UId="4" Name="in" />
                        </Wire>
                        <Wire UId="13">
                            <IdentCon UId="2" />
                            <NameCon UId="4" Name="operand" />
                        </Wire>
                    </Wires>
                </FlgNet>
            </NetworkSource>
        </CompileUnit>
        """

        root = ET.fromstring(xml_str)
        parser = LADLogicParser(root)
        # Use parse() which internally calls _parse_parts and _parse_wires
        parser.parse()
        ops = parser._extract_operations()

        # Should have 1 assignment with NOT expression
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0]['type'], 'assignment')
        expr = ops[0]['expression']
        self.assertNotIn('???', expr, f"Expression should not contain '???' but got: {expr}")
        self.assertIn('NOT', expr)
        self.assertIn('input_var', expr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
