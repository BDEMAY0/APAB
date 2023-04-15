import subprocess
import xmltodict
import json
import time

with open("data/options.txt", "r") as f:
    for line in f:
        key, value = line.strip().split(" :")
        if key == "ip":
            ip = value.replace(" ", "")
        elif key == "masque_sous_reseau":
            masque_sous_reseau = value.replace(" ", "")

commande = f'nmap -sV -oX data/test.xml {ip}/{masque_sous_reseau}'
resultat = subprocess.run(commande, shell=True, stdout=subprocess.PIPE)

with open('data/test.xml') as xml_file:
    dict_from_xml = xmltodict.parse(xml_file.read())

json_output = json.dumps(dict_from_xml, indent=4)

with open('data/output.json', 'w') as json_file:
    json_file.write(json_output)

subprocess.run("rm data/test.xml", shell=True)
subprocess.run(['python', 'data/main.py'])