from itertools import chain
from lark import Visitor, Transformer, Lark, Token

from logic import *


with open('grammar.lark') as f:
    _grammar = f.read()


def parse(text):
    parser = Lark(_grammar, start='start')
    tree = parser.parse(text)
    declaration_parser = _DeclarationParser()
    declaration_parser.visit(tree)
    constraint_parser = _ConstraintParser(
        declaration_parser.boolean_variables,
        declaration_parser.enum_variables,
        declaration_parser.enum_values
    )
    constraint_parser.transform(tree)
    return {
        "boolean_variables" : declaration_parser.boolean_variables,
        "enum_variables" : declaration_parser.enum_variables,
        "enum_values" : declaration_parser.enum_values, 
        "invar" : constraint_parser.invar,
        "init" : constraint_parser.init,
        "trans" : constraint_parser.trans,
        "ltl" : constraint_parser.ltls
    }


class _DeclarationParser(Visitor):
    def __init__(self):
        self.boolean_variables = []
        self.enum_variables = []
        self.enum_values = []
    
    def var_list(self, tree):
        if isinstance(tree.children[1].children[0], Token):
            self.boolean_variables.append(tree.children[0].value)
        else:
            self.enum_variables.append(tree.children[0].value)
            self.enum_values.append([token.value for token in tree.children[1].children[0].children])

    def init_constraint(self, tree):
        if hasattr(tree.children[0], 'contains_next'):
            raise Exception("INIT constraint cannot contain next operator")

    def invar_constraint(self, tree):
        if hasattr(tree.children[0], 'contains_next'):
            raise Exception("INVAR constraint cannot contain next operator")

    def expr(self, tree):
        if len(tree.children) == 2 and tree.children[0].type == 'NEXT':
            tree.contains_next = None
        elif any(hasattr(child, 'contains_next') for child in tree.children):
                tree.contains_next = None

class _ConstraintParser(Transformer):
    def __init__(self, boolean_variables, enum_variables, enum_values):
        self.boolean_variables = boolean_variables
        self.enum_variables = enum_variables
        self.enum_values = list(chain(*enum_values))
        self.invar = []
        self.init = []
        self.trans = []
        self.ltls = []
    
    def invar_constraint(self, children):
        self.invar.append((children[0]))  
        
    def init_constraint(self, children):
        self.init.append((children[0]))
    
    def trans_constraint(self, children):
        self.trans.append((children[0]))
    
    def expr(self, children):
        return children[0]
    
    def IDENTIFIER(self, data):
        if data in self.boolean_variables:
            return BooleanIdentifier(data)
        elif data in ['TRUE', 'FALSE']:
            return BooleanValue(data)
        elif data in self.enum_variables:
            return EnumIdentifier(data)
        elif data in self.enum_values:
            return EnumValue(data)

    def enum(self, children):
        return [children]

    def expr(self, children):
        match len(children):
            case 1:
                return children[0]
            case 2:
                match children[0].type:
                    case 'NOT':
                        return Not(children[1])
                    case 'NEXT':
                        return Next(children[1])
            case 3:
                match children[1].type:
                    case 'AND':
                        return And(children[0], children[2])
                    case 'OR':
                        return Or(children[0], children[2])
                    case 'IMPLIES':
                        return Implies(children[0], children[2])
                    case 'EQ':
                        return Eq(children[0], children[2])
                    case 'NEQ':
                        return Neq(children[0], children[2])
                    case 'IN':
                        return In(children[0], children[2])
                    case 'U':
                        return U(children[0], children[2])
                    case 'R':
                        return R(children[0], children[2])

    def enum_expr(self, children):
        return children

    def case_body(self, children):
        if len(children) == 3:
            return ([children[0]] + children[2][0], [children[1]] + children[2][1], children[2][2])
        else:
            return ([children[0]], [children[1]], \
                "Boolean" if isinstance(children[1], BooleanExpression) else "Enum")

    def ltlspec(self, children):
        self.ltls.append(children[0])

    def ltl(self, children):
        match len(children):
            case 1:
                return children[0]
            case 2:
                match children[0].type:
                    case 'G':
                        return G(children[1])
                    case 'F':
                        return F(children[1])
                    case 'X':
                        return X(children[1])
                    case 'NOT':
                        return Not(children[1])
            case 3:
                match children[1].type:
                    case 'AND':
                        return And(children[0], children[2])
                    case 'OR':
                        return Or(children[0], children[2])
                    case 'IMPLIES':
                        return Implies(children[0], children[2])
                    case 'EQ':
                        return Eq(children[0], children[2])
                    case 'NEQ':
                        return Neq(children[0], children[2])
                    case 'IN':
                        return In(children[0], children[2])
                    case 'U':
                        return U(children[0], children[2])
                    case 'R':
                        return R(children[0], children[2])
