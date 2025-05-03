def tip_calculator():
    bill_amount = float(input("Enter the bill amount: "))
    tip_percentage = float(input("Enter the tip percentage (e.g., 15, 20, 25): "))

    tip_amount = bill_amount * (tip_percentage / 100)
    total_amount = bill_amount + tip_amount

    print(f"Tip amount: ${tip_amount:.2f}")
    print(f"Total amount: ${total_amount:.2f}")

tip_calculator()