import globals
from podem import evaluate_gate


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
			# skip overwriting any outputs that have an injected fault
			if any(out in applied_fault_lines for out in outputs):
				continue
			new = evaluate_gate(gate)
			# assign new value to each output wire and mark changed if any updated
			for out in outputs:
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

