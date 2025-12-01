# given core data
primary_inputs = []
primary_outputs = []
gates = []
wire_values = {}
input_wires = []
duplicate_wires = {}
fault_list = set ()

class Gate:
    def __init__(self, name: str, output: list, gate_type: str, inputs: list, c: int = 0, inv: int = 0, PI: bool = False):
        self.name = name
        self.output = output
        self.gate_type = gate_type
        self.inputs = inputs
        self.PI = False
        
        for out in self.output:
            wire_values[out] = 'X'  # initialize output wire value
        for inp in self.inputs:
            wire_values[inp] = 'X' # initialize input wire value
            if inp in input_wires:
                if inp not in duplicate_wires:
                    duplicate_wires[inp] = 2 # first duplicate means there are at least 2 branches to be considered fanout
                else:
                    duplicate_wires[inp] += 1
            input_wires.append(inp)

            # add input s-a-faults
            fault_list.add(f"{inp}: s-a-0")
            fault_list.add(f"{inp}: s-a-1")
            if inp in primary_inputs:
                self.PI = True

        # add output s-a-faults
        fault_list.add(f"{self.output}: s-a-0")
        fault_list.add(f"{self.output}: s-a-1")

        # set controlling and inverting values
        if gate_type == "nand" or gate_type == "not":
            self.c = 0
            self.inv = 1
        elif gate_type == "nor":
            self.c = 1
            self.inv = 1
        elif gate_type == "or":
            self.c = 1
            self.inv = 0
        else:
            self.c = c
            self.inv = inv

# faults

# reset for new netlist
def reset_globals():
    global primary_inputs, primary_outputs, gates
    primary_inputs.clear()
    primary_outputs.clear()
    wire_values.clear()
    fault_list.clear()
    gates.clear()
    input_wires.clear()
    duplicate_wires.clear()
