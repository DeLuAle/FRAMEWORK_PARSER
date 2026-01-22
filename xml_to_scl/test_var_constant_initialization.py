"""
Test VAR CONSTANT initialization
Tests that VAR CONSTANT members always have initialization values,
either from XML StartValue or from default values for the type.
"""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from fbfc_generator import FBFCGenerator
from fbfc_parser import FBFCParser


class TestVarConstantInitialization(unittest.TestCase):
    """Test that VAR CONSTANT always has initialization values"""

    def test_constant_with_startvalue_from_xml(self):
        """Test: Constant with StartValue in XML gets correct value"""
        # Create minimal XML with VAR CONSTANT containing StartValue
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <SW.Blocks.FB ID="0">
    <AttributeList>
      <Name>TestFB</Name>
      <ProgrammingLanguage>LAD</ProgrammingLanguage>
      <Interface>
        <Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
          <Section Name="Constant">
            <Member Name="PI" Datatype="Real">
              <StartValue>3.14159</StartValue>
            </Member>
            <Member Name="MAX_COUNT" Datatype="Int">
              <StartValue>100</StartValue>
            </Member>
            <Member Name="ENABLED" Datatype="Bool">
              <StartValue>TRUE</StartValue>
            </Member>
          </Section>
        </Sections>
      </Interface>
    </AttributeList>
  </SW.Blocks.FB>
</Document>'''

        # Parse and generate
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = Path(f.name)

        try:
            parser = FBFCParser(temp_path)
            parsed_data = parser.parse()

            # Check that start_value was extracted
            constants = parsed_data['interface'].get('Constant', [])
            self.assertEqual(len(constants), 3)

            # Verify each constant has start_value
            pi_const = next(c for c in constants if c['name'] == 'PI')
            self.assertEqual(pi_const.get('start_value'), '3.14159')

            max_count_const = next(c for c in constants if c['name'] == 'MAX_COUNT')
            self.assertEqual(max_count_const.get('start_value'), '100')

            enabled_const = next(c for c in constants if c['name'] == 'ENABLED')
            self.assertEqual(enabled_const.get('start_value'), 'TRUE')

            # Generate SCL
            generator = FBFCGenerator(parsed_data)
            scl_code = generator.generate()

            # Verify SCL has correct initialization
            self.assertIn('PI : Real := 3.14159;', scl_code)
            self.assertIn('MAX_COUNT : Int := 100;', scl_code)
            self.assertIn('ENABLED : Bool := TRUE;', scl_code)

        finally:
            temp_path.unlink()

    def test_constant_without_startvalue_gets_default(self):
        """Test: Constant without StartValue gets default value for type"""
        # Create minimal XML with VAR CONSTANT WITHOUT StartValue
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <SW.Blocks.FB ID="0">
    <AttributeList>
      <Name>TestFB</Name>
      <ProgrammingLanguage>LAD</ProgrammingLanguage>
      <Interface>
        <Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
          <Section Name="Constant">
            <Member Name="DEFAULT_BOOL" Datatype="Bool" />
            <Member Name="DEFAULT_INT" Datatype="Int" />
            <Member Name="DEFAULT_REAL" Datatype="Real" />
            <Member Name="DEFAULT_TIME" Datatype="Time" />
            <Member Name="DEFAULT_STRING" Datatype="String" />
          </Section>
        </Sections>
      </Interface>
    </AttributeList>
  </SW.Blocks.FB>
</Document>'''

        # Parse and generate
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = Path(f.name)

        try:
            parser = FBFCParser(temp_path)
            parsed_data = parser.parse()

            # Generate SCL
            generator = FBFCGenerator(parsed_data)
            scl_code = generator.generate()

            # Verify SCL has default initialization values
            self.assertIn('DEFAULT_BOOL : Bool := FALSE;', scl_code)
            self.assertIn('DEFAULT_INT : Int := 0;', scl_code)
            self.assertIn('DEFAULT_REAL : Real := 0.0;', scl_code)
            self.assertIn('DEFAULT_TIME : Time := T#0ms;', scl_code)
            self.assertIn("DEFAULT_STRING : String := '';", scl_code)

        finally:
            temp_path.unlink()

    def test_no_uninitialized_constants(self):
        """Test: VAR CONSTANT never generated without initialization"""
        # Create XML with mixed constants (some with StartValue, some without)
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <SW.Blocks.FB ID="0">
    <AttributeList>
      <Name>TestFB</Name>
      <ProgrammingLanguage>LAD</ProgrammingLanguage>
      <Interface>
        <Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
          <Section Name="Constant">
            <Member Name="WITH_VALUE" Datatype="Int">
              <StartValue>42</StartValue>
            </Member>
            <Member Name="WITHOUT_VALUE" Datatype="Int" />
          </Section>
        </Sections>
      </Interface>
    </AttributeList>
  </SW.Blocks.FB>
</Document>'''

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = Path(f.name)

        try:
            parser = FBFCParser(temp_path)
            parsed_data = parser.parse()

            generator = FBFCGenerator(parsed_data)
            scl_code = generator.generate()

            # Find VAR CONSTANT section
            lines = scl_code.split('\n')
            in_var_constant = False
            constant_lines = []

            for line in lines:
                if 'VAR CONSTANT' in line:
                    in_var_constant = True
                elif 'END_VAR' in line and in_var_constant:
                    break
                elif in_var_constant:
                    constant_lines.append(line.strip())

            # Check that NO line has variable without ':='
            for line in constant_lines:
                if line and ':' in line and not line.startswith('//'):
                    # This is a variable declaration
                    self.assertIn(':=', line,
                        f"Constant variable declared without initialization: {line}")

            # Verify specific lines
            self.assertIn('WITH_VALUE : Int := 42;', scl_code)
            self.assertIn('WITHOUT_VALUE : Int := 0;', scl_code)

        finally:
            temp_path.unlink()


if __name__ == '__main__':
    unittest.main()
