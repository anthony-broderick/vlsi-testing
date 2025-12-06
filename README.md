# vlsi-testing general description
Take a netlist describing a combinational circuit and perform fault collapsing, list fault classes, simulate the circuit, and generate tests using PODEM.

## How to run
Enter 'make run' in terminal and follow the prompts listed in the terminal. On run, the following interactive menu will be presented:

    [0] Read the input net-list
    [1] Perform fault collapsing
    [2] List fault classes
    [3] Simulate
    [4] Generate tests (PODEM)
    [5] Exit

Type the number in the brackets of the choice you would like and hit enter. You can only make one choice at a time.

## [0] Read the input net-list
Takes a file with the following formatting rules:

    -   '$' used for comments
    -   commented 'primary input' following primary input lines
    -   commented 'primary output' following primary output lines
    -   gate construction built in this format
        output   gate_type    input1 input2 ... inputN
    -   gate types can only be 'and' 'nand' 'nor' 'or'
    -   program automatically handles fanouts

It then parses this file and generates appropriate data structures for gates, wire values, and fault lists.

Please see the files in benchmarks/ to get a better idea of formatting if needed.

## [1] Perform fault collapsing
Reduces faults to primary input faults and fanouts of primary input faults through fault equivalence and fault dominance.

## [2] List fault classes
The found fault classes are displayed, one for each line. This will be s-a-0 and s-a-1 for all wires if run before running selection "[1] Perform fault collapsing."

## [3] Simulate
Takes an input test vector and a set of faults, and shows the single stuck at faults propagated to one of the outputs at the end of simulation. If no faults are provided, it will simulate the circuit with the provided test vector to show the output values.

## [4] Generate tests (PODEM)
Uses the PODEM test pattern generator to show the list of test vectors that will detect each fault (or list the fault as undetectable). It will print in the following format:

    Test Vector Format : (wires associated with each value in test vector)
    wire1 s-a-0: (test vector)
    wire1 s-a-1: (test vector)
    wire2 s-a-0: Undetectable fault
    wire2 s-a-1: (test vector)
    ...
    wireN s-a-0: (test vector)
    wireN s-a-1: (test vector)

## [5] Exit
Exits the program.

