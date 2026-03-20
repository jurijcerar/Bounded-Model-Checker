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
    elif isinstance(expression, IntExpression):
        return NextInt(expression)
    else:
        raise Exception("Next operator must have a boolean, enum, or integer expression")


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

class Justice(Expression):
    """A justice (FAIRNESS/JUSTICE) constraint: formula f must hold infinitely often."""
    def __init__(self, formula):
        self.formula = formula

    def __repr__(self) -> str:
        return f"JUSTICE {self.formula}"

    def is_satisfied_in_loop(self, k, l, vars):
        """In a (k,l)-loop, 'infinitely often' means 'at some step in the loop [l..k]'."""
        return z3.Or(*[self.formula.to_z3(k, l, j, vars) for j in range(l, k + 1)])


class Compassion(Expression):
    """A compassion constraint: if p holds infinitely often, then q must also hold infinitely often."""
    def __init__(self, p, q):
        self.p = p
        self.q = q

    def __repr__(self) -> str:
        return f"COMPASSION ({self.p}, {self.q})"

    def is_satisfied_in_loop(self, k, l, vars):
        """In a (k,l)-loop: if p holds at some loop step, then q must also hold at some loop step."""
        p_inf = z3.Or(*[self.p.to_z3(k, l, j, vars) for j in range(l, k + 1)])
        q_inf = z3.Or(*[self.q.to_z3(k, l, j, vars) for j in range(l, k + 1)])
        return z3.Implies(p_inf, q_inf)


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


# ---------------------------------------------------------------------------
# Past LTL operators
# ---------------------------------------------------------------------------
# For a finite path s_0 ... s_k the "predecessor" of step i is:
#   pred(i) = i - 1   for i > 0
#   pred(0) = 0       (no previous state; conventionally the formula is False at i=0 for Y)

class Y(LTLFormula):
    """Yesterday / Previous operator.  Y φ holds at i iff φ held at i-1.
    At step 0 (the start of the path) Y φ is False by convention."""

    def __init__(self, formula):
        self.formula = formula

    def __repr__(self) -> str:
        return "Y " + str(self.formula)

    def to_z3(self, k, l, i, vars):
        if i == 0:
            return z3.BoolVal(False)
        return self.formula.to_z3(k, l, i - 1, vars)


class O(LTLFormula):
    """Once operator.  O φ holds at i iff φ held at some step j ≤ i."""

    def __init__(self, formula):
        self.formula = formula

    def __repr__(self) -> str:
        return "O " + str(self.formula)

    def to_z3(self, k, l, i, vars):
        return z3.Or(*[self.formula.to_z3(k, l, j, vars) for j in range(0, i + 1)])


class H(LTLFormula):
    """Historically operator.  H φ holds at i iff φ held at all steps j ≤ i."""

    def __init__(self, formula):
        self.formula = formula

    def __repr__(self) -> str:
        return "H " + str(self.formula)

    def to_z3(self, k, l, i, vars):
        return z3.And(*[self.formula.to_z3(k, l, j, vars) for j in range(0, i + 1)])


# ---------------------------------------------------------------------------
# Integer expressions
# ---------------------------------------------------------------------------

class IntExpression(Expression):
    """Base class for integer-valued expressions."""
    pass


class IntIdentifier(IntExpression):
    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return self.name

    def to_z3(self, k, l, i, vars):
        return vars[f'{self.name}{i}']


class IntLiteral(IntExpression):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return str(self.value)

    def to_z3(self, k, l, i, vars):
        return z3.IntVal(self.value)


class IntAdd(IntExpression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} + {self.right})"

    def to_z3(self, k, l, i, vars):
        return self.left.to_z3(k, l, i, vars) + self.right.to_z3(k, l, i, vars)


class IntSub(IntExpression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} - {self.right})"

    def to_z3(self, k, l, i, vars):
        return self.left.to_z3(k, l, i, vars) - self.right.to_z3(k, l, i, vars)


class IntMul(IntExpression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} * {self.right})"

    def to_z3(self, k, l, i, vars):
        return self.left.to_z3(k, l, i, vars) * self.right.to_z3(k, l, i, vars)


class IntDiv(IntExpression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} / {self.right})"

    def to_z3(self, k, l, i, vars):
        return self.left.to_z3(k, l, i, vars) / self.right.to_z3(k, l, i, vars)


class IntMod(IntExpression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} mod {self.right})"

    def to_z3(self, k, l, i, vars):
        return self.left.to_z3(k, l, i, vars) % self.right.to_z3(k, l, i, vars)


class NextInt(IntExpression):
    """next() applied to an integer expression."""
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self) -> str:
        return f"next({self.expression})"

    def to_z3(self, k, l, i, vars):
        return self.expression.to_z3(k, l, Expression.succ(k, l, i), vars)


def NextArith(expression):
    """Factory: wraps an integer expression in NextInt."""
    return NextInt(expression)


# Integer comparison — produces a BooleanExpression
class IntCmp(BooleanExpression, LTLFormula):
    def __init__(self, left, op: str, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} {self.op} {self.right})"

    def to_z3(self, k, l, i, vars):
        lv = self.left.to_z3(k, l, i, vars)
        rv = self.right.to_z3(k, l, i, vars)
        match self.op:
            case "=":  return lv == rv
            case "!=": return lv != rv
            case "<":  return lv < rv
            case "<=": return lv <= rv
            case ">":  return lv > rv
            case ">=": return lv >= rv