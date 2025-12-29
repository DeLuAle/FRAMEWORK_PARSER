"""
Expression Tree Builder - Converte espressioni LAD complesse in SCL corretto
Integra la logica del Fix per il bug di RestLimitSwitch in ValveMachine_FB
"""

from typing import Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# STRUTTURE DATI PER EXPRESSION TREE
# ============================================================================

class ExprType(Enum):
    """Tipi di nodi in un albero di espressioni LAD"""
    ACCESS = "access"          # Variabile/costante
    CONTACT = "contact"        # Contatto LAD
    AND = "and"                # Operazione AND
    OR = "or"                  # Operazione OR
    NOT = "not"                # Operazione NOT
    COMPARISON = "comparison"  # Comparazione (<=, >=, =, etc.)


@dataclass
class LadExpression:
    """Rappresenta un nodo in un albero di espressioni LAD"""
    expr_type: ExprType
    access_uid: Optional[str] = None              # Per ACCESS/CONTACT
    operand: Optional['LadExpression'] = None     # Per NOT
    operands: List['LadExpression'] = field(default_factory=list)  # Per AND/OR
    operator: Optional[str] = None                # Per COMPARISON: '<=', '>=', etc.
    left: Optional['LadExpression'] = None        # Per COMPARISON
    right: Optional['LadExpression'] = None       # Per COMPARISON
    negated: bool = False                         # Per CONTACT negato
    part_uid: Optional[str] = None                # Per debugging


@dataclass
class LadAccess:
    """Rappresenta una variabile o costante in LAD"""
    uid: str
    symbol: str
    scope: str


# ============================================================================
# EXPRESSION TREE BUILDER
# ============================================================================

def find_wire_source(target_uid: str, target_pin: str, wires: List) -> Optional[str]:
    """
    Trova il UID sorgente che si collega a target_uid:target_pin

    Args:
        target_uid: UID del part di destinazione
        target_pin: Nome del pin (es. 'in', 'in1', 'out')
        wires: Lista di wire connections

    Returns:
        source UID oppure None
    """
    for wire in wires:
        target_found = False
        source_uid = None

        for uid, pin, tag in wire.get('connections', []):
            # Cercare target
            if uid == target_uid and pin == target_pin and tag == 'NameCon':
                target_found = True
            # Cercare sorgente (Access o Part output)
            elif tag == 'IdentCon':  # Access connection
                source_uid = uid
            elif tag == 'NameCon' and pin in ['out', 'out1', 'out2']:  # Part output
                source_uid = uid

        if target_found and source_uid:
            return source_uid

    return None


def build_expression_tree(part_uid: str, wires: List, parts: Dict,
                         accesses: Dict[str, LadAccess],
                         visited: Optional[Set[str]] = None) -> Optional[LadExpression]:
    """
    Costruisce ricorsivamente un albero di espressioni dal grafo LAD

    Args:
        part_uid: UID del Part di partenza
        wires: Lista di tutti i wire
        parts: Dict di tutti i Part
        accesses: Dict di tutti gli Access
        visited: Set di UID già visitati (prevenzione cicli)

    Returns:
        LadExpression tree o None se non costruibile
    """
    if visited is None:
        visited = set()

    # Prevenzione cicli
    if part_uid in visited:
        return None
    visited.add(part_uid)

    # Caso 1: UID è un Access (foglia)
    if part_uid in accesses:
        return LadExpression(ExprType.ACCESS, access_uid=part_uid)

    # Caso 2: UID è un Part (nodo interno)
    if part_uid not in parts:
        return None

    part = parts[part_uid]
    part_type = part.get('type', '')  # Tipo del part (O, And, Contact, Le, ecc.)

    # OR block
    if part_type == 'O':
        cardinality = part.get('cardinality', 2)
        operands = []
        for i in range(1, cardinality + 1):
            pin_name = f"in{i}" if i > 1 else "in"
            source_uid = find_wire_source(part_uid, pin_name, wires)
            if source_uid:
                child_expr = build_expression_tree(source_uid, wires, parts, accesses, visited.copy())
                if child_expr:
                    operands.append(child_expr)

        return LadExpression(ExprType.OR, operands=operands, part_uid=part_uid) if operands else None

    # AND block (bitwise)
    elif part_type == 'And':
        in1_uid = find_wire_source(part_uid, 'in1', wires)
        in2_uid = find_wire_source(part_uid, 'in2', wires)

        left = build_expression_tree(in1_uid, wires, parts, accesses, visited.copy()) if in1_uid else None
        right = build_expression_tree(in2_uid, wires, parts, accesses, visited.copy()) if in2_uid else None

        if left and right:
            return LadExpression(ExprType.AND, operands=[left, right], part_uid=part_uid)

    # Contact (genera AND implicito se collegato in serie)
    elif part_type in ['Contact', 'PContact', 'NContact']:
        operand_uid = find_wire_source(part_uid, 'operand', wires)
        if operand_uid and operand_uid in accesses:
            is_negated = part.get('negated', False)
            return LadExpression(
                ExprType.CONTACT,
                access_uid=operand_uid,
                negated=is_negated,
                part_uid=part_uid
            )

    # Comparisons
    elif part_type in ['Le', 'Ge', 'Eq', 'Ne', 'Lt', 'Gt']:
        operator_map = {'Le': '<=', 'Ge': '>=', 'Eq': '=', 'Ne': '<>', 'Lt': '<', 'Gt': '>'}
        operator = operator_map[part_type]

        in1_uid = find_wire_source(part_uid, 'in1', wires)
        in2_uid = find_wire_source(part_uid, 'in2', wires)

        left = build_expression_tree(in1_uid, wires, parts, accesses, visited.copy()) if in1_uid else None
        right = build_expression_tree(in2_uid, wires, parts, accesses, visited.copy()) if in2_uid else None

        if left and right:
            comp_expr = LadExpression(
                ExprType.COMPARISON,
                operator=operator,
                left=left,
                right=right,
                part_uid=part_uid
            )

            # Controlla se ha precondizione
            pre_uid = find_wire_source(part_uid, 'pre', wires)
            if pre_uid:
                pre_expr = build_expression_tree(pre_uid, wires, parts, accesses, visited.copy())
                if pre_expr:
                    return LadExpression(ExprType.AND, operands=[pre_expr, comp_expr])

            return comp_expr

    # NOT
    elif part_type == 'Not':
        in_uid = find_wire_source(part_uid, 'in', wires)
        if in_uid:
            operand = build_expression_tree(in_uid, wires, parts, accesses, visited.copy())
            if operand:
                return LadExpression(ExprType.NOT, operand=operand, part_uid=part_uid)

    return None


# ============================================================================
# EXPRESSION TO SCL CONVERTER
# ============================================================================

def expression_to_scl(expr: LadExpression, accesses: Dict[str, LadAccess],
                     parent_precedence: int = 0) -> str:
    """
    Converte un albero di espressioni LAD in SCL con parentesi minimali

    Livelli di precedenza (alta → bassa):
    0 = OR (più bassa)
    1 = AND
    2 = NOT
    3 = COMPARISON
    4 = ACCESS, CONTACT (più alta)

    Args:
        expr: Albero di espressione LAD
        accesses: Mappa di variabili disponibili
        parent_precedence: Precedenza dell'operatore genitore

    Returns:
        Stringa SCL rappresentante l'espressione
    """
    if expr is None:
        return "UNKNOWN"

    if expr.expr_type == ExprType.ACCESS:
        # Foglia: ritorna il simbolo della variabile/costante
        if expr.access_uid in accesses:
            return accesses[expr.access_uid].symbol
        else:
            return f"UNKNOWN_{expr.access_uid}"

    elif expr.expr_type == ExprType.CONTACT:
        # Contatto: ritorna variabile (con NOT se negato)
        if expr.access_uid in accesses:
            var = accesses[expr.access_uid].symbol
            return f"NOT {var}" if expr.negated else var
        else:
            return "UNKNOWN"

    elif expr.expr_type == ExprType.NOT:
        # NOT: operatore unario
        precedence = 2
        operand_str = expression_to_scl(expr.operand, accesses, precedence)
        result = f"NOT {operand_str}"
        return f"({result})" if parent_precedence > precedence else result

    elif expr.expr_type == ExprType.COMPARISON:
        # Comparazione: operatore binario
        precedence = 3
        left_str = expression_to_scl(expr.left, accesses, precedence)
        right_str = expression_to_scl(expr.right, accesses, precedence)
        return f"({left_str} {expr.operator} {right_str})"

    elif expr.expr_type == ExprType.AND:
        # AND: operatore n-ario
        precedence = 1
        if not expr.operands:
            return "TRUE"
        if len(expr.operands) == 1:
            return expression_to_scl(expr.operands[0], accesses, parent_precedence)

        operand_strs = [expression_to_scl(op, accesses, precedence) for op in expr.operands]
        result = " AND ".join(operand_strs)
        return f"({result})" if len(operand_strs) > 1 or parent_precedence > precedence else result

    elif expr.expr_type == ExprType.OR:
        # OR: operatore n-ario
        precedence = 0
        if not expr.operands:
            return "FALSE"
        if len(expr.operands) == 1:
            return expression_to_scl(expr.operands[0], accesses, parent_precedence)

        operand_strs = [expression_to_scl(op, accesses, precedence) for op in expr.operands]
        result = " OR ".join(operand_strs)
        return f"({result})" if parent_precedence > precedence else result

    else:
        return f"/* UNSUPPORTED_EXPR_TYPE: {expr.expr_type} */"
