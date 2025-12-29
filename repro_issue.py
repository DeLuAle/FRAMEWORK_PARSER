
import xml.etree.ElementTree as ET
from xml_to_scl.lad_parser import LADLogicParser
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# XML of Network 33 from DecoilersHRot_FB
# Using a structure similar to what the parser sees in real life
xml_content = """
<CompileUnit ID="125" CompositionName="CompileUnits">
  <AttributeList>
    <NetworkSource>
      <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5">
        <Parts>
          <Access Scope="LocalVariable" UId="21">
            <Symbol><Component Name="Rotation" /><Component Name="MachineInterface" /></Symbol>
          </Access>
          <Access Scope="LocalVariable" UId="22">
            <Symbol><Component Name="Pivot" /><Component Name="MachineInterface" /></Symbol>
          </Access>
          <Access Scope="LiteralConstant" UId="23">
            <Constant><ConstantType>Bool</ConstantType><ConstantValue>FALSE</ConstantValue></Constant>
          </Access>
          <Access Scope="LiteralConstant" UId="24">
            <Constant><ConstantType>Bool</ConstantType><ConstantValue>FALSE</ConstantValue></Constant>
          </Access>
          <Access Scope="LocalVariable" UId="25">
            <Symbol><Component Name="MachineInterface" /></Symbol>
          </Access>
          <Access Scope="LocalVariable" UId="26">
            <Symbol><Component Name="Warning" /><Component Name="Rotation_NotInPosition" /></Symbol>
          </Access>
          <Access Scope="LocalVariable" UId="27">
            <Symbol><Component Name="Warning" /><Component Name="Pivot_NotWork" /></Symbol>
          </Access>
          <Access Scope="LocalVariable" UId="28">
            <Symbol><Component Name="Warning" /><Component Name="Translation_NotInPosition" /></Symbol>
          </Access>
          <Access Scope="LocalVariable" UId="29">
            <Symbol><Component Name="MachineInterface" /></Symbol>
          </Access>
          <Access Scope="LocalVariable" UId="30">
            <Symbol><Component Name="Translation" /><Component Name="MachineInterface" /></Symbol>
          </Access>
          <Access Scope="LiteralConstant" UId="31">
            <Constant><ConstantType>Bool</ConstantType><ConstantValue>FALSE</ConstantValue></Constant>
          </Access>
          <Access Scope="LocalVariable" UId="32">
            <Symbol><Component Name="MachineInterface" /></Symbol>
          </Access>
          <Call UId="33">
            <CallInfo Name="MachineInterface_2_To_1" BlockType="FC">
              <Parameter Name="MachineInterface_1" Section="Input" Type="&quot;MachineInterface&quot;" />
              <Parameter Name="MachineInterface_2" Section="Input" Type="&quot;MachineInterface&quot;" />
              <Parameter Name="AdditionalAlarms" Section="Input" Type="Bool" />
              <Parameter Name="AdditionalWarnings" Section="Input" Type="Bool" />
              <Parameter Name="Ret_Val" Section="Return" Type="&quot;MachineInterface&quot;" />
            </CallInfo>
          </Call>
          <Part Name="Contact" UId="34"><Negated Name="operand" /></Part>
          <Part Name="Contact" UId="35"><Negated Name="operand" /></Part>
          <Part Name="Contact" UId="36"><Negated Name="operand" /></Part>
          <Part Name="Not" UId="37" />
          <Call UId="38">
            <CallInfo Name="MachineInterface_2_To_1" BlockType="FC">
              <Parameter Name="MachineInterface_1" Section="Input" Type="&quot;MachineInterface&quot;" />
              <Parameter Name="MachineInterface_2" Section="Input" Type="&quot;MachineInterface&quot;" />
              <Parameter Name="AdditionalAlarms" Section="Input" Type="Bool" />
              <Parameter Name="AdditionalWarnings" Section="Input" Type="Bool" />
              <Parameter Name="Ret_Val" Section="Return" Type="&quot;MachineInterface&quot;" />
            </CallInfo>
          </Call>
        </Parts>
        <Wires>
          <Wire UId="39">
            <Powerrail />
            <NameCon UId="33" Name="en" />
            <NameCon UId="38" Name="en" />
            <NameCon UId="34" Name="in" />
          </Wire>
          <Wire UId="40"><IdentCon UId="21" /><NameCon UId="33" Name="MachineInterface_1" /></Wire>
          <Wire UId="41"><IdentCon UId="22" /><NameCon UId="33" Name="MachineInterface_2" /></Wire>
          <Wire UId="42"><IdentCon UId="23" /><NameCon UId="33" Name="AdditionalAlarms" /></Wire>
          <Wire UId="43"><IdentCon UId="24" /><NameCon UId="33" Name="AdditionalWarnings" /></Wire>
          <Wire UId="44"><NameCon UId="33" Name="Ret_Val" /><IdentCon UId="25" /></Wire>
          <Wire UId="45"><IdentCon UId="26" /><NameCon UId="34" Name="operand" /></Wire>
          <Wire UId="46"><NameCon UId="34" Name="out" /><NameCon UId="35" Name="in" /></Wire>
          <Wire UId="47"><IdentCon UId="27" /><NameCon UId="35" Name="operand" /></Wire>
          <Wire UId="48"><NameCon UId="35" Name="out" /><NameCon UId="36" Name="in" /></Wire>
          <Wire UId="49"><IdentCon UId="28" /><NameCon UId="36" Name="operand" /></Wire>
          <Wire UId="50"><NameCon UId="36" Name="out" /><NameCon UId="37" Name="in" /></Wire>
          <Wire UId="51"><NameCon UId="37" Name="out" /><NameCon UId="38" Name="AdditionalWarnings" /></Wire>
          <Wire UId="52"><IdentCon UId="29" /><NameCon UId="38" Name="MachineInterface_1" /></Wire>
          <Wire UId="53"><IdentCon UId="30" /><NameCon UId="38" Name="MachineInterface_2" /></Wire>
          <Wire UId="54"><IdentCon UId="31" /><NameCon UId="38" Name="AdditionalAlarms" /></Wire>
          <Wire UId="55"><NameCon UId="38" Name="Ret_Val" /><IdentCon UId="32" /></Wire>
        </Wires>
      </FlgNet>
    </NetworkSource>
  </AttributeList>
</CompileUnit>
"""

def reproduce():
    root = ET.fromstring(xml_content)
    # The LADLogicParser expects the CompileUnit element
    parser = LADLogicParser(root)
    fb_calls = parser.parse()
    
    print("\n--- FB Calls ---")
    if not fb_calls:
        print("NONE")
    for call in fb_calls:
        print(f"Call: {call['fb_type']} (Instance: {call.get('instance')})")
        print(f"  Inputs: {call['inputs']}")
        print(f"  Outputs: {call['outputs']}")
        
    ops = parser._extract_operations()
    print("\n--- Operations ---")
    if not ops:
        print("NONE")
    for op in ops:
        print(op)

if __name__ == "__main__":
    reproduce()
