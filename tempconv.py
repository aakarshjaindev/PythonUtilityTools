'''
def temperature_converter():
    print("Temperature Converter")
    print("1. Celsius to Fahrenheit")
    print("2. Fahrenheit to Celsius")
    print("3. Celsius to Kelvin")
    print("4. Kelvin to Celsius")

    choice = int(input("Enter your choice (1-4): "))

    if choice == 1:
        celsius = float(input("Enter the temperature in Celsius: "))
        fahrenheit = (celsius * 9/5) + 32
        print(f"{celsius}°C is equal to {fahrenheit}°F")
    # Add the other conversion options
    else:
        print("Invalid choice. Please try again.")

temperature_converter()


'''


print( ' welcome the temperature converter program. Let me help you with converting the temperature you need')

temp = int(input(" what is the conversion you are expecting from? 1- F to C, 2- C to F"))

value = int(input(' what is the temperature values'))


if temp == '1': 
    value = (value - 32) * 9/5
print(f'your converted temperature is {value}') 
    

