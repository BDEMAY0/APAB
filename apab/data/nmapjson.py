import subprocess
import xmltodict
import json
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(current_dir, "ressources", "parametres", "options.txt")
path_options = os.path.expanduser(folder)
with open(path_options, "r") as f:
    for line in f:
        key, value = line.strip().split(" :")
        if key == "ip":
            ip = value.replace(" ", "")
        elif key == "masque_sous_reseau":
            masque_sous_reseau = value.replace(" ", "")
        elif key == "ip_ex":
            ip_ex = value.replace(" ", "")


current_dir = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(current_dir, "ressources", "nmap", "test.xml")
path_xml = os.path.expanduser(folder)
if ip_ex != "":
    commande = f'nmap -sV --exclude {ip_ex} -oX {path_xml} {ip}/{masque_sous_reseau}'
else:
    commande = f'nmap -sV -oX {path_xml} {ip}/{masque_sous_reseau}'

resultat = subprocess.run(commande, shell=True, stdout=subprocess.PIPE)

with open(path_xml) as xml_file:
    dict_from_xml = xmltodict.parse(xml_file.read())

json_output = json.dumps(dict_from_xml, indent=4)

current_dir = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(current_dir, "ressources", "nmap", "output.json")
path_output = os.path.expanduser(folder)
with open(path_output, 'w') as json_file:
    json_file.write(json_output)

subprocess.run(f'rm {path_xml}', shell=True)
subprocess.run(['python', 'main.py'])