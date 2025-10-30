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

    primary_inputs = []
    primary_outputs = []
    gates = []

    # read and strip lines
    with open(filepath, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('$'):
                continue
        
            tokens = line.split()

            # primary inputs
            if "$... primary input" in line or "$ ... primary input" in line:
                wire_name = tokens[0]
                primary_inputs.append(wire_name)

            # primary outputs
            elif "$... primary output" in line or "$ ... primary output" in line:
                wire_name = tokens[0]
                primary_outputs.append(wire_name)
            
            # gates
            else:
                if len(tokens) == 4:
                    output, gate_type, input1, input2 = tokens
                    gates.append({
                        "output": output,
                        "gate_type": gate_type.lower(),
                        "inputs": [input1, input2]
                    })
                elif len(tokens) == 3:
                    output, gate_type, input1 = tokens
                    gates.append({
                        "output": output,
                        "gate_type": gate_type.lower(),
                        "inputs": [input1]
                    })
                else:
                    print(f"Warning: Unrecognized line format: '{line}'")

    # display for testing
    print(f"Primary Inputs: {primary_inputs}")
    print(f"Primary Outputs: {primary_outputs}")
    print("Gates:")
    for gate in gates:
        print(f"  {gate['output']} {gate['gate_type']} {gate['inputs']}")
    
    return primary_inputs, primary_outputs, gates

# test runner
if __name__ == "__main__":
    # Example usage
    filepath = input("Enter the path to the net-list file: ").strip()
    read_netlist(filepath)