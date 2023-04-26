import zipfile
import pyminizip
import random
import string

# Définir les caractères autorisés
caracteres = string.ascii_letters + string.digits

# Générer une chaîne aléatoire de 20 caractères
mot_de_passe = ''.join(random.choice(caracteres) for i in range(20))

# Ouvrir un fichier en mode écriture
with open('password.txt', mode='w') as fichier:
    # Écrire du contenu dans le fichier
    fichier.write(mot_de_passe)


inpt = "rapport_audit_pentest.pdf"
pre = None
oupt = "output.zip"
com_lvl = 5

# compressing file
pyminizip.compress(inpt, None, oupt,
                   mot_de_passe, com_lvl)





