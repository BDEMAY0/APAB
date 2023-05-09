import zipfile
import pyminizip
import random
import string

# Définir les caractères autorisés
caracteres = string.ascii_letters + string.digits

# Générer une chaîne aléatoire de 20 caractères
mot_de_passe = ''.join(random.choice(caracteres) for i in range(20))

inpt = "rapport_audit_pentest.pdf"
pre = None
oupt = "rapport_audit_pentest.zip"
com_lvl = 5

# compressing file
pyminizip.compress(inpt, None, oupt,mot_de_passe, com_lvl)

print(mot_de_passe)



