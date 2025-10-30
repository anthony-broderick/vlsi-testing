from menu import disply_menu, handle_selection

def main():
    while True:
        selection = display_menu()
        if selection == '5':
            handle_selection(selection)
            break
        handle_selection(selection)

if __name__ == "__main__":
    main()