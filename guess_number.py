import random
def guess(x): 
    random_number  = random.randint(1, x)
    guess = 0 
    while guess!= random_number:
        guess = int(input(f'guess a number between 1 and {x}:'))
        if guess < random_number:
            print(' sorry , guess agin  too lwo,')      
        elif guess > random_number:
            print( 'guess again too hight  ')
    print(' you guessed it right ')
guess(11)
