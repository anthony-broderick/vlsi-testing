import globals

def collapse_faults():
    collapsed_set = set()
    for gate in globals.gates:
        if gate.PI == False:
            continue
        collapsed_set |= collapse_faults_at_gate(gate)
    print("Collapsed Faults:")
    for fault in sorted(collapsed_set):
        print(f" {fault}")

def collapse_faults_at_gate(Gate):
    collapsed_faults = set() # use a set to avoid duplicates
    
    if Gate.gate_type == "nand":
        # input s-a-0's equivalent to output s-a-1
        # output s-a-0 dominates inputs s-a-1, remove output s-a-0
        for inp in Gate.inputs:
            collapsed_faults.add(f"{inp}: s-a-1")
        collapsed_faults.add(f"{Gate.output}: s-a-1")
    elif Gate.gate_type == "nor":
        # input s-a-1's equivalent to output s-a-0
        # output s-a-1 dominates inputs s-a-0, remove output s-a-1
        for inp in Gate.inputs:
            collapsed_faults.add(f"{inp}: s-a-0")
        collapsed_faults.add(f"{Gate.output}: s-a-0")
    elif Gate.gate_type == "and":
        # input s-a-0's equivalent to output s-a-0
        # output s-a-1 dominates inputs s-a-1, remove output s-a-1
        for inp in Gate.inputs:
            collapsed_faults.add(f"{inp}: s-a-1")
        collapsed_faults.add(f"{Gate.output}: s-a-0")
    else:   # or gate
        # input s-a-1's equivalent to output s-a-1
        # output s-a-0 dominates inputs s-a-0, remove output s-a-0
        for inp in Gate.inputs:
            collapsed_faults.add(f"{inp}: s-a-0")
        collapsed_faults.add(f"{Gate.output}: s-a-1")
    return collapsed_faults
