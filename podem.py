import globals

# main functions: PODEM, Objective, Backtrace, Imply
# all functions above # line will be abstracted to other files

# no longer used
def inject_fault(fault_line, fault_value):
    if fault_line not in globals.wire_values:
        print("inject fault: invalid fault line")
        return "FAILURE"
    if fault_value == '0': 
        globals.wire_values[fault_line] = '1'  # s-a-0 fault
    elif fault_value == '1':
        globals.wire_values[fault_line] = "0"  # s-a-1 fault
    else:
        print("inject_fault: Invalid fault value.")
        return "FAILURE"
    set_initial_gate_fault(fault_line, fault_value)
    return podem(fault_line, fault_value)

# no longer used
def set_initial_gate_fault(fault_line, fault_value):
    for gate in globals.gates:
        for inp in gate.inputs:
            if inp == fault_line:
                if fault_value == gate.inv:
                    value = "D"
                else:
                    value = "D'"
                globals.wire_values[gate.output] = value 

def error_at_PO():
    # Check if there is an error at any primary output

    # testing purpose: print wire values
    for wire, value in globals.wire_values.items():
        print(f"{wire}: {value}")
    print("error_at_PO: Done printing wire values.")

    for po in globals.primary_outputs:
        if globals.wire_values[po] == 'D' or globals.wire_values[po] == "D'":
            print("error_at_PO: Error at PO found.")
            return True
        
    print("error_at_PO: No error at PO.")
    return False

def test_possible():
    # Check if test is not possible based on current wire values and D-frontier
    if error_at_PO():
        print("test_possible: Test possible due to error at PO.")
        return True
    
    d_frontier = get_d_frontier()
    print(f"test_possible: D-frontier size: {len(d_frontier)}")
    print(f"test_possible: D-frontier gates: {[gate.name for gate in d_frontier]}")
    return len(d_frontier) > 0

def evaluate_gate(gate):
    input_values = [globals.wire_values[inp] for inp in gate.inputs]

    if gate.gate_type == "not":
        return input_values[0] == '1' and '0' or input_values[0] == '0' and '1' or 'X'
    
    c = str(gate.c)
    c_complement = '1' if gate.c == 0 else '0'

    # output is control value if input is control value
    if c in input_values:
        out = c
    else:
        if 'X' in input_values:
            out = 'X'
        else:
            # all inputs non-controlling means output is c_complement
            out = c_complement
    
    # handle d values
    d_present = 'D' in input_values
    dc_present = "D'" in input_values

    if d_present or dc_present:
        # D can't propagate with controlling values present
        if c in input_values:
            pass # output stays c
        else:
            # D passes through
            if d_present and not dc_present:
                out = 'D'
            elif dc_present and not d_present:
                out = "D'"
            else:
                out = 'X'

    if gate.inv == 1:
        out = invert_value(out)

    return out

def invert_value(value):
    if value == '1':
        return '0'
    elif value == '0':
        return '1'
    elif value == 'D':
        return "D'"
    elif value == "D'":
        return 'D'
    else:
        return 'X'


def get_d_frontier():
    d_frontier = []
    for gate in globals.gates:
        output_value = globals.wire_values.get(gate.output, 'X')
        if output_value == 'X':  
            inp_value = [globals.wire_values.get(inp, 'X') for inp in gate.inputs]
            if 'D' in inp_value or "D'" in inp_value:
                d_frontier.append(gate)
    if not d_frontier:
        print("get_d_frontier: D-frontier is empty.")
    for gate in d_frontier:
        print(f"get_d_frontier: D-frontier gate: {gate.name} with output {gate.output}")
    return d_frontier
    
def find_gate_by_output(output_line):
    for gate in globals.gates:
        if gate.output == output_line:
            return gate
    return None

def get_test_vector():
    test_vector = {}
    for pi in globals.primary_inputs:
        value = globals.wire_values.get(pi, 'X')
        test_vector[pi] = value    
    print_test_vector(test_vector)

def print_test_vector(test_vector):
    for pi in sorted(test_vector.keys()):
        print(f"{pi}: {test_vector[pi]}")

    
##########################################################

def podem(fault_line, fault_value):
    if error_at_PO():
        return "SUCCESS"

    """
    if not test_possible():
        print("Returning failure")
        return "FAILURE"
    """

    # get objective
    # returns fault_line and fault_value complement
    k, vk = objective(fault_line, fault_value)
    if k is None:
        return "FAILURE"

    j, vj = backtrace(k, vk) # j is a PI
    if j is None:
        return "FAILURE"
    
    imply(j, vj) # 5-value simulation with PI assignments

    if podem(fault_line, fault_value) == "SUCCESS":
        return "SUCCESS"

    vj_complement = '1' if vj == '0' else '0'
    imply(j, vj_complement) # reverse decision

    if podem(fault_line, fault_value) == "SUCCESS":
        return "SUCCESS"

    imply(j, 'X') # reverse j to x

    return "FAILURE" # D-frontier becomes empty

def objective(fault_line, fault_value):
    print(f"objective: objective called with {fault_line} s-a-{fault_value}")

    # target fault is activated if 'X'
    if globals.wire_values[fault_line] == 'X':
        # complement s-a-value to activate fault
        target_value = '1' if fault_value == '0' else '0'
        globals.wire_values[fault_line] = target_value
        return (fault_line, target_value)
    
    # find gate in D-frontier to propagate fault
    d_frontier = get_d_frontier()

    if not d_frontier:
        return (None, None)
    
    # select a gate (gate) from the D-frontier
    gate = d_frontier[0]  # select first gate in D-frontier
    
    # select an input (inp) of (gate) with value 'X'
    # return complement of controlling value of (gate)
    for inp in gate.inputs:
        if globals.wire_values[inp] == 'X':
            c_complement = '1' if gate.c == 0 else '0'
            return (inp, c_complement)
    
    return (None, None)

def backtrace(k, vk):
    # k is current line, vk is desired value at k
    v = vk
    
    while k not in globals.primary_inputs: # k/current_line is not PI
        gate = find_gate_by_output(k)
        print(f"backtrace: At gate {gate.name} for line {k} needing value {v}")
        if gate is None:
            return (None, None)

        # select an input j of k with value X
        j = None
        for inp in gate.inputs:
            if globals.wire_values[inp] == 'X':
                j = inp
                print(f"backtrace: Selected input {j} for backtrace.")
                break
        
        if j is None:
            print("backtrace: No input with value X found.")
            return (None, None)

        # v XOR i
        if gate.inv == 1:
            v = '1' if v == '0' else '0'
            print(f"backtrace: Inverted value to {v} due to gate inversion.")

        k = j
   
    print(f"backtrace: Reached PI {k} with value {v}.")
    return (k, v)

def imply(line, value):
    print(f"imply: line {line} called with value {value}")
    # Perform 5-value simulation to set line to value
    globals.wire_values[line] = value
    print(f"imply: line {line} set to {value}")

    changed = True
    while changed:
        changed = False
        for gate in globals.gates:
            old_value = globals.wire_values.get(gate.output, 'X')
            new_value = evaluate_gate(gate)
            print(f"imply: gate: {gate.name} old_value = {old_value} new value = {new_value}")
            if new_value != old_value:
                globals.wire_values[gate.output] = new_value
                print(f"imply: set {gate.output} to {new_value}")
                changed = True