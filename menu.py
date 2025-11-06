from netlist_parser import read_netlist
from fault_collapse import collapse_faults

def display_menu():
    print("""
    [0] Read the input net-list
    [1] Perform fault collapsing
    [2] List fault classes
    [3] Simulate
    [4] Generate tests (D-Algorithm)
    [5] Exit
          """)
    return input("Select an option: ")

def handle_selection(selection):
    if selection == '0':
        read_netlist(filepath = input("Enter the path to the net-list file: ").strip())
    elif selection == '1':
        collapse_faults()
    elif selection == '2':
        print("You chose '2'\n")
        #list_fault_classes()
    elif selection == '3':
        print("You chose '3'\n")
        #simulate()
    elif selection == '4':
        print("You chose '4'\n")
        #generate_tests()
    elif selection == '5':
        print("You chose '5'\n")
        print("Exiting program.")
        #exit_program()
    else:
        print("Invalid selection. Please try again.")
    return True