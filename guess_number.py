import random

def guess(x):
    """
    Computer picks a number, user guesses.
    """
    random_number = random.randint(1, x)
    guess = 0
    print(f"\n--- User Guessing Game ---")
    print(f"I'm thinking of a number between 1 and {x}.")
    while guess != random_number:
        try:
            # Get user input
            guess_input = input(f'Guess a number between 1 and {x}: ')
            guess = int(guess_input) # Convert input to integer

            # Provide feedback
            if guess < random_number:
                print('Sorry, guess again. Too low.')
            elif guess > random_number:
                print("Sorry, guess again. Too high.")
            # No need for an else here, the loop condition handles the correct guess

        except ValueError:
            print("Invalid input. Please enter a number.") # Handle non-numeric input

    # Loop terminates when guess == random_number
    print(f'Yay, congrats! You have guessed the number {random_number} correctly!!')

def computer_guess(x):
    """
    User picks a number, computer guesses.
    """
    low = 1
    high = x
    feedback = ''
    print(f"\n--- Computer Guessing Game ---")
    print(f"Think of a number between 1 and {x}, and I'll try to guess it.")
    print("Tell me if my guess is too high (H), too low (L), or correct (C).")
    input("Press Enter when you have thought of a number...") # Give user time

    while feedback != 'c':
        if low > high: # Check for inconsistent feedback from the user
             print("Hmm, something went wrong. Your feedback might have been inconsistent.")
             return # Exit the function if the range becomes invalid
        elif low == high:
            guess = low  # Only one possibility left
            print(f"The number must be {guess}!") # Inform the user it must be this
        else:
            # Guess randomly within the current valid range
            guess = random.randint(low, high)
            # Alternative (more efficient) strategy: Binary Search
            # guess = (low + high) // 2

        # Get feedback from the user
        feedback = input(f'Is {guess} too high (H), too low (L), or correct (C)? ').lower()

        # Process feedback and adjust range
        if feedback == 'h':
            if guess == low: # Check if user says the lowest possible is too high
                print("Hmm, you said it was too high, but that was the lowest possible guess!")
                return
            high = guess - 1
        elif feedback == 'l':
            if guess == high: # Check if user says the highest possible is too low
                 print("Hmm, you said it was too low, but that was the highest possible guess!")
                 return
            low = guess + 1
        elif feedback == 'c':
            # Correct guess, loop will terminate
            pass
        else:
            print("Invalid feedback. Please enter H, L, or C.")

    # Loop terminates when feedback is 'c'
    print(f'Yay! The computer guessed your number, {guess}, correctly!')

# --- Example Usage ---
if __name__ == "__main__":
    # Example: User guesses a number between 1 and 10
    guess(10)

    print("\n============================\n")

    # Example: Computer guesses a number between 1 and 100
    computer_guess(100)
