from itertools import chain
from lark import Visitor, Transformer, Lark, Token, Tree

from logic import *


with open('grammar.lark') as f:
    _grammar = f.read()


def parse(text):
    parser = Lark(_grammar, start='start', ambiguity='resolve', parser='earley')
    tree = parser.parse(text)
    decl = _DeclarationParser()
    decl.visit(tree)
    cp = _ConstraintParser(
        decl.boolean_variables,
        decl.enum_variables,
        decl.enum_values,
        decl.int_variables,
        decl.int_ranges,
    )
    cp.transform(tree)
    return {
        "boolean_variables": decl.boolean_variables,
        "enum_variables":    decl.enum_variables,
        "enum_values":       decl.enum_values,
        "int_variables":     decl.int_variables,
        "int_ranges":        decl.int_ranges,
        "invar":    cp.invar,
        "init":     cp.init,
        "trans":    cp.trans,
        "ltl":      cp.ltls,
        "fairness": cp.fairness,
    }


# ---------------------------------------------------------------------------
# Declaration pass (bottom-up Visitor — only reads tree structure)
# ---------------------------------------------------------------------------
class _DeclarationParser(Visitor):
    def __init__(self):
        self.boolean_variables = []
        self.enum_variables    = []
        self.enum_values       = []   # parallel list of value-lists
        self.int_variables     = []
        self.int_ranges        = {}   # name -> (lo, hi) | None

    def var_list(self, tree):
        name     = str(tree.children[0])
        typespec = tree.children[1]   # Tree(type_specifier, [...])
        ch       = typespec.children

        if isinstance(ch[0], Token):
            t = ch[0].type
            if t == 'BOOLEANTYPE':
                self.boolean_variables.append(name)
            elif t == 'INTTYPE':
                self.int_variables.append(name)
                self.int_ranges[name] = None
            elif t == 'INT_LITERAL':
                lo = int(ch[0])
                hi = int(ch[1])
                self.int_variables.append(name)
                self.int_ranges[name] = (lo, hi)
        else:
            # enum subtree: Tree(enum, [Token(IDENTIFIER,...), ...])
            enum_tree = ch[0]
            self.enum_variables.append(name)
            self.enum_values.append([str(t) for t in enum_tree.children])


# ---------------------------------------------------------------------------
# Transformation pass — builds logic objects from the parse tree
# ---------------------------------------------------------------------------
class _ConstraintParser(Transformer):
    def __init__(self, bool_vars, enum_vars, enum_vals, int_vars, int_ranges):
        self.boolean_variables = bool_vars
        self.enum_variables    = enum_vars
        self.enum_values       = list(chain(*enum_vals))
        self.int_variables     = int_vars
        self.int_ranges        = int_ranges
        self.invar   = []
        self.init    = []
        self.trans   = []
        self.ltls    = []
        self.fairness = []

    # -- constraints --------------------------------------------------------
    def init_constraint(self, ch):   self.init.append(ch[0])
    def trans_constraint(self, ch):  self.trans.append(ch[0])
    def invar_constraint(self, ch):  self.invar.append(ch[0])
    def ltlspec(self, ch):           self.ltls.append(ch[0])

    def fairness_constraint(self, ch):
        if len(ch) == 1:
            self.fairness.append(Justice(ch[0]))
        else:
            self.fairness.append(Compassion(ch[0], ch[1]))

    # -- bool_atom ----------------------------------------------------------
    def bool_atom(self, ch):
        tok = ch[0]
        if tok.type == 'TRUE_KW':
            return BooleanValue('TRUE')
        if tok.type == 'FALSE_KW':
            return BooleanValue('FALSE')
        return self._resolve(str(tok))

    # -- arith_expr ---------------------------------------------------------
    def arith_expr(self, ch):
        if len(ch) == 1:
            c = ch[0]
            if isinstance(c, Token):
                name = str(c)
                if c.type == 'INT_LITERAL':
                    return IntLiteral(int(c))
                # IDENTIFIER — resolve using symbol table
                return self._resolve(name)
            return c   # already a logic object
        if len(ch) == 2:
            if isinstance(ch[0], Token) and ch[0].type == 'NEXT':
                inner = ch[1]
                if isinstance(inner, IntExpression):
                    return NextInt(inner)
                elif isinstance(inner, EnumExpression):
                    return NextEnum(inner)
                else:
                    return NextBool(inner)
        if len(ch) == 3:
            left, op, right = ch
            if isinstance(op, Token):
                match op.type:
                    case 'PLUS':   return IntAdd(left, right)
                    case 'MINUS':  return IntSub(left, right)
                    case 'TIMES':  return IntMul(left, right)
                    case 'DIVIDE': return IntDiv(left, right)
                    case 'MOD':    return IntMod(left, right)
        raise Exception(f"Unexpected arith_expr: {ch}")

    def _resolve(self, name):
        """Resolve an identifier to the correct logic type."""
        if name in self.boolean_variables:
            return BooleanIdentifier(name)
        if name in self.enum_variables:
            return EnumIdentifier(name)
        if name in self.enum_values:
            return EnumValue(name)
        if name in self.int_variables:
            return IntIdentifier(name)
        if name == 'TRUE':
            return BooleanValue('TRUE')
        if name == 'FALSE':
            return BooleanValue('FALSE')
        raise Exception(f"Unknown identifier: '{name}'")

    def INT_LITERAL(self, tok):
        return IntLiteral(int(tok))

    # -- enum helpers -------------------------------------------------------
    def enum_expr_lhs(self, ch):
        if len(ch) == 1:
            name = str(ch[0])
            if name in self.enum_variables:
                return EnumIdentifier(name)
            return EnumIdentifier(name)
        # NEXT "(" IDENTIFIER ")"
        name = str(ch[1])
        return NextEnum(EnumIdentifier(name))

    def enum_set(self, ch):
        result = []
        for t in ch:
            name = str(t)
            if name in self.enum_variables:
                result.append(EnumIdentifier(name))
            else:
                result.append(EnumValue(name))
        return result

    # -- bool_expr ----------------------------------------------------------
    def bool_expr(self, ch):
        if len(ch) == 1:
            return ch[0]
        if len(ch) == 2:
            op = ch[0]
            if isinstance(op, Token) and op.type == 'NOT':
                return Not(ch[1])
        if len(ch) == 3:
            left, op, right = ch
            if not isinstance(op, Token):
                raise Exception(f"Expected operator token, got {op}")
            match op.type:
                case 'AND':     return And(left, right)
                case 'OR':      return Or(left, right)
                case 'IMPLIES': return Implies(left, right)
                case 'EQ':      return _cmp_or_eq(left, '=',  right)
                case 'NEQ':     return _cmp_or_eq(left, '!=', right)
                case 'LT':      return IntCmp(left, '<',  right)
                case 'LE':      return IntCmp(left, '<=', right)
                case 'GT':      return IntCmp(left, '>',  right)
                case 'GE':      return IntCmp(left, '>=', right)
                case 'IN':      return In(left, right)
        raise Exception(f"Unexpected bool_expr children: {ch}")

    # -- ltl ----------------------------------------------------------------
    def ltl(self, ch):
        if len(ch) == 1:
            return ch[0]
        if len(ch) == 2:
            op, sub = ch
            if isinstance(op, Token):
                match op.type:
                    case 'G':    return G(sub)
                    case 'F':    return F(sub)
                    case 'X':    return X(sub)
                    case 'Y':    return Y(sub)
                    case 'H':    return H(sub)
                    case 'O_OP': return O(sub)
                    case 'NOT':  return Not(sub)
        if len(ch) == 3:
            left, op, right = ch
            match op.type:
                case 'AND':     return And(left, right)
                case 'OR':      return Or(left, right)
                case 'IMPLIES': return Implies(left, right)
                case 'U':       return U(left, right)
                case 'R':       return R(left, right)
        raise Exception(f"Unexpected ltl children: {ch}")


def _cmp_or_eq(left, op, right):
    """Dispatch = and != to the correct comparison class based on operand types."""
    if isinstance(left, IntExpression) or isinstance(right, IntExpression):
        return IntCmp(left, op, right)
    if op == '=':
        return Eq(left, right)
    return Neq(left, right)
