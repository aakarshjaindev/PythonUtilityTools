def tip_calculator():
    """
    Calculates the tip and total amount for a bill based on user input.

    Prompts the user to enter the bill amount and the desired tip percentage.
    Then, it calculates the tip amount and the total bill (bill + tip).
    Finally, it prints the calculated tip amount and total amount, formatted to two decimal places.
    """
    try:
        # Get bill amount from user
        bill_amount = float(input("Enter the bill amount: "))
        if bill_amount < 0:
            print("Bill amount cannot be negative.")
            return

        # Get tip percentage from user
        tip_percentage = float(input("Enter the tip percentage (e.g., 15, 20, 25): "))
        if tip_percentage < 0:
            print("Tip percentage cannot be negative.")
            return

    except ValueError:
        print("Invalid input. Please enter numeric values for bill amount and tip percentage.")
        return

    # Calculate tip amount
    tip_amount = bill_amount * (tip_percentage / 100)
    
    # Calculate total amount
    total_amount = bill_amount + tip_amount

    # Display the results
    print(f"Tip amount: ${tip_amount:.2f}")
    print(f"Total amount: ${total_amount:.2f}")

if __name__ == "__main__":
    tip_calculator()

# Note: This script assumes valid numeric input and does not handle currency formatting beyond two decimal places.