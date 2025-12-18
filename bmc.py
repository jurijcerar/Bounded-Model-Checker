from z3 import *
import copy

class BoundedModelChecker:
    def __init__(self, smv_model):
        self.bool_var = smv_model['boolean_variables']
        self.enum_var = smv_model['enum_variables']
        self.enum_val = smv_model['enum_values']
        self.init = smv_model['init']
        self.trans = smv_model['trans']
        self.invar = smv_model['invar']
        self.ltl = smv_model['ltl']
        self.enum_types = {}

        self.model = []


    def declare_variables(self, k):
    # Declare boolean variables
        bool_vars = {f'{var_name}{i}': z3.Bool(f'{var_name}{i}') for var_name in self.bool_var for i in range(k + 1)}
        
        enum_vars = {}
        existing_enum_type = None
        
        for var_name, values in zip(self.enum_var, self.enum_val):
            # Check if an existing enum type matches the current values
            for enum_type, enum_values in self.enum_types.values():
                if values == [str(ev) for ev in enum_values]:
                    existing_enum_type = (enum_type, enum_values)
                    break
            
            if existing_enum_type:
                enum_type, enum_values = existing_enum_type
                for ev in enum_values:
                    enum_vars[f'{ev}'] = ev
            else:
                # Create a new enum type since no match was found
                enum_type, enum_values = z3.EnumSort(var_name, values)
                for ev in enum_values:
                    enum_vars[f'{ev}'] = ev
                self.enum_types[var_name] = (enum_type, enum_values)

            # Declare the variables for each step
            for i in range(k + 1):
                enum_var_name = f'{var_name}{i}'
                enum_vars[enum_var_name] = z3.Const(enum_var_name, enum_type)
            
            existing_enum_type = None  # Reset for the next variable

        all_vars = bool_vars | enum_vars
        
        return all_vars

    
    def encode_init(self, k, l, vars):
        inits = [ expr.to_z3(k, l, 0, vars) for expr in self.init ]
        return inits

    def encode_trans(self, k, l, vars):
        trans = [ expr.to_z3(k, l, i, vars) for expr in self.trans for i in range(k + 1)  ]
        return trans

    def encode_invar(self, k, l, vars):
        invar = [ expr.to_z3(k, l, i, vars) for expr in self.invar for i in range(k + 1)  ]
        return invar

    def encode_ltl(self, k, l, vars):
        ltl = []
        for expr in self.ltl:
            z3_expr = expr.to_z3(k, l, 0, vars)
            ltl.append(z3.Not(z3_expr))
        
        '''expr = self.ltl[1]
        z3_expr = expr.to_z3(k, l, 0, vars)
        ltl.append(z3.Not(z3_expr))'''
    
        return ltl


    def check(self, k, l):
        vars = self.declare_variables(k)

        solver = z3.Solver()

        init = self.encode_init(k,l,vars)
        trans = self.encode_trans(k,l,vars)
        invar = self.encode_invar(k,l,vars)
        ltl = self.encode_ltl(k,l,vars)

        solver.add(init)
        solver.add(z3.And(trans))
        solver.add(z3.And(invar))
        #solver.add(ltl)

        for i, exp in enumerate(ltl):
            exp_solv = copy.copy(solver)
            exp_solv.add(exp)

            if exp_solv.check() == z3.sat: 
                print(f"LTL Expression at index {i}: {self.ltl[i]}")  # Print the index and LTL expression
                self.model.append(exp_solv.model())
                break
            else:
                self.model.append(None)



    def print_model(self, k, modl):
        vars = self.declare_variables(k)

        for i in range(k + 1):
            print(f'Step {i}:')
            for var_name in vars:
                if var_name.endswith(str(i)):  # Ensure we're looking at the right step
                    var_value = modl[vars[var_name]]
                    print(f'  {var_name[:-len(str(i))]} = {var_value}')


    def model(self):
        if (self.model == None):
            raise Exception('No model available')
        
        return self.model