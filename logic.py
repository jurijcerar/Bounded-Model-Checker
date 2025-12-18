'''
This file contains definitions of expressions and formulas.
'''
from z3 import *

class Expression:
      
    @staticmethod
    def succ(k, l, i):
        return (i + 1) if i < k else l


class BooleanExpression(Expression):
    pass


class EnumExpression(Expression):
    pass


class LTLFormula(Expression):
    pass


class EnumIdentifier(EnumExpression):
    def type_check(name):
        if not isinstance(name, str):
            raise Exception("Identifier name must be a string")
    
    def __init__(self, name):
        EnumIdentifier.type_check(name)
        self.name = name

    def __repr__(self) -> str:
        return self.name

    def evaluate(self, interpretation):
        return interpretation[self.name]
    
    def to_z3(self, k, l, i, vars):
        return vars[f'{self.name}{i}']


class BooleanIdentifier(BooleanExpression, LTLFormula):
    def type_check(name):
        if not isinstance(name, str):
            raise Exception("Identifier name must be a string")
    
    def __init__(self, name):
        BooleanIdentifier.type_check(name)
        self.name = name

    def __repr__(self) -> str:
        return self.name

    def evaluate(self, interpretation):
        return interpretation[self.name]
    
    def to_z3(self, k, l, i, vars):
        return vars[f'{self.name}{i}']


class EnumValue(EnumExpression):
    def type_check(name):
        if not isinstance(name, str):
            raise Exception("Enum value must be a string")
    
    def __init__(self, name):
        EnumValue.type_check(name)
        self.name = name

    def __repr__(self) -> str:
        return self.name

    def evaluate(self, interpretation):
        return self.name
    
    def to_z3(self, k, l, i, vars):
        return vars[self.name]


class BooleanValue(BooleanExpression):
    def type_check(name):
        if name not in ["TRUE", "FALSE"]:
            raise Exception("Boolean value must be True or False")
    
    def __init__(self, name):
        BooleanValue.type_check(name)
        self.name = name

    def __repr__(self) -> str:
        return self.name

    def evaluate(self, interpretation):
        return True if self.name == "TRUE" else False
    
    def to_z3(self, k, l, i, vars):
        return True if self.name == "TRUE" else False


class NextBool(BooleanExpression):
    def type_check(expression):
        if not isinstance(expression, BooleanExpression):
            raise Exception("Next operator must have an expression")
    
    def __init__(self, expression):
        NextBool.type_check(expression)
        self.expression = expression

    def __repr__(self) -> str:
        return "next(" + str(self.expression) + ")"
    
    def to_z3(self, k, l, i, vars):
        return self.expression.to_z3(k,l,Expression.succ(k,l,i), vars)



class NextEnum(EnumExpression):
    def type_check(expression):
        if not isinstance(expression, EnumExpression):
            raise Exception("Next operator must have an expression")
    
    def __init__(self, expression):
        NextEnum.type_check(expression)
        self.expression = expression

    def __repr__(self) -> str:
        return "next(" + str(self.expression) + ")"
    
    def to_z3(self, k, l, i, vars):
        return self.expression.to_z3(k,l,Expression.succ(k,l,i), vars)


def Next(expression):
    if isinstance(expression, BooleanExpression):
        return NextBool(expression)
    elif isinstance(expression, EnumExpression):
        return NextEnum(expression)
    else:
        raise Exception("Next operator must have a boolean or enum expression")


class Not(BooleanExpression, LTLFormula):
    def type_check(expression):
        if not isinstance(expression, BooleanExpression) and not isinstance(expression, LTLFormula):
            raise Exception("Negated expression must be a boolean expression or LTL formula")
    
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self) -> str:
        return "¬" + str(self.expression)

    def evaluate(self, interpretation):
        return not self.expression.evaluate(interpretation)
    
    def to_z3(self, k, l, i, vars):
        return z3.Not(self.expression.to_z3(k,l,i, vars))


class And(BooleanExpression, LTLFormula):
    def type_check(left, right):
        if (not isinstance(left, BooleanExpression) and not isinstance(left, LTLFormula)) or \
              (not isinstance(right, BooleanExpression) and not isinstance(right, LTLFormula)):
            raise Exception("And expression must have boolean expressions or LTL formulas")
    
    def __init__(self, left, right):
        And.type_check(left, right)
        self.left = left
        self.right = right
        
    def __repr__(self) -> str:
        return "(" + str(self.left) + " ∧ " + str(self.right) + ")"

    def evaluate(self, interpretation):
        return self.left.evaluate(interpretation) and self.right.evaluate(interpretation)

    def to_z3(self, k, l, i, vars):
        return z3.And(self.left.to_z3(k,l,i, vars), self.right.to_z3(k,l,i, vars))

class Or(BooleanExpression, LTLFormula):
    def type_check(left, right):
        if (not isinstance(left, BooleanExpression) and not isinstance(left, LTLFormula)) or \
              (not isinstance(right, BooleanExpression) and not isinstance(right, LTLFormula)):
            raise Exception("Or expression must have boolean expressions or LTL formulas")
    
    def __init__(self, left, right):
        Or.type_check(left, right)
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return "(" + str(self.left) + " ∨ " + str(self.right) + ")"

    def evaluate(self, interpretation):
        return self.left.evaluate(interpretation) or self.right.evaluate(interpretation)

    def to_z3(self, k, l, i, vars):
        return z3.Or(self.left.to_z3(k,l,i, vars), self.right.to_z3(k,l,i, vars))

class Implies(BooleanExpression, LTLFormula):
    def type_check(left, right):
        if (not isinstance(left, BooleanExpression) and not isinstance(left, LTLFormula)) or \
              (not isinstance(right, BooleanExpression) and not isinstance(right, LTLFormula)):
            raise Exception("Implies expression must have two boolean expressions")
    
    def __init__(self, left, right):
        Implies.type_check(left, right)
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return "(" + str(self.left) + " → " + str(self.right) + ")"

    def evaluate(self, interpretation):
        return not self.left.evaluate(interpretation) or self.right.evaluate(interpretation)

    def to_z3(self, k, l, i, vars):
        return z3.Implies(self.left.to_z3(k,l,i, vars), self.right.to_z3(k,l,i, vars))

class Eq(BooleanExpression):
    def type_check(left, right):
        if not (isinstance(left, EnumExpression) and isinstance(right, EnumExpression)) and \
                not (isinstance(left, BooleanExpression) and isinstance(right, BooleanExpression)):
            raise Exception("Equals expression must have two expressions of same type")
    
    def __init__(self, left, right):
        Eq.type_check(left, right)
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return "(" + str(self.left) + " = " + str(self.right) + ")"

    def evaluate(self, interpretation):
        return self.left.evaluate(interpretation) == self.right.evaluate(interpretation)
    
    def to_z3(self, k, l, i, vars):
        left_expr = self.left.to_z3(k,l,i, vars)
        right_expr = self.right.to_z3(k,l,i, vars)
        return (left_expr == right_expr)

def Neq(left, right):
    return Not(Eq(left, right))


class In(BooleanExpression):
    def type_check(left, right):
        if not isinstance(left, EnumExpression) or not isinstance(right, list) \
            or not all(isinstance(element, EnumExpression) for element in right):
            raise Exception("In expression must have enum arguments") 
    
    def __init__(self, left, right):
        In.type_check(left, right)
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return "(" + str(self.left) + " ∈ " + str(self.right) + ")"

    def evaluate(self, interpretation):
        return self.left.evaluate(interpretation) in [self.right.evaluate(element) for element in self.right]

    def to_z3(self, k, l, i, vars):
        return z3.Or(*[self.left.to_z3(k,l,i, vars)
                   == r.to_z3(k,l,i, vars) for r in self.right])

class G(LTLFormula):
    def type_check(formula):
        if not isinstance(formula, LTLFormula) and not isinstance(formula, BooleanExpression):
            raise Exception("G operator must have a boolean expression or LTL formula")
    
    def __init__(self, formula):
        G.type_check(formula)
        self.formula = formula

    def __repr__(self) -> str:
        return "G " + str(self.formula)
    
    def to_z3(self, k, l, i, vars):
        ind_range = range(i, k + 1) if i < l else range(l, k + 1)
        return z3.And(*[self.formula.to_z3(k,l,j,vars) for j in ind_range])


class F(LTLFormula):
    def type_check(formula):
        if not isinstance(formula, LTLFormula) and not isinstance(formula, BooleanExpression):
            raise Exception("F operator must have a boolean expression or LTL formula")
        
    def __init__(self, formula):
        F.type_check(formula)
        self.formula = formula

    def __repr__(self) -> str:
        return "F " + str(self.formula)
    
    def to_z3(self, k, l, i, vars):
        ind_range = range(i, k + 1) if i < l else range(l, k + 1)
        return z3.Or(*[self.formula.to_z3(k,l,j,vars) for j in ind_range])


class X(LTLFormula):
    def type_check(formula):
        if not isinstance(formula, LTLFormula) and not isinstance(formula, BooleanExpression):
            raise Exception("X operator must have a boolean expression or LTL formula")
        
    def __init__(self, formula):
        X.type_check(formula)
        self.formula = formula

    def __repr__(self) -> str:
        return "X" + str(self.formula)
    
    def to_z3(self, k, l, i, vars):
        return self.formula.to_z3(k,l,Expression.succ(k,l,i),vars)


class U(LTLFormula):
    def type_check(left, right):
        if not isinstance(left, LTLFormula) and not isinstance(left, BooleanExpression):
            raise Exception("U operator left operand must be a boolean expression or LTL formula")
        if not isinstance(right, LTLFormula) and not isinstance(right, BooleanExpression):
            raise Exception("U operator right operand must be a boolean expression or LTL formula")
    
    def __init__(self, left, right):
        U.type_check(left, right)
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return "(" + str(self.left) + " U " + str(self.right) + ")"
    
    def to_z3(self, k, l, i, vars):
        return z3.Or(
            z3.Or(*[
                z3.And(
                    self.right.to_z3(k,l,j,vars),
                    z3.And(*[
                        self.left.to_z3(k,l,n,vars)
                        for n in range(i, j)
                    ])
                ) for j in range (i, k+1)
            ]),
            z3.Or(*[
                z3.And(
                    self.right.to_z3(k,l,j,vars),
                    z3.And(*[
                        self.left.to_z3(k,l,n,vars)
                        for n in range(i, k+1)
                    ]),
                    z3.And(*[
                        self.left.to_z3(k,l,n,vars)
                        for n in range(l, j)
                    ])  
                ) for j in range (l, i)
            ])
        )
    
class R(LTLFormula):
    def type_check(left, right):
        if not isinstance(left, LTLFormula) and not isinstance(left, BooleanExpression):
            raise Exception("R operator left operand must be a boolean expression or LTL formula")
        if not isinstance(right, LTLFormula) and not isinstance(right, BooleanExpression):
            raise Exception("R operator right operand must be a boolean expression or LTL formula")
    
    def __init__(self, left, right):
        R.type_check(left, right)
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return "(" + str(self.left) + " R " + str(self.right) + ")"
    
    def to_z3(self, k, l, i, vars):
        ind_range = range(i, k + 1) if i < l else range(l, k + 1)
        return z3.Or(
            z3.And(*[
                self.right.to_z3(k,l,j,vars)
                for j in ind_range
            ]),
            z3.Or(*[
                z3.And(
                    self.left.to_z3(k,l,j,vars),
                    z3.And(*[
                        self.right.to_z3(k,l,n,vars)
                        for n in range(i, j)
                    ])
                ) for j in range (i, k+1)
            ]),
            z3.Or(*[
                z3.And(
                    self.left.to_z3(k,l,j,vars),
                    z3.And(*[
                        self.right.to_z3(k,l,n,vars)
                        for n in range(i, k+1)
                    ]),
                    z3.And(*[
                        self.right.to_z3(k,l,n,vars)
                        for n in range(l, j)
                    ])  
                ) for j in range (l, i)
            ])
        )