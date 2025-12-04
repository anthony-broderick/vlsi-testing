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

def simulate():
	"""Collect PI values and faults from the user, run a simulation
	across the whole circuit and print resulting wire values.
	"""
	# ensure there is something to simulate
	if not globals.gates:
		print("No gates loaded in globals.gates. Parse a netlist first.")
		return

	# collect primary input values
	print("Primary inputs:")
	for pi in globals.primary_inputs:
		while True:
			val = input(f"  Enter value for {pi} (0/1/X): ").strip().upper()
			if val in ('0', '1', 'X'):
				globals.wire_values[pi] = val
				break
			print("    Invalid value — enter 0, 1, or X.")

	# collect faults to inject
	# show all known wires so user can pick fault targets
	print("\nAvailable wires in circuit (can inject faults on any):")
	wires = sorted(globals.wire_values.keys())
	if wires:
		print("  " + ", ".join(wires))
	else:
		print("  (no wires detected)")

	raw_faults = input("\nEnter faults to inject (comma-separated, e.g. 'a: s-a-0, b: s-a-0'), or leave blank: ").strip()
	applied_fault_lines = set()
	if raw_faults:
		parts = [p.strip() for p in raw_faults.split(',') if p.strip()]
		for p in parts:
			# accept formats like "wire: s-a-0" or "wire s-a-0" or "wire:s-a-0"
			token = p.replace(':', ' ').split()
			if len(token) >= 2:
				line = token[0]
				sa = token[1]
				if sa.endswith('0'):
					# represent s-a-0 as D (good=1, faulty=0)
					if line in globals.wire_values:
						globals.wire_values[line] = 'D'
						applied_fault_lines.add(line)
					else:
						print(f"Warning: fault line {line} not found in circuit.")
				elif sa.endswith('1'):
					# represent s-a-1 as D' (good=0, faulty=1)
					if line in globals.wire_values:
						globals.wire_values[line] = "D'"
						applied_fault_lines.add(line)
					else:
						print(f"Warning: fault line {line} not found in circuit.")
				else:
					print(f"Warning: couldn't parse stuck value in '{p}'.")
			else:
				print(f"Warning: couldn't parse fault '{p}'.")

	# iterative simulation
	changed = True
	iteration = 0
	while changed:
		changed = False
		iteration += 1
		for gate in globals.gates:
			# gate.output may be a list (fanout) or a single value; normalize to list
			outputs = gate.output if isinstance(gate.output, list) else [gate.output]
			# evaluate gate once; only update outputs that do not have injected faults
			new = evaluate_gate(gate)
			# assign new value to each output wire and mark changed if any updated
			for out in outputs:
				# don't overwrite wires with explicitly injected faults
				if out in applied_fault_lines:
					continue
				old = globals.wire_values.get(out, 'X')
				if new != old:
					globals.wire_values[out] = new
					changed = True

	# print summary of wire values
	print('\nSimulation complete. Wire values:')
	for wire in sorted(globals.wire_values.keys()):
		print(f"  {wire}: {globals.wire_values[wire]}")

	print('\nPrimary outputs:')
	for po in globals.primary_outputs:
		print(f"  {po}: {globals.wire_values.get(po, 'X')}")


if __name__ == '__main__':
	simulate()

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