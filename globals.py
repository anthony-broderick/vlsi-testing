# given core data
primary_inputs = []
primary_outputs = []
gates = []

class Gate:
    def __init__(self, name: str, output: str, gate_type: str, inputs: list, c: int = 0, inv: int = 0, PI: bool = False):
        self.name = name
        self.output = output
        self.gate_type = gate_type
        self.inputs = inputs
        self.PI = False
        
        for inp in self.inputs:
            if inp in primary_inputs:
                self.PI = True

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

# wire values

# faults

# reset for new netlist
def reset_globals():
    global primary_inputs, primary_outputs, gates
    primary_inputs.clear()
    primary_outputs.clear()
    gates.clear()
