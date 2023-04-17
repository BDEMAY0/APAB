from Package_Manage.Parser import NmapParser
import os

# Le point d'entrée du programme
if __name__ == "__main__":

    # Chemin du répertoire courant
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Chemin absolu pour le fichier output.json
    nmap_output_file = os.path.join(current_dir, "ressources", "nmap", "output.json")

    # Création d'un objet NmapParser et chargement du fichier JSON
    parser = NmapParser(nmap_output_file)

    #Récupère les attaques cochés de l'application
    with open("data/ressources/parametres/pentest.txt", "r") as f:
        for line in f:
            key, value = line.strip().split(" :")
            if value == " True":
                globals()[key](parser)

