import zipfile
import pyminizip
import random
import string
import os

def f_zip_encrypt(name_file):
# Définir les caractères autorisés
    caracteres = string.ascii_letters + string.digits

# Générer une chaîne aléatoire de 20 caractères
    mot_de_passe = ''.join(random.choice(caracteres) for i in range(20))


    current_dir = os.path.dirname(os.path.abspath(__file__))

    inpt = f'{current_dir}/rapport/{name_file}'
    pre = None
    oupt = f'{current_dir}/ressources/mail/{name_file}.zip'
    com_lvl = 5

# compressing file
    pyminizip.compress(inpt, None, oupt,mot_de_passe, com_lvl)

    return mot_de_passe    



