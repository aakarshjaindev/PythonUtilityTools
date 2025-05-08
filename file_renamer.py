import os 
from datetime import datetime 


def rename_fils(directory, prefix = ' ', suffix =  ''):
    for filename in os.listdir(directory):
        file_path = os.listdir(directory, filename )
        if os.path.isfile(file_path):
            new_filename  = f'{prefix}, {os.path.splitext(filename)[0], {suffix}{os.path.splitext(filename)_}'
            new_file_path = os.path.join(directory , new_filename) 
            os.rename ( file_path ,  new_file_path)
            print(f'Renmaed {filename} to {new_filename}')



# example usage 
rename_files = ("/path/to/directory", prefix = 'file ' , suffix = ' _updated ')