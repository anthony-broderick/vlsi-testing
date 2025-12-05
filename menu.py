from netlist_parser import read_netlist
from fault_collapse import collapse_faults
from podem import PODEM
from simulate import simulate
import globals

def display_menu():
    print("""
    [0] Read the input net-list
    [1] Perform fault collapsing
    [2] List fault classes
    [3] Simulate
    [4] Generate tests (PODEM)
    [5] Exit
          """)
    return input("Select an option: ")

def handle_selection(selection):
    if selection == '0':
        read_netlist(filepath = input("Enter the path to the net-list file: ").strip())
    elif selection == '1':
        collapse_faults()
    elif selection == '2':
        print("Fault List:")
        for fault in sorted(globals.fault_list):
            print(f"{fault}")
    elif selection == '3':
        print("You chose '3'\n")
        simulate()
    elif selection == '4':
        globals.reset_wire_values()
        target_line = input("Fault_line: ")
        fault_value = input("Fault_value: ")
        if target_line not in globals.wire_values:
            print(f"Error: Wire '{target_line}' not found in the circuit.")
            return
        elif fault_value not in ['0', '1']:
            print("Error: Fault value must be '0' or '1'.")
            return
        else:
            globals.target_line = target_line
            globals.fault_value = fault_value

        result = PODEM()
        if result == "SUCCESS":
            print("Test generated successfully.")
            print(f"All wire values: {globals.wire_values}")
            for pi in globals.primary_inputs:
                if globals.wire_values[pi] == 'D':
                    globals.wire_values[pi] = '1'
                elif globals.wire_values[pi] == "D'":
                    globals.wire_values[pi] = '0'
                print(f"{pi}: {globals.wire_values[pi]}")
        else:
            print("Failed to generate test.")
            
        #generate_tests()
    elif selection == '5':
        print("You chose '5'\n")
        print("Exiting program.")
        #exit_program()
    else:
        print("Invalid selection. Please try again.")
    return True