import globals

# 5-value logic constants
X = 'X'
ZERO = '0'
ONE = '1'
D = 'D'
DB = "D'"

def invert_value(val):
    if val == ONE:
        return ZERO
    if val == ZERO:
        return ONE
    if val == D:
        return DB
    if val == DB:
        return D
    return X

def PODEM():
    if error_at_PO():
        return 'SUCCESS'
    
    if test_not_possible():
        return 'FAILURE'

    # set intial fault line on first run
    # find necessary input to propagate fault
    k, vk = Objective() 
    if k is None:
        print("No Objective found, test not possible.")
        return 'FAILURE'

    print(f"Calling backtrace on line {k} for value {vk}")
    # using input from Objective, backtrace to PI (does not change any values)
    j, vj = Backtrace(k, vk)
    if j is None:
        return 'FAILURE'

    print(f"Calling imply on PI {j} for value {vj}")
    # from PI, keep evaluating gate output until its no longer changing outputs
    Imply(j, vj)

    if PODEM() == 'SUCCESS': return 'SUCCESS'

    print(f"Reversing decision on PI {j} to value {invert_value(vj)}")
    # reverse decision
    vj_complement = invert_value(vj)
    Imply(j, vj_complement) 

    if PODEM() == 'SUCCESS': return 'SUCCESS'

    print(f"Reversing decision on PI {j} to 'X'")
    # reverse j to 'X'
    Imply(j, X)

    return 'FAILURE'

def Objective():
    print(f"fault line: {globals.target_line}, fault value: {globals.fault_value}")
    if globals.wire_values[globals.target_line] == 'X':
        if globals.fault_value == '1':
            return (globals.target_line, DB)
        else:
            return (globals.target_line, D)
    
    D_frontier = get_D_frontier()
    print(f"D-frontier gates: {[gate.name for gate in D_frontier]}")

    if D_frontier: # D-frontier not empty

        gate = D_frontier[-1] # select last gate
        print(f"Selected gate {gate.name} from D-frontier with inputs {gate.inputs} and gate.c = {gate.c}")
        for inp in gate.inputs:
            if globals.wire_values[inp] == 'X':
                if gate.c == 0:
                    complement = ONE
                else:
                    complement = ZERO
                print(f"complement: {complement}")
                return (inp, complement)
    return (None, None)

def Backtrace(k, complement):
    v = complement
    while k not in globals.primary_inputs: # k is not PI
        for gate in globals.gates:
            if k in gate.output:
                for j in gate.inputs:
                    if globals.wire_values[j] == 'X':
                        #v = v ^ gate.inv
                        v = invert_value(v) if gate.inv == 1 else v
                        k = j
                    if k in globals.primary_inputs:
                        return (k,v)
    return (k, v) # k is already a PI

def Imply(j,vj): # first call is a PI line (j) and needed value (vj)
    globals.wire_values[j] = vj # assigning PI to a value
    print(f"Set PI {j} to value {vj}")

    # evaluating gates (assigning outputs) until output does not change
    changed = True
    while changed:
        changed = False
        for gate in globals.gates:
            if gate.gate_type == 'fanout':
                for out in gate.output:
                    old = globals.wire_values.get(out, X)
                    new = globals.wire_values[gate.inputs[0]]
                    if new != old:
                        print(f"{gate.name} output {out} changing from {old} to {new}")
                        globals.wire_values[out] = new
                        changed = True
            else:
                old = globals.wire_values.get(gate.output[0], X)
                new = evaluate_gate(gate)
                # print(f"new: {new}, old: {old}")
                if new != old:
                    print(f"{gate.name} output {gate.output[0]} changing from {old} to {new}")
                    globals.wire_values[gate.output[0]] = new
                    changed = True

def evaluate_gate(gate):
    # Returns new 5-valued logic for gate.output[0] based on gate.inputs
    in_vals = [globals.wire_values.get(i, X) for i in gate.inputs]

    # NOT gate
    if gate.gate_type == 'not':
        return invert_value(in_vals[0])

    control = str(gate.c)
    control = ONE if control == '1' else ZERO

    if control in in_vals:
        out = control
    elif X not in in_vals:
        has_d = D in in_vals
        has_db = DB in in_vals
        if has_d and not has_db:
            out = D
        elif has_db and not has_d:
            out = DB
        elif has_d and has_db:
            # conflict
            out = X
        else:
            control_complement = invert_value(control)
            out = control_complement
    else:
        out = X


    # Account for gate inversion
    if gate.inv == 1:
        out = invert_value(out)

    return out

def error_at_PO():
    # True if any primary output has D or D'
    for po in globals.primary_outputs:
        val = globals.wire_values.get(po, X)
        if val == D or val == DB:
            return True
    return False

def test_not_possible():
    globals.recursion_depth += 1
    if globals.recursion_depth > globals.max_recursion_depth:
        print("Max recursion depth reached, test not possible.")
        return True


def get_D_frontier():
    D_frontier = []
    for gate in globals.gates:
        for inp in gate.inputs:
            if globals.wire_values.get(inp, X) == D or globals.wire_values.get(inp, X) == DB:
                output = globals.wire_values.get(gate.output[0], X)
                if output == D or output == DB:
                    break
                D_frontier.append(gate)
                break

    return D_frontier