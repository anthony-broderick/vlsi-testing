from netlist_parser import read_netlist
from fault_collapse import collapse_faults
from podem import podem, print_test_vector, get_test_vector
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
        fault_line = input("Fault_line: ")
        fault_value = input("Fault_value: ")
        result = podem(fault_line, fault_value)
        if result == "SUCCESS":
            print("Test generated successfully.")
            tv = get_test_vector()
            print_test_vector(tv)
            #get_test_vector()
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