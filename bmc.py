import z3
import copy

class BoundedModelChecker:
    def __init__(self, smv_model):
        self.bool_var = smv_model['boolean_variables']
        self.enum_var = smv_model['enum_variables']
        self.enum_val = smv_model['enum_values']
        self.int_var   = smv_model.get('int_variables', [])
        self.int_ranges = smv_model.get('int_ranges', {})
        self.init = smv_model['init']
        self.trans = smv_model['trans']
        self.invar = smv_model['invar']
        self.ltl = smv_model['ltl']
        self.fairness_constraints = smv_model.get('fairness', [])
        self.enum_types = {}
        self._sort_gen  = 0
        self._model = []

    @property
    def model(self):
        return self._model


    def declare_variables(self, k):
        bool_vars = {f'{v}{i}': z3.Bool(f'{v}{i}')
                     for v in self.bool_var for i in range(k + 1)}

        int_vars = {f'{v}{i}': z3.Int(f'{v}{i}')
                    for v in self.int_var for i in range(k + 1)}

        enum_vars = {}
        existing_enum_type = None

        for var_name, values in zip(self.enum_var, self.enum_val):
            for enum_type, enum_values in self.enum_types.values():
                if values == [str(ev) for ev in enum_values]:
                    existing_enum_type = (enum_type, enum_values)
                    break

            if existing_enum_type:
                enum_type, enum_values = existing_enum_type
            else:
                # Unique sort name per check() call avoids Z3 "already declared" error
                unique_name = f'{var_name}_{self._sort_gen}'
                enum_type, enum_values = z3.EnumSort(unique_name, values)
                self.enum_types[var_name] = (enum_type, enum_values)

            for ev in enum_values:
                enum_vars[str(ev)] = ev
            for i in range(k + 1):
                enum_vars[f'{var_name}{i}'] = z3.Const(f'{var_name}{i}', enum_type)

            existing_enum_type = None

        return bool_vars | int_vars | enum_vars

    def _int_range_constraints(self, k, vars):
        """Add lo <= v_i <= hi for every range-typed integer variable."""
        constraints = []
        for var_name, rng in self.int_ranges.items():
            if rng is None:
                continue
            lo, hi = rng
            for i in range(k + 1):
                v = vars[f'{var_name}{i}']
                constraints.append(z3.And(v >= lo, v <= hi))
        return constraints

    
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


    def encode_fairness(self, k, l, vars):
        """Encode fairness constraints for a (k,l)-loop.
        
        For a loop to be fair, all fairness constraints must be satisfied.
        - Justice(f): f must hold at some step in the loop [l..k]
        - Compassion(p,q): if p holds at some loop step, q must too
        
        If there are no fairness constraints, every path is considered fair.
        """
        return [fc.is_satisfied_in_loop(k, l, vars) for fc in self.fairness_constraints]

    def check(self, k, l):
        self._model = []
        self._sort_gen = getattr(self, '_sort_gen', 0) + 1   # unique suffix per call
        self.enum_types = {}
        vars = self.declare_variables(k)
        self._last_vars = vars

        solver = z3.Solver()

        init     = self.encode_init(k, l, vars)
        trans    = self.encode_trans(k, l, vars)
        invar    = self.encode_invar(k, l, vars)
        ltl      = self.encode_ltl(k, l, vars)
        fairness = self.encode_fairness(k, l, vars)
        ranges   = self._int_range_constraints(k, vars)

        solver.add(init)
        solver.add(z3.And(trans))
        solver.add(z3.And(invar))
        if ranges:
            solver.add(z3.And(ranges))
        if fairness:
            solver.add(z3.And(fairness))

        for i, exp in enumerate(ltl):
            exp_solv = copy.copy(solver)
            exp_solv.add(exp)

            if exp_solv.check() == z3.sat:
                print(f"LTL Expression at index {i}: {self.ltl[i]}")
                self._model.append(exp_solv.model())
                break
            else:
                self._model.append(None)



    def print_model(self, k, modl):
        vars = getattr(self, '_last_vars', None) or self.declare_variables(k)

        for i in range(k + 1):
            print(f'Step {i}:')
            for var_name in vars:
                if var_name.endswith(str(i)):  # Ensure we're looking at the right step
                    var_value = modl[vars[var_name]]
                    print(f'  {var_name[:-len(str(i))]} = {var_value}')


    def get_model(self):
        if not self._model:
            raise Exception('No model available')
        return self._model