import random
def guess(x):
  random_number = random.randint(1,x)
  guess = 0 # starting  the number eist 
  while guess != random_number:
    guess = int(input(f'Gues a random number1 and {x}))
    if guess < random_number:
      print('sorry , guess agian. too low.')
    elif guess > random_number:
      print("sorry, guess again. Too high ')
  print(f'yay, congrat. you have guess the number{ random_number) 
    correctly !!' )


computer_guess(x):
low = 1 
hight = x 
feedback = ' ' 
while feedback != 