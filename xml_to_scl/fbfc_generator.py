"""
FB/FC (Function Block / Function) SCL code generator
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from .scl_generator_base import SCLGeneratorBase
    from .utils import escape_scl_identifier
    from .config import config
except ImportError:
    from scl_generator_base import SCLGeneratorBase
    from utils import escape_scl_identifier
    from config import config

logger = logging.getLogger(__name__)


class FBFCGenerator(SCLGeneratorBase):
    """Generator for FB/FC SCL code"""
    
    def _generate_specific(self):
        """Generate FB/FC-specific SCL code"""
        name = self.data.get('name', 'UnknownBlock')
        block_type = self.data.get('block_type', 'FB')
        
        # Determine block declaration
        if block_type == 'FB':
            self._add_line(f'FUNCTION_BLOCK "{name}"')
        else:  # FC
            # FC needs return type - default to Void if not specified
            return_type = self.data.get('return_type', 'Void')
            self._add_line(f'FUNCTION "{name}" : {return_type}')
        
        # Attributes (after declaration, before VERSION)
        self._generate_attributes()
        
        # Version
        self._generate_version()
        
        # Add title/comment if present
        if 'title' in self.data:
            self._add_comment(self.data['title'])
        
        # Generate interface sections
        interface = self.data.get('interface', {})
        

        # Input section
        if 'Input' in interface and interface['Input']:
            self._indent()
            self._add_line("VAR_INPUT")
            self._indent()
            self._generate_struct_members(interface['Input'], include_values=False)
            self._dedent()
            self._add_line("END_VAR")
            self._dedent()
            self._add_line("")
        
        # Output section
        if 'Output' in interface and interface['Output']:
            self._indent()
            self._add_line("VAR_OUTPUT")
            self._indent()
            self._generate_struct_members(interface['Output'], include_values=False)
            self._dedent()
            self._add_line("END_VAR")
            self._dedent()
            self._add_line("")
        
        # InOut section
        if 'InOut' in interface and interface['InOut']:
            self._indent()
            self._add_line("VAR_IN_OUT")
            self._indent()
            self._generate_struct_members(interface['InOut'], include_values=False)
            self._dedent()
            self._add_line("END_VAR")
            self._dedent()
            self._add_line("")
        
        # Static section (only for FB) - uses VAR not VAR_STATIC
        if block_type == 'FB' and 'Static' in interface and interface['Static']:
            self._indent()
            self._add_line("VAR")
            self._indent()
            self._generate_struct_members(interface['Static'], include_values=False)
            self._dedent()
            self._add_line("END_VAR")
            self._dedent()
            self._add_line("")
        
        # Temp section
        if 'Temp' in interface and interface['Temp']:
            self._indent()
            self._add_line("VAR_TEMP")
            self._indent()
            self._generate_struct_members(interface['Temp'], include_values=False)
            self._dedent()
            self._add_line("END_VAR")
            self._dedent()
            self._add_line("")
        
        # Constant section - TIA Portal uses "VAR CONSTANT" not "CONST"
        if 'Constant' in interface and interface['Constant']:
            self._indent()
            self._add_line("VAR CONSTANT")
            self._indent()
            # Constants must have initialization values
            for member in interface['Constant']:
                self._generate_member_declaration(member, include_value=True)
            self._dedent()
            self._add_line("END_VAR")
            self._dedent()
            self._add_line("")
        
        # Empty line before BEGIN
        self._add_line("")
        
        # BEGIN section with logic placeholder
        self._add_line("BEGIN")
        
        if self.data.get('has_graphical_logic', False):
            prog_lang = self.data.get('programming_language', 'LAD/FBD')
            self._indent()
            # Generate logic from networks
            networks = self.data.get('networks', [])
            fb_calls_legacy = self.data.get('fb_calls', [])

            if networks:
                for i, net in enumerate(networks):
                    net_num = net.get('number', i + 1)
                    title = net.get('title', '').strip()
                    comment = net.get('comment', '').strip()
                    
                    # Determine Region Name
                    region_name = title if title else f"Network {net_num}"
                    
                    self._add_line(f'REGION "{region_name}"')
                    self._indent()

                    if comment:
                         # Fix: Extract replace() outside f-string to avoid backslash in f-string
                         formatted_comment = comment.replace("\n", "\n// ")
                         self._add_line(f'// {formatted_comment}')
                         self._add_line('')

                    if net['type'] == 'SCL':
                        code = net.get('code', '')
                        if code:
                            for line in code.splitlines():
                                self._add_line(line)
                            self._add_line("")
                            
                    elif net['type'] == 'LAD':
                        calls = net.get('fb_calls', [])
                        if calls:
                            # self._add_comment(f"FB calls extracted from LAD")
                            for fb_call in calls:
                                self._generate_single_fb_call(fb_call)
                                
                        logic_ops = net.get('logic_ops', [])
                        for op in logic_ops:
                            op_type = op['type']
                            if op_type == 'assignment':
                                self._add_line(f"{op['variable']} := {op['expression']};")
                            elif op_type == 'set':
                                self._add_line(f"IF {op['condition']} THEN")
                                self._indent()
                                self._add_line(f"{op['variable']} := TRUE;")
                                self._dedent()
                                self._add_line("END_IF;")
                            elif op_type == 'reset':
                                self._add_line(f"IF {op['condition']} THEN")
                                self._indent()
                                self._add_line(f"{op['variable']} := FALSE;")
                                self._dedent()
                                self._add_line("END_IF;")
                            elif op_type == 'sr':
                                self._add_line(f"IF {op['r_expr']} THEN")
                                self._indent()
                                self._add_line(f"{op['variable']} := FALSE;")
                                self._dedent()
                                self._add_line(f"ELSIF {op['s_expr']} THEN")
                                self._indent()
                                self._add_line(f"{op['variable']} := TRUE;")
                                self._dedent()
                                self._add_line("END_IF;")
                            elif op_type == 'rs':
                                self._add_line(f"IF {op['s_expr']} THEN")
                                self._indent()
                                self._add_line(f"{op['variable']} := TRUE;")
                                self._dedent()
                                self._add_line(f"ELSIF {op['r_expr']} THEN")
                                self._indent()
                                self._add_line(f"{op['variable']} := FALSE;")
                                self._dedent()
                                self._add_line("END_IF;")
                            elif op_type == 'move':
                                en = op.get('en_expr')
                                if en == '???':
                                    # N2 Fix: Unresolved logic - skip operation with warning comment
                                    self._add_line(f"// WARNING: Unresolved enable logic - operation skipped")
                                    self._add_line(f"// TODO: Manually verify: {op['dest']} := {op['source']}")
                                elif en and en != 'TRUE':
                                    self._add_line(f"IF {en} THEN")
                                    self._indent()
                                    self._add_line(f"{op['dest']} := {op['source']};")
                                    self._dedent()
                                    self._add_line("END_IF;")
                                else:
                                    # en is TRUE or empty -> unconditional execution
                                    self._add_line(f"{op['dest']} := {op['source']};")
                            elif op_type == 'instruction_assignment':
                                en = op.get('en_expr')
                                if en == '???':
                                    # N2 Fix: Unresolved logic - skip operation with warning comment
                                    self._add_line(f"// WARNING: Unresolved enable logic - operation skipped")
                                    self._add_line(f"// TODO: Manually verify: {op['variable']} := {op['expression']}")
                                elif en and en != 'TRUE':
                                    self._add_line(f"IF {en} THEN")
                                    self._indent()
                                    self._add_line(f"{op['variable']} := {op['expression']};")
                                    self._dedent()
                                    self._add_line("END_IF;")
                                else:
                                    # en is TRUE or empty -> unconditional execution
                                    self._add_line(f"{op['variable']} := {op['expression']};")
                            elif op_type == 'instruction_call':
                                en = op.get('en_expr')
                                if en == '???':
                                    # N2 Fix: Unresolved logic - skip operation with warning comment
                                    self._add_line(f"// WARNING: Unresolved enable logic - operation skipped")
                                    self._add_line(f"// TODO: Manually verify: {op['expression']}")
                                elif en and en != 'TRUE':
                                    self._add_line(f"IF {en} THEN")
                                    self._indent()
                                    self._add_line(f"{op['expression']};")
                                    self._dedent()
                                    self._add_line("END_IF;")
                                else:
                                    # en is TRUE or empty -> unconditional execution
                                    self._add_line(f"{op['expression']};")
                            
                            # --- CONTROL FLOW ---
                            elif op_type == 'return':
                                en = op.get('condition')
                                if en == '???':
                                    # N2 Fix: Unresolved condition - skip with warning
                                    self._add_line(f"// WARNING: Unresolved return condition - operation skipped")
                                    self._add_line(f"// TODO: Manually verify RETURN condition")
                                elif en and en != 'TRUE':
                                    self._add_line(f"IF {en} THEN RETURN; END_IF;")
                                else:
                                    # en is TRUE or empty -> unconditional return
                                    self._add_line("RETURN;")

                            elif op_type == 'exit':
                                en = op.get('condition')
                                if en == '???':
                                    # N2 Fix: Unresolved condition - skip with warning
                                    self._add_line(f"// WARNING: Unresolved exit condition - operation skipped")
                                    self._add_line(f"// TODO: Manually verify EXIT condition")
                                elif en and en != 'TRUE':
                                    self._add_line(f"IF {en} THEN EXIT; END_IF;")
                                else:
                                    # en is TRUE or empty -> unconditional exit
                                    self._add_line("EXIT;")

                            elif op_type == 'continue':
                                en = op.get('condition')
                                if en == '???':
                                    # N2 Fix: Unresolved condition - skip with warning
                                    self._add_line(f"// WARNING: Unresolved continue condition - operation skipped")
                                    self._add_line(f"// TODO: Manually verify CONTINUE condition")
                                elif en and en != 'TRUE':
                                    self._add_line(f"IF {en} THEN CONTINUE; END_IF;")
                                else:
                                    # en is TRUE or empty -> unconditional continue
                                    self._add_line("CONTINUE;")

                            elif op_type == 'label_definition':
                                self._dedent() # Labels usually at root level or distinct indent
                                self._add_line(f"{op['label']}:") # Label syntax: "Name:"
                                self._indent()
                                # Add an empty statement or valid op? SCL allows empty after label?
                                # Usually "Label: ;" is safer
                                self._add_line(";") 

                            elif op_type == 'jump':
                                target = op['target']
                                cond = op['condition']
                                negated = op.get('negated', False)

                                if negated:
                                    # IF (NOT cond) OR cond=FALSE
                                    cond_expr = f"NOT ({cond})"
                                else:
                                    cond_expr = cond

                                if '???' in cond_expr:
                                    # N2 Fix: Unresolved condition - skip with warning
                                    self._add_line(f"// WARNING: Unresolved jump condition - operation skipped")
                                    self._add_line(f"// TODO: Manually verify GOTO {target}")
                                elif cond_expr == 'TRUE':
                                    self._add_line(f"GOTO {target};")
                                elif cond_expr != 'FALSE':
                                    self._add_line(f"IF {cond_expr} THEN")
                                    self._indent()
                                    self._add_line(f"GOTO {target};")
                                    self._dedent()
                                    self._add_line("END_IF;")
                                    
                            elif op_type == 'return':
                                cond = op['condition']
                                if cond == '???':
                                    # N2 Fix: Unresolved condition - skip with warning
                                    self._add_line(f"// WARNING: Unresolved return condition - operation skipped")
                                    self._add_line(f"// TODO: Manually verify RETURN condition")
                                elif cond == 'TRUE':
                                    self._add_line("RETURN;")
                                elif cond != 'FALSE':
                                    self._add_line(f"IF {cond} THEN")
                                    self._indent()
                                    self._add_line("RETURN;")
                                    self._dedent()
                                    self._add_line("END_IF;")

                    self._dedent()
                    self._add_line('END_REGION')
                    self._add_line('')
            elif fb_calls_legacy:
                # Backward compatibility / Fallback
                self._add_line("REGION Logic")
                self._indent()
                self._add_comment(f"FB calls extracted from {prog_lang} logic")
                self._add_line("")
                for fb_call in fb_calls_legacy:
                    self._generate_single_fb_call(fb_call)
                self._dedent()
                self._add_line("END_REGION")
            
            # Fallback to generic placeholders if NO logic found anywhere
            elif not networks and not fb_calls_legacy and block_type == 'FB' and 'Static' in interface:
                self._add_line("REGION Logic")
                self._indent()
                fb_instances = []
                for member in interface['Static']:
                    datatype = member.get('datatype', '')
                    # Check if it's likely an FB instance (not a basic type)
                    if datatype not in ['Bool', 'Byte', 'Word', 'DWord', 'LWord', 
                                       'SInt', 'Int', 'DInt', 'LInt', 'USInt', 'UInt', 'UDInt', 'ULInt',
                                       'Real', 'LReal', 'Time', 'LTime', 'String', 'WString', 'Char', 'WChar'] and not member.get('is_array'):
                        fb_instances.append(member)
                
                if fb_instances:
                    self._add_comment(f"TODO: Configure and call FB instances (converted from {prog_lang})")
                    self._add_line("")
                    for fb_inst in fb_instances:
                        name = fb_inst.get('name')
                        datatype = fb_inst.get('datatype')
                        self._add_line(f'#{name}(')
                        self._indent()
                        # Add parameter placeholders
                        self._add_comment(f"Input parameters for {datatype}")
                        self._add_line("// param1 := value1,")
                        self._add_line("// param2 := value2,")
                        self._add_line("")
                        self._add_comment(f"Output parameters for {datatype}")
                        self._add_line("// output1 => variable1,")
                        self._add_line("// output2 => variable2")
                        self._dedent()
                        self._add_line(');')
                        self._add_line("")
                else:
                    self._add_comment(f"TODO: Convert {prog_lang} logic to SCL")
                self._dedent()
                self._add_line("END_REGION")

            elif not networks and not fb_calls_legacy:
                self._add_line("REGION Logic")
                self._indent()
                self._add_comment(f"TODO: Convert {prog_lang} logic to SCL")
                self._add_comment("Original logic is in graphical format")
                self._dedent()
                self._add_line("END_REGION")
            self._dedent()
        else:
            self._indent()
            self._add_comment("Block logic")
            self._dedent()
        
        # Empty line before END
        self._add_line("")
        
        # Close block
        if block_type == 'FB':
            self._add_line("END_FUNCTION_BLOCK")
        else:
            self._add_line("END_FUNCTION")
        
        self._add_line("")
    
    def _generate_single_fb_call(self, fb_call: Dict[str, Any]):
        """Generate SCL code for a single FB call"""
        instance = fb_call.get('instance')
        fb_type = fb_call.get('fb_type', 'Unknown')
        inputs = fb_call.get('inputs', {})
        outputs = fb_call.get('outputs', {})
        
        # Use quoted names for FB instances in SCL
        # In SCL, both FB instances and FC calls use quoted names: "InstanceName"()
        call_name = f'"{instance}"' if instance else f'"{fb_type}"'
        self._add_line(f'{call_name}(')
        self._indent()
        
        # Combine inputs and outputs
        all_params = []
        
        # Add input parameters (use :=)
        for param_name, value in inputs.items():
            all_params.append((param_name, value, ':='))
        
        # Add output parameters (use =>), but only if assigned
        for param_name, value in outputs.items():
            all_params.append((param_name, value, '=>'))
        
        # Generate parameter list
        for i, (param_name, value, operator) in enumerate(all_params):
            # Add comma except for last parameter
            comma = ',' if i < len(all_params) - 1 else ''
            self._add_line(f'{param_name} {operator} {value}{comma}')
        
        self._dedent()
        self._add_line(');')
        self._add_line("")

    def _generate_attributes(self):
        """Generate block attributes"""
        attributes = []
        
        # Optimized access
        config_optimized = config.get('optimize_access', True)
        
        # If 'memory_layout' is present, use it. 
        memory_layout = self.data.get('memory_layout')
        
        if memory_layout:
             if memory_layout == 'Optimized':
                 attributes.append("S7_Optimized_Access := 'TRUE'")
             elif memory_layout == 'Standard':
                 attributes.append("S7_Optimized_Access := 'FALSE'")
        elif config_optimized:
             attributes.append("S7_Optimized_Access := 'TRUE'")

        # Author
        if 'author' in self.data:
            attributes.append(f"Author : '{self.data['author']}'")

        # Family
        if 'family' in self.data:
            attributes.append(f"Family : '{self.data['family']}'")
        
        if attributes:
            self._add_line("{ " + "; ".join(attributes) + " }")
    
    def _generate_version(self):
        """Generate version declaration"""
        version = self.data.get('version', '0.1')
        self._add_line(f"VERSION : {version}")

    def get_file_extension(self) -> str:
        """Get the correct file extension for FB/FC files"""
        return ".scl"
