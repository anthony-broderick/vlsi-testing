import globals

# main functions: PODEM, Objective, Backtrace, Imply
# all functions above # line will be abstracted to other files

def inject_fault(fault_line, fault_value):
    if fault_value == '0': 
        globals.wire_values[fault_line] = 'D'  # s-a-0 fault
    elif fault_value == '1':
        globals.wire_values[fault_line] = "D'"  # s-a-1 fault
    else:
        print("inject_fault: Invalid fault value.")
        return "FAILURE"
    return podem(fault_line, fault_value)

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
    
    if gate.c in [0, 1]:  
        c_str = str(gate.c)
        if c_str in input_values:
            result = c_str
        elif 'X' in input_values:
            result = 'X'
        else:
            # all non-controlling values
            result = '1' if gate.c == 0 else '0'
    else:
        result = 'X'  # unknown controlling value
    
    result = handle_d_values(gate, input_values, result)

    if gate.inv == 1:
        result = invert_value(result)

    return result  # unknown if gate type is unrecognized

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
    
def handle_d_values(gate, input_values, result):
    if 'D' in input_values or "D'" in input_values:
        # check if all other inputs are non-controlling
        c_str = str(gate.c) if gate.c in [0,1] else None

        d_count = input_values.count('D') + input_values.count("D'")

        if c_str and c_str in input_values:
            return result
        
        # propagate D or D'
        if d_count == 1:
            if 'D' in input_values:
                return 'D'
            else:
                return "D'"
    return result

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

    if not test_possible():
        return "FAILURE"
    
    # get objective
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
    # activate fault for unknown values
    if globals.wire_values[fault_line] == 'X':
        # complement s-a-value to activate fault
        target_value = '1' if fault_value == '0' else '0'
        return (fault_line, target_value)
    
    # find gate in D-frontier to propagate fault
    d_frontier = get_d_frontier()

    if not d_frontier:
        return (None, None)
    
    gate = d_frontier[0]  # select first gate in D-frontier
    
    for inp in gate.inputs:
        if globals.wire_values[inp] == 'X':
            c_complement = gate.c ^ 1 # controlling value complement
            str(c_complement)
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