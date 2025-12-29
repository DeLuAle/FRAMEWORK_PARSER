"""
LAD/FBD logic parser - extracts FB calls and parameter connections from FlgNet
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

try:
    from expression_builder import (
        LadExpression, LadAccess, ExprType,
        build_expression_tree, expression_to_scl
    )
    # DISABLED: expression_builder needs debugging - revert to base LAD parser
    EXPRESSION_BUILDER_AVAILABLE = False
except ImportError:
    EXPRESSION_BUILDER_AVAILABLE = False

logger = logging.getLogger(__name__)


class LADLogicParser:
    """Parser for LAD/FBD logic in FlgNet format"""
    
    def __init__(self, compile_unit: ET.Element):
        """
        Initialize LAD parser.
        
        Args:
            compile_unit: CompileUnit XML element containing NetworkSource/FlgNet
        """
        self.compile_unit = compile_unit
        self.parts = {}  # UId -> part data
        self.wires = []  # List of wire connections
        # Map (dest_uid, dest_pin) -> source_info
        # source_info: {'type': 'Powerrail'|'IdentCon'|'NameCon', 'uid': ..., 'pin': ...}
        self.connections = {} 
        
    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse FlgNet and extract FB calls with parameters.
        
        Returns:
            List of FB call dictionaries
        """
        # Try to find NetworkSource with FlgNet
        network_source = self.compile_unit.find('.//NetworkSource')
        
        if network_source is None:
            logger.debug("NetworkSource not found")
            return []
        
        # FlgNet should be child of NetworkSource
        flgnet = None
        for child in network_source:
            tag_name = child.tag.split('}')[-1]  # Remove namespace
            if 'FlgNet' in tag_name:
                flgnet = child
                break
        
        if flgnet is None:
            logger.debug("FlgNet not found in NetworkSource")
            return []
        
        # Parse Parts (variables, constants, FB instances)
        self._parse_parts(flgnet)
        
        # Parse Wires (connections)
        self._parse_wires(flgnet)
        
        # Extract FB calls
        fb_calls = self._extract_fb_calls()
        
        return fb_calls
    
    def _parse_parts(self, flgnet: ET.Element):
        """Parse Parts section to build UId lookup"""
        parts_elem = None
        for child in flgnet:
            if 'Parts' in child.tag:
                parts_elem = child
                break
        
        if parts_elem is None:
            return
        
        for child in parts_elem:
            uid = child.get('UId')
            if not uid:
                continue
            
            part_data = {'type': child.tag.split('}')[-1]}  # Remove namespace
            
            if part_data['type'] == 'Access':
                # Variable or constant access
                scope = child.get('Scope')
                part_data['scope'] = scope
                
                # Get symbol/constant name
                symbol = None
                constant = None
                for elem in child:
                    if 'Symbol' in elem.tag:
                        symbol = elem
                    elif 'Constant' in elem.tag:
                        constant = elem
                
                if symbol is not None:
                    name_parts = []
                    last_was_component = False

                    for elem in symbol:
                        if 'Component' in elem.tag:
                            if last_was_component:
                                name_parts.append('.')
                            name_parts.append(elem.get('Name'))
                            last_was_component = True

                            # Check for nested array index in Component
                            # Structure: <Component Name="Rest_Ls"><Access><Constant>1</Constant></Access></Component>
                            for sub_elem in elem:
                                if 'Access' in sub_elem.tag:
                                    # Found array index
                                    for const_elem in sub_elem:
                                        if 'Constant' in const_elem.tag:
                                            for const_val in const_elem:
                                                if 'ConstantValue' in const_val.tag:
                                                    idx = const_val.text
                                                    if idx:
                                                        name_parts.append(f'[{idx}]')

                        elif 'Token' in elem.tag:
                            text = elem.get('Text')
                            if text:
                                # Token can be array index [n], comparison operator, etc
                                name_parts.append(text)
                                # Tokens like [1] don't reset the component flag
                                if not text.startswith('['):
                                    last_was_component = False

                    if name_parts:
                        part_data['name'] = ''.join(name_parts)
                
                if constant is not None:
                    const_name = constant.get('Name')
                    if const_name:
                        part_data['name'] = f'#{const_name}'
                    else:
                        const_type = None
                        const_value = None
                        for elem in constant:
                            if 'ConstantType' in elem.tag:
                                const_type = elem.text
                            elif 'ConstantValue' in elem.tag:
                                const_value = elem.text
                        if const_value is not None:
                            part_data['name'] = const_value
            
            elif part_data['type'] == 'Part':
                # Generic Part (FB call, Contact, Coil, etc.)
                part_data['part_type'] = child.get('Name')  # Contact, O, TON, etc.
                part_data['version'] = child.get('Version')
                
                # Check for Negated operand
                for elem in child:
                    if 'Negated' in elem.tag and elem.get('Name') == 'operand':
                        part_data['negated'] = True
                
                # Check for Instance (FB call)
                instance = None
                for elem in child:
                    if 'Instance' in elem.tag:
                        instance = elem
                        break
                
                if instance is not None:
                    components = []
                    for comp in instance:
                        if 'Component' in comp.tag:
                            components.append(comp.get('Name'))
                    if components:
                        part_data['instance_name'] = '.'.join(components)
                
                # Extract TemplateValue for Convert specific types
                template_values = {}
                for elem in child:
                    if 'TemplateValue' in elem.tag:
                        name = elem.get('Name')
                        val = elem.text
                        if name and val:
                            template_values[name] = val
                
                if template_values:
                    part_data['template_values'] = template_values
            
            elif part_data['type'] == 'Call':
                # Call element (e.g. for some FBs)
                # Structure: <Call UId="25"><CallInfo Name="DelayOnOff_R" BlockType="FB"><Instance ...>
                call_info = None
                for elem in child:
                    if 'CallInfo' in elem.tag:
                        call_info = elem
                        break
                
                if call_info is not None:
                    part_data['part_type'] = call_info.get('Name')
                    part_data['type'] = 'Part' # Treat as Part for compatibility with _extract_fb_calls
                    
                    # Extract instance from CallInfo
                    instance = None
                    for elem in call_info:
                        if 'Instance' in elem.tag:
                            instance = elem
                            break
                            
                    if instance is not None:
                        components = []
                        for comp in instance:
                            if 'Component' in comp.tag:
                                components.append(comp.get('Name'))
                        if components:
                            part_data['instance_name'] = '.'.join(components)
                    
                    # Store block name even if no instance (for FCs)
                    part_data['block_name'] = call_info.get('Name')
                            
            self.parts[uid] = part_data

    def _parse_wires(self, flgnet: ET.Element):
        """Parse Wires section to build connections"""
        wires_elem = None
        for child in flgnet:
            if 'Wires' in child.tag:
                wires_elem = child
                break
        
        if wires_elem is None:
            return
        
        for wire in wires_elem:
            if 'Wire' not in wire.tag:
                continue
            
            # Wire has source and destination
            # We map DESTINATION -> SOURCE for backtracking
            
            children = list(wire)
            if len(children) >= 2:
                # Source is usually the first element in Logic, 
                # but connections are Source -> Dest.
                # In Wire XML:
                # <Powerrail />
                # <NameCon UId="..." Name="in" />
                # This means Powerrail CONNECTS TO NameCon.
                
                # IMPORTANT: Wire elements can have MULTIPLE connections in a chain?
                # No, usually Source -> Dest.
                # But sometimes: <IdentCon ...> <NameCon ...>
                # Let's assume Child[0] -> Child[1].
                
                source = children[0]
                source_tag = source.tag.split('}')[-1]
                source_uid = source.get('UId')
                source_name = source.get('Name')
                
                # Iterate over all destinations (all children after the first one)
                for dest in children[1:]:
                    dest_tag = dest.tag.split('}')[-1]
                    dest_uid = dest.get('UId')
                    dest_name = dest.get('Name')
                    
                    if dest_uid:
                        key = (dest_uid, dest_name) if dest_name else (dest_uid, None)
                        
                        self.connections[key] = {
                            'type': source_tag,
                            'uid': source_uid,
                            'name': source_name
                        }
                        
                        # Store for debugging and original logic compatibility
                        self.wires.append({
                            'source_type': source_tag,
                            'source_uid': source_uid,
                            'source_name': source_name,
                            'dest_type': dest_tag,
                            'dest_uid': dest_uid,
                            'dest_name': dest_name
                        })

                # If there are more than 2 elements, it might be a chain? 
                # Usually Wire has exactly 2 points.
                # Exception: one output drives multiple inputs? 
                # In that case, there would be multiple wires or multiple dests?
                # The XML usually has separate Wire blocks for separate connections.
                # Example:
                # <Wire UId="46">
                #   <NameCon UId="33" Name="out" />
                #   <NameCon UId="34" Name="in" />
                #   <NameCon UId="35" Name="in" />
                # </Wire>
                # Oh, wait! Look at search result Step 50, Wire UId 46:
                # Source: UId 33 out. Dests: UId 34 in AND UId 35 in.
                # So a Wire can have multiple targets! source is [0], dests are [1:]
                
                if len(children) > 2:
                    source = children[0]
                    source_tag = source.tag.split('}')[-1]
                    source_uid = source.get('UId')
                    source_name = source.get('Name')
                    
                    for dest in children[1:]:
                        dest_tag = dest.tag.split('}')[-1]
                        dest_uid = dest.get('UId')
                        dest_name = dest.get('Name')
                        
                        if dest_uid:
                            key = (dest_uid, dest_name) if dest_name else (dest_uid, None)
                            
                            self.connections[key] = {
                                'type': source_tag,
                                'uid': source_uid,
                                'name': source_name
                            }

    def _extract_fb_calls(self) -> List[Dict[str, Any]]:
        """Extract FB calls with parameter connections"""
        fb_calls = []
        
        # Find all block calls (Parts or Call elements)
        for uid, part in self.parts.items():
            # A call is anything with an instance_name OR a block_name from a Call element
            if part.get('type') == 'Part' and (part.get('instance_name') or part.get('block_name')):
                fb_call = {
                    'instance': part.get('instance_name'),
                    'fb_type': part.get('part_type') or part.get('block_name'),
                    'version': part.get('version'),
                    'inputs': {},
                    'outputs': {},
                    'inouts': {}
                }
                
                logger.debug(f"Processing block call '{fb_call['fb_type']}' with UID {uid}")
                
                # For input parameters, we need to find what connects TO them.
                # In LAD, FB inputs are pins on the Part.
                # We need to iterate through POTENTIAL inputs.
                # Since we don't know the FB definition, we rely on Wires connecting to this UID.
                
                # Check all connections that target this UID
                for (dest_uid, dest_pin), source_info in self.connections.items():
                    if dest_uid == uid:
                        # This wire connects TO the FB
                        param_name = dest_pin
                        
                        logger.debug(f"  Input pin: {param_name}")
                        
                        # Resolve the value
                        value = self._resolve_input_connection(source_info)
                        logger.debug(f"    Resolved to: {value}")

                        # Include any non-??? value (even falsy ones like 0, FALSE, empty string)
                        if value and value != '???':
                            fb_call['inputs'][param_name] = value

                # Handle Outputs
                # Output pins connect FROM the FB to something else.
                # We need to find wires where SOURCE is this FB.
                # This is harder with `self.connections` (dest->source).
                # But we have `self.wires` or can iterate connections reverse.
                # Wait, standard output parameters in SCL are `fb.Output := Var`.
                # In LAD, if FB.Out -> Var, then Var is assigned FB.Out.
                # So we want to find Vars connected to FB Outputs.
                
                # Iterate all connections, find if source is this FB
                for (dest_uid, dest_pin), source_info in self.connections.items():
                    if source_info['uid'] == uid:
                        # This wire comes FROM the FB
                        param_name = source_info.get('name')

                        # Skip if output pin name is None (shouldn't normally happen)
                        if not param_name:
                            logger.debug(f"    Skipping FB output with no pin name")
                            continue

                        logger.debug(f"  Output pin: {param_name}")

                        # Destination is dest_uid/dest_pin
                        # We want to know what Variable is connected there.
                        # dest_uid should be an Access (variable).
                        # If dest is another Part logic, it's not a direct assignment output.
                        # But in SCL, output parameters map to variables.

                        dest_part = self.parts.get(dest_uid)
                        if dest_part and dest_part.get('type') == 'Access':
                            var_name = dest_part.get('name', '???')
                            logger.debug(f"    Resolved to variable: {var_name}")
                            fb_call['outputs'][param_name] = var_name
                        elif dest_part:
                            # Connected to logic?
                            logger.debug(f"    Output {param_name} connected to part type {dest_part.get('type')}")
                        
                fb_calls.append(fb_call)

        return fb_calls

    def _try_build_expression_tree(self, start_uid: str) -> Optional[str]:
        """
        Try to build expression tree for complex logic using expression_builder.
        Returns SCL expression string if successful, None otherwise.
        """
        if not EXPRESSION_BUILDER_AVAILABLE:
            return None

        try:
            # Convert parts to expression_builder format
            converted_parts = {}
            for uid, part_info in self.parts.items():
                if part_info.get('type') == 'Access':
                    # Accesses are handled separately
                    continue
                converted_parts[uid] = {
                    'type': part_info.get('part_type', ''),
                    'negated': part_info.get('negated', False),
                    'cardinality': part_info.get('cardinality', 2)
                }

            # Convert accesses to expression_builder format
            converted_accesses = {}
            for uid, part_info in self.parts.items():
                if part_info.get('type') == 'Access':
                    converted_accesses[uid] = LadAccess(
                        uid=uid,
                        symbol=part_info.get('name', f'VAR_{uid}'),
                        scope=part_info.get('scope', '')
                    )

            # Convert wires to expression_builder format
            converted_wires = []
            for (dest_uid, dest_pin), source_info in self.connections.items():
                wire_conn = {
                    'connections': []
                }

                # Add source
                if source_info.get('type') == 'Powerrail':
                    wire_conn['connections'].append((None, None, 'Powerrail'))
                elif source_info.get('uid'):
                    wire_conn['connections'].append((
                        source_info['uid'],
                        source_info.get('name'),
                        source_info['type']
                    ))

                # Add destination
                wire_conn['connections'].append((dest_uid, dest_pin, 'NameCon'))
                converted_wires.append(wire_conn)

            # Build expression tree
            expr_tree = build_expression_tree(
                start_uid,
                converted_wires,
                converted_parts,
                converted_accesses
            )

            if expr_tree:
                # Convert to SCL
                result = expression_to_scl(expr_tree, converted_accesses)
                logger.debug(f"Expression tree built for {start_uid}: {result}")
                return result

        except Exception as e:
            logger.debug(f"Failed to build expression tree for {start_uid}: {e}")

        return None

    def _resolve_input_connection(self, source_info: Optional[Dict[str, Any]]) -> str:
        """Resolve a connection source to an SCL expression"""
        if not source_info:
            return '???'

        src_type = source_info.get('type')
        src_uid = source_info.get('uid')
        src_pin = source_info.get('name')

        # Powerrail has no UID but should return TRUE
        if src_type == 'Powerrail':
            return 'TRUE'

        # If no UID but 'val' exists (e.g. constant or test mock)
        if not src_uid and 'val' in source_info:
            return source_info['val']

        if not src_uid:
             return '???'
        
        if src_type == 'IdentCon':
            # Direct variable connection
            if src_uid in self.parts:
                return self.parts[src_uid].get('name', '???')
            return '???'
            
        if src_type == 'NameCon':
            # Connection from another Part (logic or FB)
            # Try expression builder first for complex expressions
            if EXPRESSION_BUILDER_AVAILABLE:
                expr_result = self._try_build_expression_tree(src_uid)
                if expr_result and expr_result != '???':
                    logger.debug(f"Using expression tree result for {src_uid}: {expr_result}")
                    return expr_result

            # Fallback to original recursive logic
            return self._resolve_logic_part(src_uid, src_pin)

        return '???'

    def _resolve_logic_part(self, uid: str, pin: str = None) -> str:
        """
        Recursively resolve logic part output.

        When pin is None or 'out', resolve the part's output completely.
        For Contact/OR/And/etc, this means evaluating the entire logic.
        """
        if uid not in self.parts:
            return '???'

        # --- Handle ENO pin requests ---
        if pin and pin.lower() == 'eno':
            return 'TRUE'

        part = self.parts[uid]
        part_type = part.get('part_type')

        # Avoid infinite recursion (simple check) - could pass specialized set of visited nodes

        # When pin is 'out' or None, resolve the complete output logic
        if pin in [None, 'out']:
            pin = None

        if part_type == 'Contact':
            # Standard Contact (-| |-) or Negated (-|/|-)
            # Output = (Input AND Operand)

            # 1. Resolve 'in' (Input flow)
            in_conn = self.connections.get((uid, 'in'))
            in_expr = self._resolve_input_connection(in_conn) if in_conn else 'TRUE'  # Default to TRUE at rung start

            # 2. Resolve 'operand' (Variable)
            op_conn = self.connections.get((uid, 'operand'))
            op_expr = self._resolve_input_connection(op_conn) if op_conn else '???'

            if part.get('negated'):
                op_expr = f"NOT ({op_expr})"

            if in_expr == 'TRUE':
                return op_expr
            elif in_expr == 'FALSE' or in_expr == '???':
                 return in_expr # Propagate fail/false
            else:
                return f"({in_expr} AND {op_expr})"
                
        elif part_type == 'O':
            # OR block parallel branch
            # Has multiple inputs: in1, in2...
            # We don't know how many in advance, but we can look in connections for (uid, 'inX')
            
            exprs = []
            
            # Check for in1, in2... up to reasonable number or scan connections
            # Scan connections is safer
            found_inputs = []
            for (curr_uid, curr_pin) in self.connections:
                if curr_uid == uid and curr_pin and curr_pin.startswith('in'):
                    found_inputs.append(curr_pin)
            
            for pin in sorted(found_inputs):
                conn = self.connections[(uid, pin)]
                val = self._resolve_input_connection(conn)
                exprs.append(val)
                
            if not exprs:
                return '???'
                
            if len(exprs) == 1:
                return exprs[0]
                
            return f"({' OR '.join(exprs)})"
            
        elif part_type in ['Coil', 'SCoil', 'RCoil']:
            # Coil output passes the input signal through
            in_conn = self.connections.get((uid, 'in'))
            return self._resolve_input_connection(in_conn) if in_conn else '???'

        elif part_type == 'Not':
            # Inverter
            in_conn = self.connections.get((uid, 'in'))
            val = self._resolve_input_connection(in_conn) if in_conn else '???'
            if val == '???': return '???'
            return f"NOT ({val})"

        elif part_type in ['Eq', 'Ne', 'Gt', 'Lt', 'Ge', 'Le']:
            # Comparators
            ops = {
                'Eq': '=', 'Ne': '<>', 
                'Gt': '>', 'Lt': '<', 
                'Ge': '>=', 'Le': '<='
            }
            operator = ops.get(part_type, '=')
            
            # Resolve inputs
            in1_conn = self.connections.get((uid, 'in1'))
            in2_conn = self.connections.get((uid, 'in2'))
            
            in1 = self._resolve_input_connection(in1_conn) if in1_conn else '???'
            in2 = self._resolve_input_connection(in2_conn) if in2_conn else '???'
            
            comp_expr = f"({in1} {operator} {in2})"
            
            # Handle 'pre' (Enable/Predecessor logic) if present
            # If 'pre' is missing/Powerrail, we just return comp_expr
            # If 'pre' exists, result is (pre AND comp_expr)
            pre_conn = self.connections.get((uid, 'pre'))
            pre_expr = self._resolve_input_connection(pre_conn) if pre_conn else 'TRUE' # Default to True if not wired? Or FALSE? 
            # In LAD XML, if 'pre' is not listed in wires, it might be implicit TRUE (start of rung)?
            # But usually it is wired to Powerrail.
            
            if pre_expr == 'TRUE':
                return comp_expr
            elif pre_expr == 'FALSE' or pre_expr == '???':
                return 'FALSE'
            else:
                return f"({pre_expr} AND {comp_expr})"
            
        elif part_type == 'Sr' or part_type == 'Rs':
            # SR / RS Flip-Flop
            # If used in logic flow (Q output), it represents the state of the Operand.
            op_var = self._resolve_operand(uid)
            if op_var:
                return op_var
            return f"UnknownLogic_{part_type}_{uid}"

        elif part_type == 'PContact':
            # Positive Edge Contact -|P|-
            # 1. If it has an instance (R_TRIG), use it.
            if part.get('instance_name'):
                return f'#{part["instance_name"]}.Q'
            
            # 2. If no instance, it's checking the edge of an operand bit.
            # SCL doesn't have a direct "Scan for P edge" expression without an instance or aux memory.
            # We return a specific marker that users can search/replace if needed, 
            # or best effort expression if possible.
            op_conn = self.connections.get((uid, 'operand'))
            op_expr = self._resolve_input_connection(op_conn) if op_conn else '???'
            return f"PosEdge({op_expr})" 

        elif part_type == 'NContact':
            # Negative Edge Contact -|N|-
            if part.get('instance_name'):
                return f'#{part["instance_name"]}.Q'
                
            op_conn = self.connections.get((uid, 'operand'))
            op_expr = self._resolve_input_connection(op_conn) if op_conn else '???'
            return f"NegEdge({op_expr})"

        elif part_type == 'PBox':
            # Positive Edge Box (P_TRIG)
            # Has 'in' and 'bit'
            in_conn = self.connections.get((uid, 'in'))
            in_expr = self._resolve_input_connection(in_conn) if in_conn else '???'
            
            bit_conn = self.connections.get((uid, 'bit'))
            bit_expr = self._resolve_input_connection(bit_conn) if bit_conn else '???'
            
            return f"PosEdge({in_expr}, {bit_expr})"

        elif part_type == 'NBox':
            # Negative Edge Box (N_TRIG)
            # Has 'in' and 'bit'
            in_conn = self.connections.get((uid, 'in'))
            in_expr = self._resolve_input_connection(in_conn) if in_conn else '???'
            
            bit_conn = self.connections.get((uid, 'bit'))
            bit_expr = self._resolve_input_connection(bit_conn) if bit_conn else '???'
            
            return f"NegEdge({in_expr}, {bit_expr})"

        # Mathematical and Standard Functions
        elif part_type in ['Mul', 'Add', 'Sub', 'Div', 'Mod', 'And', 'Or', 'Xor']:
            ops = {
                'Mul': ' * ', 'Add': ' + ', 'Sub': ' - ', 'Div': ' / ', 'Mod': ' MOD ',
                'And': ' AND ', 'Or': ' OR ', 'Xor': ' XOR '
            }
            op = ops.get(part_type)
            
            # Resolve inputs 'in1', 'in2'
            in1_conn = self.connections.get((uid, 'in1'))
            in2_conn = self.connections.get((uid, 'in2'))
            
            in1 = self._resolve_input_connection(in1_conn) if in1_conn else '???'
            in2 = self._resolve_input_connection(in2_conn) if in2_conn else '???'
            
            return f"({in1}{op}{in2})"
            
        elif part_type == 'Convert':
             # Handle implicit conversion e.g. Real_TO_Int derived from TemplateValue
             tpl = part.get('template_values', {})
             src_type = tpl.get('SrcType')
             dest_type = tpl.get('DestType')
             
             func_name = 'CONVERT'
             if src_type and dest_type:
                 func_name = f"{src_type}_TO_{dest_type}".upper()
             
             # Resolve input 'in'
             in_conn = self.connections.get((uid, 'in'))
             in_expr = self._resolve_input_connection(in_conn) if in_conn else '???'
             
             return f"{func_name}({in_expr})"

        elif part_type in ['Abs', 'LIMIT', 'Sqr', 'Sqrt', 'Round', 'Trunc', 'Ceil', 'Floor', 'Sin', 'Cos', 'Tan', 'Asin', 'Acos', 'Atan', 'Ln', 'Exp', 'Expt', 'Min', 'Max', 'Sel', 'Mux',
                           'Len', 'Concat', 'Left', 'Right', 'Mid', 'Find', 'Replace', 'Insert', 'Delete', 'String_to_Chars', 'Chars_to_String',
                           'Shl', 'Shr', 'Rol', 'Ror', 'Swap',
                           'Scale_X', 'Norm_X', 'Neg', 'Frac',
                           'InRange', 'OutRange', 'MoveBlk', 'FillBlk', 'UMoveBlk', 'UFillBlk',
                           'CountOfElements', 'IsArray',
                           'Peek', 'Poke', 'PeekBool', 'PokeBool', 'Peek_Bool', 'Poke_Bool',
                           'To_Int', 'To_DInt', 'To_Real', 'To_LReal', 'To_Bool', 'To_Byte', 'To_Word', 'To_DWord', 'To_Time', 'To_SInt', 'To_USInt', 'To_UInt', 'To_UDInt', 'To_String', 'To_WString',
                           'Bool_To_Int', 'Bool_To_DInt', 'Bool_To_Byte', 'Int_To_Bool', 'DInt_To_Bool',
                           # Advanced Types
                           'TypeOf', 'VariantGet', 'VariantPut', 'Ref',
                           'RD_SYS_T', 'T_DIFF', 'T_COMBINE', 'T_CONV', 'T_ADD', 'T_SUB',
                           'SET_CINT', 'QRY_CINT', 'CAN_CINT']:
             # Function Calls
             func_map = {
                'Abs': 'ABS', 'LIMIT': 'LIMIT', 'Sqr': 'SQR', 'Sqrt': 'SQRT',
                'Round': 'ROUND', 'Trunc': 'TRUNC', 'Ceil': 'CEIL', 'Floor': 'FLOOR',
                'Sin': 'SIN', 'Cos': 'COS', 'Tan': 'TAN', 'Asin': 'ASIN', 'Acos': 'ACOS', 'Atan': 'ATAN',
                'Ln': 'LN', 'Exp': 'EXP', 'Expt': 'EXPT',
                'Min': 'MIN', 'Max': 'MAX', 'Sel': 'SEL', 'Mux': 'MUX',
                'Len': 'LEN', 'Concat': 'CONCAT', 'Left': 'LEFT', 'Right': 'RIGHT',
                'Mid': 'MID', 'Find': 'FIND', 'Replace': 'REPLACE',
                'Insert': 'INSERT', 'Delete': 'DELETE', 'String_to_Chars': 'Strg_TO_Chars',
                'Chars_to_String': 'Chars_TO_Strg',
                'Shl': 'SHL', 'Shr': 'SHR', 'Rol': 'ROL', 'Ror': 'ROR', 'Swap': 'SWAP',
                'Scale_X': 'SCALE_X', 'Norm_X': 'NORM_X', 'Neg': 'NEG', 'Frac': 'FRAC',
                'InRange': 'IN_RANGE', 'OutRange': 'OUT_RANGE', 
                'MoveBlk': 'MOVE_BLK', 'FillBlk': 'FILL_BLK', 
                'UMoveBlk': 'UMOVE_BLK', 'UFillBlk': 'UFILL_BLK',
                'CountOfElements': 'CountOfElements', 'IsArray': 'IS_ARRAY',
                'Peek': 'PEEK', 'Poke': 'POKE', 'PeekBool': 'PEEK_BOOL', 'Peek_Bool': 'PEEK_BOOL', 'PokeBool': 'POKE_BOOL', 'Poke_Bool': 'POKE_BOOL',
                'To_Int': 'TO_INT', 'To_DInt': 'TO_DINT', 'To_Real': 'TO_REAL', 'To_LReal': 'TO_LREAL',
                'To_Bool': 'TO_BOOL', 'To_Byte': 'TO_BYTE', 'To_Word': 'TO_WORD', 'To_DWord': 'TO_DWORD',
                'To_Time': 'TO_TIME', 'To_SInt': 'TO_SINT', 'To_USInt': 'TO_USINT', 'To_UInt': 'TO_UINT', 'To_UDInt': 'TO_UDINT',
                'To_String': 'TO_STRING', 'To_WString': 'TO_WSTRING',
                'Bool_To_Int': 'BOOL_TO_INT', 'Bool_To_DInt': 'BOOL_TO_DInt', 'Bool_To_Byte': 'BOOL_TO_Byte',
                'Int_To_Bool': 'INT_TO_BOOL', 'DInt_To_Bool': 'DINT_TO_BOOL',
                'TypeOf': 'TypeOf', 'VariantGet': 'VariantGet', 'VariantPut': 'VariantPut', 'Ref': 'REF',
                # System Functions Cases
                'RD_SYS_T': 'RD_SYS_T', 'T_DIFF': 'T_DIFF', 'T_COMBINE': 'T_COMBINE', 
                'T_CONV': 'T_CONV', 'T_ADD': 'T_ADD', 'T_SUB': 'T_SUB',
                'SET_CINT': 'SET_CINT', 'QRY_CINT': 'QRY_CINT', 'CAN_CINT': 'CAN_CINT'
             }
             func_name = func_map.get(part_type, part_type.upper())
             
             # Resolve parameters based on standard naming (in, in1, in2, mn, mx, val, g, k)
             # We iterate connections to find relevant inputs
             params = []
             
             # Gather all input connections
             input_args = {}
             # Pin names to exclude from parameters list (as they are handled as EN/ENO or assignment result)
             exclude_pins = ['en', 'eno', 'out', 'out1', 'value', 'ret_val', 'retval']
             
             for (curr_uid, curr_pin) in self.connections:
                 if curr_uid == uid and curr_pin:
                     pin_lower = curr_pin.lower()
                     if pin_lower not in exclude_pins:
                         conn = self.connections[(uid, curr_pin)]
                         val = self._resolve_input_connection(conn)
                         input_args[curr_pin] = val
             
             # Format parameters
             if part_type == 'LIMIT':
                 # Order: MN, IN, MX
                 mn = input_args.get('mn', '0')
                 val = input_args.get('in', '0')
                 mx = input_args.get('mx', '0')
                 return f"LIMIT(MN:={mn}, IN:={val}, MX:={mx})"
                 
             # Generic
             for arg_name, arg_val in input_args.items():
                 params.append(f"{arg_name.upper()}:={arg_val}")
             
             if not params and 'in' in input_args: # Fallback
                  return f"{func_name}({input_args['in']})"
             elif not params:
                  # Maybe implicit 'in'?
                  conn = self.connections.get((uid, 'in'))
                  if conn:
                      val = self._resolve_input_connection(conn)
                      return f"{func_name}({val})"
             
             return f"{func_name}({', '.join(params)})"
        
        elif part_type == 'Move':
            # Move as an expression? Typically Move is an instruction.
            # But if used in a wire flow: In -> Move -> Out
            # It just passes value.
            return self._resolve_input_connection(self.connections.get((uid, 'in')))

        elif part.get('instance_name'):
             # FB/Timer/Counter instance logic usage (e.g. TON Q output)
             instance_name = part.get('instance_name')
             # Map pin name if necessary (usually Q, ET, etc match SCL)
             # If pin is None, likely default output (Q for timers?)
             if pin:
                 return f"#{instance_name}.{pin}"
             else:
                 return f"#{instance_name}.Q" # Best guess default

        elif part.get('type') == 'Call' or (part_type and part.get('blocktype') == 'FC') or part.get('block_name'):
            # FC/FB Call in LAD logic
            # part_type or block_name contains the FC/FB name
            call_name = part_type or part.get('block_name') or part.get('name', f'Call_{uid}')
            
            # Resolve parameters
            input_args = {}
            for (curr_uid, curr_pin), source_info in self.connections.items():
                if curr_uid == uid and curr_pin and curr_pin not in ['en', 'eno', 'Ret_Val']:
                    # Use the common resolver
                    val = self._resolve_input_connection(source_info)
                    input_args[curr_pin] = val
            
            # Formatting call: "FC_Name"(Param1 := Val1, ...)
            params = [f"{k} := {v}" for k, v in input_args.items() if v != '???']
            return f'"{call_name}"({", ".join(params)})'

        # For unknown or unsupported logic parts (e.g., FC call results in LAD)
        # Return placeholder instead of UnknownLogic to be more explicit that we don't support this
        logger.warning(f"Unsupported logic part type '{part_type}' (UID {uid}) - using placeholder")
        return f"???"

    def _extract_rung_expression(self, coil_uid: str) -> str:
        """
        Build boolean expression for a single rung by backtracing from Coil to Powerrail.

        A rung is: Powerrail -> Contact1 -> Contact2 -> ... -> Coil
        This method reconstructs the complete boolean expression.
        """
        # Backtrack from Coil's input to reconstruct the rung expression
        conn = self.connections.get((coil_uid, 'in'))
        if not conn:
            return '???'

        # Start backtracing from the coil input
        return self._resolve_input_connection(conn)

    def _extract_operations(self) -> List[Dict]:
        """Extract logical operations (Coils, Assignments, SR/RS, Moves, etc.)"""
        operations = []
        processed_parts = set()

        OP_TYPES = ['Mul', 'Add', 'Sub', 'Div', 'Mod', 'And', 'Or', 'Xor']
        FUNC_TYPES = ['Abs', 'LIMIT', 'Sqr', 'Sqrt', 'Round', 'Trunc', 'Ceil', 'Floor', 'Sin', 'Cos', 'Tan',
                      'Asin', 'Acos', 'Atan', 'Ln', 'Exp', 'Expt', 'Min', 'Max', 'Sel', 'Mux',
                      'Len', 'Concat', 'Left', 'Right', 'Mid', 'Find', 'Replace', 'Insert', 'Delete',
                      'String_to_Chars', 'Chars_to_String',
                      'Shl', 'Shr', 'Rol', 'Ror', 'Swap',
                      'Scale_X', 'Norm_X', 'Neg', 'Frac', 'Convert',
                      'InRange', 'OutRange', 'MoveBlk', 'FillBlk', 'UMoveBlk', 'UFillBlk',
                      'CountOfElements', 'IsArray',
                      # System Functions
                      'SET_CINT', 'QRY_CINT', 'CAN_CINT', 'DIS_CINT', 'EN_CINT',
                      'RD_SYS_T', 'T_DIFF', 'T_COMBINE', 'T_CONV', 'T_ADD', 'T_SUB']

        for uid, part in self.parts.items():
            name = part.get('part_type')
            if not name or uid in processed_parts:
                continue

            op_entry = None
            
            # --- COILS ---
            if name == 'Coil':
                negated = part.get('negated', False)
                conn = self.connections.get((uid, 'in'))
                expr = self._resolve_input_connection(conn) if conn else 'FALSE'
                target_var = self._resolve_operand(uid)
                if target_var:
                    op_entry = {
                        'type': 'assignment',
                        'variable': target_var,
                        'expression': f"NOT ({expr})" if negated else expr
                    }
            
            elif name in ['SCoil', 'RCoil']:
                conn = self.connections.get((uid, 'in'))
                expr = self._resolve_input_connection(conn) if conn else 'FALSE'
                target_var = self._resolve_operand(uid)
                if target_var:
                    op_entry = {
                        'type': 'set' if name == 'SCoil' else 'reset',
                        'variable': target_var,
                        'condition': expr
                    }

            # --- FLIP-FLOPS ---
            elif name in ['Sr', 'Rs']:
                # TIA Portal XML uses lowercase pin names for SR/RS (s, r1, s1, r)
                s_conn = self.connections.get((uid, 'S')) or self.connections.get((uid, 'S1')) or \
                         self.connections.get((uid, 's')) or self.connections.get((uid, 's1'))
                
                r_conn = self.connections.get((uid, 'R')) or self.connections.get((uid, 'R1')) or \
                         self.connections.get((uid, 'r')) or self.connections.get((uid, 'r1'))
                
                s_expr = self._resolve_input_connection(s_conn) if s_conn else 'FALSE'
                r_expr = self._resolve_input_connection(r_conn) if r_conn else 'FALSE'
                
                target_var = self._resolve_operand(uid)
                
                if target_var:
                    op_entry = {
                        'type': 'sr' if name == 'Sr' else 'rs',
                        'variable': target_var,
                        's_expr': s_expr,
                        'r_expr': r_expr
                    }

            # --- MOVE ---
            elif name == 'Move':
                en_conn = self.connections.get((uid, 'en'))
                en_expr = self._resolve_input_connection(en_conn) if en_conn else 'TRUE'
                
                in_conn = self.connections.get((uid, 'in'))
                src_expr = self._resolve_input_connection(in_conn) if in_conn else '???'
                
                dest_var = self._find_variable_connected_to_output(uid, 'out1')
                
                if dest_var:
                    op_entry = {
                        'type': 'move',
                        'source': src_expr,
                        'dest': dest_var,
                        'en_expr': en_expr
                    }

            # --- MATH / INSTRUCTIONS ---
            elif name in OP_TYPES or name in FUNC_TYPES:
                # Map name to SCL function name to check properties
                scl_name = name.upper()
                if name in ['InRange', 'OutRange']: scl_name = 'IN_RANGE' if name == 'InRange' else 'OUT_RANGE'
                if name == 'MoveBlk': scl_name = 'MOVE_BLK'
                if name == 'FillBlk': scl_name = 'FILL_BLK'
                if name == 'UMoveBlk': scl_name = 'UMOVE_BLK'
                if name == 'UFillBlk': scl_name = 'UFILL_BLK'

                # VOID functions do not return a value, so we generate a call directly
                VOID_FUNCS = ['MOVE_BLK', 'FILL_BLK', 'UMOVE_BLK', 'UFILL_BLK']
                
                if scl_name in VOID_FUNCS:
                    en_conn = self.connections.get((uid, 'en'))
                    en_expr = self._resolve_input_connection(en_conn) if en_conn else 'TRUE'
                    
                    # Resolve call string
                    call_expr = self._resolve_logic_part(uid, None)
                    
                    op_entry = {
                        'type': 'instruction_call',
                        'expression': call_expr,
                        'en_expr': en_expr
                    }
                else:
                    # Value-returning functions - find assignment target
                    dest_var = None
                    # Common output pins in TIA Portal LAD XML
                    output_pins = ['out', 'out1', 'value', 'shl', 'shr', 'rol', 'ror', 'ret_val', 'retval']
                    
                    for pin in output_pins:
                        # Try both the name as is and lowercase/uppercase variants if needed
                        # _find_variable_connected_to_output should ideally handle this
                        dest_var = self._find_variable_connected_to_output(uid, pin)
                        if dest_var: break
                    
                    if dest_var: 
                        en_conn = self.connections.get((uid, 'en'))
                        en_expr = self._resolve_input_connection(en_conn) if en_conn else 'TRUE'
                        
                        # Re-resolve the expression for THIS part
                        rhs_expr = self._resolve_logic_part(uid, None)
                        
                        op_entry = {
                            'type': 'instruction_assignment',
                            'variable': dest_var,
                            'expression': rhs_expr,
                            'en_expr': en_expr
                        }

            if op_entry:
                operations.append(op_entry)
                processed_parts.add(uid)
                
            # --- CONTROL FLOW ---
            elif name == 'Label':
                 # Determine Label Name
                 # Often in Attribute "Name" or as a child "AttributeList/Name"? 
                 # In LAD XML, Label usually has a 'Name' attribute or 'LabelName'
                 # Part for Label: <Part Name="Label" UId="21"> <AttributeList> <Attribute Name="Name" ...> </AttributeList>
                 # Or shorter: <Part Name="Label"> <TemplateValue Name="Name" Type="Type">LabelName</TemplateValue>
                 
                 label_name = part.get('name') # We might need to check if 'name' was extracted correctly in _parse_parts
                 
                 # Let's check _parse_parts logic for 'name'.
                 # Usually part_data['name'] is invalid for Label if it's not an Access.
                 # For Part elements, we might need to look for specific attributes.
                 if not label_name:
                     # Attempt to find "LabelName" in template values or attributes
                     tpl = part.get('template_values', {})
                     if 'Name' in tpl:
                         label_name = tpl['Name']
                     
                 # Fallback: check original element if needed (not accessible here easily without storing it)
                 # But _parse_parts extracts TemplateValues.
                 
                 if label_name:
                     op_entry = {
                         'type': 'label_definition',
                         'label': label_name
                     }
            
            elif name in ['Jump', 'Jmp']:
                 # Unconditional or conditional jump
                 # Check connection to 'en' or 'in'
                 en_conn = self.connections.get((uid, 'en'))
                 en_expr = self._resolve_input_connection(en_conn) if en_conn else 'TRUE'
                 
                 # Target label
                 # <TemplateValue Name="Target" Type="Type">LabelName</TemplateValue>
                 tpl = part.get('template_values', {})
                 target = tpl.get('Target')
                 
                 if target:
                     op_entry = {
                         'type': 'jump',
                         'target': target,
                         'condition': en_expr,
                         'negated': False
                     }

            elif name == 'JmpN':
                 # Conditional jump if RLO=0 (or N contact logic)
                 # Actually JmpN usually means "Jump if Not".
                 en_conn = self.connections.get((uid, 'en'))
                 en_expr = self._resolve_input_connection(en_conn) if en_conn else 'TRUE'
                 
                 tpl = part.get('template_values', {})
                 target = tpl.get('Target')
                 
                 if target:
                     op_entry = {
                         'type': 'jump',
                         'target': target,
                         'condition': en_expr,
                         'negated': True
                     }
            
            elif name == 'Return':
                 # Return instruction
                 en_conn = self.connections.get((uid, 'en'))
                 en_expr = self._resolve_input_connection(en_conn) if en_conn else 'TRUE'
                 
                 op_entry = {
                     'type': 'return',
                     'condition': en_expr
                 }

            elif name == 'Exit':
                 # Loop exit
                 en_conn = self.connections.get((uid, 'en'))
                 en_expr = self._resolve_input_connection(en_conn) if en_conn else 'TRUE'
                 op_entry = { 'type': 'exit', 'condition': en_expr }

            elif name == 'Continue':
                 # Loop continue
                 en_conn = self.connections.get((uid, 'en'))
                 en_expr = self._resolve_input_connection(en_conn) if en_conn else 'TRUE'
                 op_entry = { 'type': 'continue', 'condition': en_expr }

            # --- GENERIC CALLS (FC/FB) ---
            elif part.get('block_name') or part.get('instance_name'):
                 # This covers calls that weren't processed as specific operations above
                 en_conn = self.connections.get((uid, 'en'))
                 en_expr = self._resolve_input_connection(en_conn) if en_conn else 'TRUE'
                 
                 # Check if it has a return value (assignment)
                 dest_var = self._find_variable_connected_to_output(uid, 'Ret_Val') or \
                            self._find_variable_connected_to_output(uid, 'out')
                 
                 # Resolve call string
                 call_expr = self._resolve_logic_part(uid, None)
                 
                 if dest_var:
                      op_entry = {
                          'type': 'instruction_assignment',
                          'variable': dest_var,
                          'expression': call_expr,
                          'en_expr': en_expr
                      }
                 else:
                      op_entry = {
                          'type': 'instruction_call',
                          'expression': call_expr,
                          'en_expr': en_expr
                      }

            if op_entry:
                operations.append(op_entry)
                processed_parts.add(uid)

        # Deduplicate operations (same variable and expression)
        seen = {}
        deduped = []
        for op in operations:
            # Create a key for deduplication
            key = (op.get('type'), op.get('variable'), op.get('expression'), op.get('condition'))
            if key not in seen:
                seen[key] = True
                deduped.append(op)

        return deduped

    def _resolve_operand(self, part_uid):
        """Resolve the operand variable for a Coil or SR/RS"""
        info = self.connections.get((part_uid, 'operand'))
        if info and info['type'] == 'IdentCon': 
            return self._resolve_access_name(info['uid'])
        return None

    def _resolve_access_name(self, uid):
        """Reconstruct variable name from Access part"""
        part = self.parts.get(uid)
        if not part: return "???"
        if part.get('name'): return part.get('name')
        return "???"
    
    def _find_variable_connected_to_output(self, part_uid, pin_name):
        """Finds a variable connected to the output of a part"""
        for (dest_uid, dest_pin), source_info in self.connections.items():
            source_pin = source_info.get('name', '')
            if source_info['uid'] == part_uid and (source_pin.lower() == pin_name.lower()):
                dest_part = self.parts.get(dest_uid)
                if dest_part and dest_part.get('type') == 'Access':
                     return self._resolve_access_name(dest_uid)
        return None

