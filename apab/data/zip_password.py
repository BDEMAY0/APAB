import zipfile
import pyminizip
import random
import string
import os

def f_zip_encrypt(name_file, password):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    inpt = f'{current_dir}/rapport/{name_file}'
    pre = None
    oupt = f'{current_dir}/ressources/mail/{name_file}.zip'
    com_lvl = 5

# compressing file
    pyminizip.compress(inpt, None, oupt,password, com_lvl) 



