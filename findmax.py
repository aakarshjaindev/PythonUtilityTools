def find_max(numbers):
    """
    Finds the maximum value in a list of integers.
    
    Args:
        numbers (list): A list of integers.
    
    Returns:
        int: The maximum value in the list.
    """
    if not numbers:
        return None
    
    max_value = numbers [0]
    for num in numbers:
        if num > max_value:
            max_value = num
    
    return max_value


numbers = [5, 2, 8, 1, 9, 3]
print(find_max(numbers))  # Output: 9
