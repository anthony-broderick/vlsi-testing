import os

def read_netlist(filepath: str):
    # validate file
    # not yet implemented
    if not os.path.isfile(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        return None
    if not filepath.endswith('.ckt'):
        print(f"Error: Invalid file type. Must be a .ckt file.")
        return None

    # read and strip lines
    with open(filepath, "r") as file:
        lines = [line.strip() for line in file if line.strip()]

    primary_inputs = []
    primary_outputs = []
    gates = []

    # skip leading $ lines
    while lines and lines[0].startswith('$'):
        lines.pop(0)

    # primary inputs
    while lines and not lines[0].startswith('$'):
        pi = lines.pop(0).split("$")[0].strip() # ignore comments
        primary_inputs.append(pi)

    # skip two lines between PIs and POs
    for _ in range(2):
        if lines and lines[0].startswith('$'):
            lines.pop(0)
        
    # primary outputs
    while lines and not lines[0].startswith('$'):
        po = lines.pop(0).split("$")[0].strip() # ignore comments
        primary_outputs.append(po)

    # skip four lines between POs and gates
    for _ in range(4):
        if lines and lines[0].startswith('$'):
            lines.pop(0)
    
    # gates
    while lines and not lines[0].startswith('$'):
        parts = lines.pop(0).split()
        if len(parts) == 4:
            output, gate_type, input1, input2 = parts
            gates.append({
                "output": output,
                "gate_type": gate_type.lower(),
                "inputs": [input1, input2]
            })
    
    # display for testing
    print(f"Primary Inputs: {primary_inputs}")
    print(f"Primary Outputs: {primary_outputs}")
    print("Gates:")
    for gate in gates:
        print(f"  {gate['output']} = {gate['gate_type'].upper()}({', '.join(gate['inputs'])})")
    
    return primary_inputs, primary_outputs, gates

# test runner
if __name__ == "__main__":
    # Example usage
    filepath = input("Enter the path to the net-list file: ").strip()
    read_netlist(filepath)