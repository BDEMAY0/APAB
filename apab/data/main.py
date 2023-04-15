from Package_Manage.Parser import NmapParser

# Le point d'entrée du programme
if __name__ == "__main__":

    # Nom du fichier JSON contenant les résultats de Nmap
    nmap_output_file = "ressources/nmap/output2.json"

    # Création d'un objet NmapParser et chargement du fichier JSON
    parser = NmapParser(nmap_output_file)

    #Récupère les attaques cochés de l'application
    with open("data/pentest.txt", "r") as f:
        for line in f:
            key, value = line.strip().split(" :")
            if value == " True":
                globals()[key](parser)

