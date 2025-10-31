import os
import globals

def read_netlist(filepath: str):
    # validate file
    # not yet implemented
    if not os.path.isfile(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        return None
    if not filepath.endswith('.ckt'):
        print(f"Error: Invalid file type. Must be a .ckt file.")
        return None
    
    # clear any previous netlist data
    globals.reset_globals()
    gate_number = 0

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
                globals.primary_inputs.append(wire_name)

            # primary outputs
            elif "$... primary output" in line or "$ ... primary output" in line:
                wire_name = tokens[0]
                globals.primary_outputs.append(wire_name)
            
            # gates
            else:
                if len(tokens) == 4:
                    output, gate_type, input1, input2 = tokens
                    name = f"G{gate_number}"
                    gate_obj = globals.Gate(name, output, gate_type.lower(), [input1, input2])
                    gate_number += 1
                    globals.gates.append(gate_obj)
                elif len(tokens) == 3:
                    output, gate_type, input1 = tokens
                    name = f"G{gate_number}"
                    gate_obj = globals.Gate(name, output, gate_type.lower(), [input1])
                    gate_number += 1
                    globals.gates.append(gate_obj)
                else:
                    print(f"Warning: Unrecognized line format: '{line}'")

    # display for testing
    print(f"Primary Inputs: {globals.primary_inputs}")
    print(f"Primary Outputs: {globals.primary_outputs}")
    print("Gates:")
    for gate in globals.gates:
        print(f"  {gate.name}: {gate.output} = {gate.gate_type}({', '.join(gate.inputs)})   c={gate.c}, inv={gate.inv}")

# test runner
if __name__ == "__main__":
    # Example usage
    filepath = input("Enter the path to the net-list file: ").strip()
    read_netlist(filepath)