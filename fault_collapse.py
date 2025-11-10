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

    # NOT GATE
    # inputs are functionally equivalent to the output inverted
    # remove all input s-a-faults and keep output s-a-faults
    if Gate.gate_type == "not":
        collapsed_faults.add(f"{Gate.output}: s-a-0")
        collapsed_faults.add(f"{Gate.output}: s-a-1")
        return collapsed_faults

    # FAULT EQUIVALENCE
    # input s-a-(c) equivalent to output s-a-(c XOR i)
    # remove both input s-a-(c)s and keep output s-a-(c XOR i)

    # FAULT DOMINANCE
    # output s-a-(c XNOR i) dominates input s-a-(c')s
    # remove output s-a-(c XNOR i) and keep both input s-a-(c')s

    # after removing output s-a-(c XNOR i) and both input s-a-(c)s, we have:
    # input s-a-(c')s
    # output s-a-(c XOR i)

    for inp in Gate.inputs:
        if inp in globals.primary_inputs:
            collapsed_faults.add(f"{inp}: s-a-{Gate.c ^ 1}")
    collapsed_faults.add(f"{Gate.output}: s-a-{Gate.c ^ Gate.inv}")
    return collapsed_faults
