import globals
import copy

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


def find_gate_by_output(line):
    for gate in globals.gates:
        if line in gate.output:
            return gate
    return None


def evaluate_gate(gate):
    # Returns new 5-valued logic for gate.output[0] based on gate.inputs
    in_vals = [globals.wire_values.get(i, X) for i in gate.inputs]

    # NOT gate
    if gate.gate_type == 'not':
        vin = in_vals[0]
        if vin in (ZERO, ONE):
            return ONE if vin == ZERO else ZERO
        if vin == D:
            return DB if gate.inv == 0 else invert_value(DB)
        if vin == DB:
            return D if gate.inv == 0 else invert_value(D)
        return X

    # For multi-input gates (AND/OR-like with control value gate.c)
    control = str(gate.c)
    non_control = '1' if gate.c == 0 else '0'

    # If any input equals control -> output is control
    if control in in_vals:
        out = control
    else:
        # no control value present
        if X in in_vals:
            out = X
        else:
            out = non_control

    # Handle D / D' propagation
    has_d = D in in_vals
    has_db = DB in in_vals
    if has_d or has_db:
        if control in in_vals:
            out = control
        else:
            if has_d and not has_db:
                out = D
            elif has_db and not has_d:
                out = DB
            else:
                out = X

    # Account for gate inversion
    if getattr(gate, 'inv', 0) == 1:
        out = invert_value(out)

    return out


def error_at_PO():
    # True if any primary output has D or D'
    for po in globals.primary_outputs:
        val = globals.wire_values.get(po, X)
        if val == D or val == DB:
            return True
    return False


def get_d_frontier():
    df = []
    for gate in globals.gates:
        out_val = globals.wire_values.get(gate.output[0], X)
        if out_val == X:
            in_vals = [globals.wire_values.get(i, X) for i in gate.inputs]
            if D in in_vals or DB in in_vals:
                df.append(gate)
    return df


def objective(fault_line, fault_value):
    # Step 1: If fault site is still X, activate it (return concrete value)
    fault_current = globals.wire_values.get(fault_line, X)
    if fault_current == X:
        # Activate the fault: to detect s-a-v, set opposite value
        if fault_value == '0':
            return (fault_line, ONE)  # set to 1 to detect s-a-0
        else:
            return (fault_line, ZERO)  # set to 0 to detect s-a-1
    
    # Step 2: If D-frontier is non-empty, pick a gate and propagate
    df = get_d_frontier()
    if not df:
        return (None, None)
    
    # Select first gate in D-frontier
    gate = df[0]
    
    # Find an input with X and set to non-controlling value (concrete value)
    for inp in gate.inputs:
        if globals.wire_values.get(inp, X) == X:
            c_comp = ONE if gate.c == 0 else ZERO
            return (inp, c_comp)
    
    return (None, None)


def backtrace(line, desired_val):
    # Backtrace from line toward a primary input
    v = desired_val
    current = line

    while current not in globals.primary_inputs:
        gate = find_gate_by_output(current)
        if gate is None:
            return (None, None)

        # Find an input with X value
        j = None
        for inp in gate.inputs:
            if globals.wire_values.get(inp, X) == X:
                j = inp
                break
        
        if j is None:
            return (None, None)

        # If gate has inversion, flip the required value
        if getattr(gate, 'inv', 0) == 1:
            v = invert_value(v)

        current = j

    return (current, v)


def imply(pi, value):
    # Assign primary input and perform iterative 5-value simulation
    globals.wire_values[pi] = value

    changed = True
    while changed:
        changed = False
        for gate in globals.gates:
            old = globals.wire_values.get(gate.output[0], X)
            new = evaluate_gate(gate)
            if new != old:
                globals.wire_values[gate.output[0]] = new
                changed = True


def get_test_vector():
    """
    For any PI left as X, try assigning 0 or 1 while preserving the
    detection (D/D' reaching a primary output). The algorithm builds
    assignments cumulatively so the final vector contains only 0/1/X
    """
    # base_state is the circuit state after successful PODEM (contains D propagation)
    base_state = copy.deepcopy(globals.wire_values)
    assignments = {}

    for pi in globals.primary_inputs:
        cur = base_state.get(pi, X)
        if cur in (ZERO, ONE):
            assignments[pi] = cur
            continue
        if cur == D:
            # D at PI => good value is 1
            assignments[pi] = ONE
            # apply for next PI
            base_state[pi] = ONE
            # propagate this assignment into base_state
            globals.wire_values.clear()
            globals.wire_values.update(base_state)
            imply(pi, ONE)
            base_state = copy.deepcopy(globals.wire_values)
            continue
        if cur == DB:
            assignments[pi] = ZERO
            base_state[pi] = ZERO
            globals.wire_values.clear()
            globals.wire_values.update(base_state)
            imply(pi, ZERO)
            base_state = copy.deepcopy(globals.wire_values)
            continue

        # cur is X: try 0 then 1, keep the value that preserves detection
        chosen = None

        for cand in (ZERO, ONE):
            # start from base_state and apply previous assignments
            trial_state = copy.deepcopy(base_state)
            for a_pi, a_val in assignments.items():
                trial_state[a_pi] = a_val
            trial_state[pi] = cand

            # load trial_state into globals and propagate
            globals.wire_values.clear()
            globals.wire_values.update(trial_state)
            imply(pi, cand)

            if error_at_PO():
                chosen = cand
                break

        if chosen is None:
            # neither value preserved detection — pick ZERO by default
            chosen = ZERO

        # accept chosen and update base_state for next PI
        assignments[pi] = chosen
        base_state[pi] = chosen
        globals.wire_values.clear()
        globals.wire_values.update(base_state)
        imply(pi, chosen)
        base_state = copy.deepcopy(globals.wire_values)

    return assignments


def print_test_vector(tv):
    for pi in sorted(tv.keys()):
        print(f"{pi}: {tv[pi]}")


def podem(fault_line, fault_value):
    """Main PODEM algorithm entry point

    Accepts fault_value as '0' or '1' (stuck-at) or as activation 'D' / "D'".
    If 'D' or "D'" is provided, the fault is considered already activated and
    we pre-inject the D/D' value at the fault site before running recursion.
    Internally the recursive routine expects a stuck-at value ('0' or '1').
    """
    # normalize input: accept D/DB (case-insensitive) as already-activated forms
    fv = fault_value.strip() if isinstance(fault_value, str) else fault_value
    fv_up = fv.upper() if isinstance(fv, str) else fv

    activated = False
    if fv_up == D:
        stuck_at = '0'
        activated = True
    elif fv_up == DB:
        stuck_at = '1'
        activated = True
    else:
        stuck_at = fv

    # Initialize all wires to X
    for wire in globals.wire_values:
        globals.wire_values[wire] = X

    # If user passed an activated form (D or D'), inject it now and propagate
    if activated:
        globals.wire_values[fault_line] = D if stuck_at == '0' else DB
        changed = True
        while changed:
            changed = False
            for gate in globals.gates:
                old = globals.wire_values.get(gate.output[0], X)
                new = evaluate_gate(gate)
                if new != old:
                    globals.wire_values[gate.output[0]] = new
                    changed = True

    # Run recursive PODEM using the normalized stuck-at value
    return podem_rec(fault_line, stuck_at, 0)


def podem_rec(fault_line, fault_value, depth):
    """Recursive PODEM with backtracking"""
    
    # Depth limit
    if depth > len(globals.primary_inputs) + 10:
        return 'FAILURE'
    
    # Inject fault into simulation (convert activation to D/D')
    fault_current = globals.wire_values.get(fault_line, X)
    if fault_current == ONE and fault_value == '0':
        # Injecting s-a-0 fault: mark as D (faulty would be 0, good is 1)
        globals.wire_values[fault_line] = D
        # Re-propagate with D
        changed = True
        while changed:
            changed = False
            for gate in globals.gates:
                old = globals.wire_values.get(gate.output[0], X)
                new = evaluate_gate(gate)
                if new != old:
                    globals.wire_values[gate.output[0]] = new
                    changed = True
    elif fault_current == ZERO and fault_value == '1':
        # Injecting s-a-1 fault: mark as D' (faulty would be 1, good is 0)
        globals.wire_values[fault_line] = DB
        # Re-propagate with D'
        changed = True
        while changed:
            changed = False
            for gate in globals.gates:
                old = globals.wire_values.get(gate.output[0], X)
                new = evaluate_gate(gate)
                if new != old:
                    globals.wire_values[gate.output[0]] = new
                    changed = True
    
    # Check if error propagated to PO
    if error_at_PO():
        return 'SUCCESS'
    
    # Check if D-frontier empty (meaning cannot proceed further)
    df = get_d_frontier()
    if not df and fault_current != X:  # if D-frontier empty and fault already activated, fail
        return 'FAILURE'
    
    # Get objective (line and value to set)
    k, vk = objective(fault_line, fault_value)
    if k is None:
        return 'FAILURE'
    
    # Backtrace to PI
    j, vj = backtrace(k, vk)
    if j is None:
        return 'FAILURE'
    
    # Save state before decision
    saved_state = copy.deepcopy(globals.wire_values)
    
    # Try assigning j to vj
    imply(j, vj)
    if podem_rec(fault_line, fault_value, depth + 1) == 'SUCCESS':
        return 'SUCCESS'
    
    # Restore state and try complement
    globals.wire_values.clear()
    globals.wire_values.update(saved_state)
    
    vj_comp = ONE if vj == ZERO else ZERO
    imply(j, vj_comp)
    if podem_rec(fault_line, fault_value, depth + 1) == 'SUCCESS':
        return 'SUCCESS'
    
    # Restore state
    globals.wire_values.clear()
    globals.wire_values.update(saved_state)
    
    return 'FAILURE'

