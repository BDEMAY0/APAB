from Package_Manage.Parser import NmapParser
import os

# Le point d'entrée du programme
if __name__ == "__main__":

    # Chemin du répertoire courant
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Chemin absolu pour le fichier output.json
    nmap_output_file = os.path.join(current_dir, "ressources", "nmap", "output.json")
    parameter_file = os.path.join(current_dir, "ressources", "parametres", "pentest.txt")

    # Création d'un objet NmapParser et chargement du fichier JSON
    parser = NmapParser(nmap_output_file)

    # Récupère les attaques cochées de l'application
    with open(parameter_file, "r+") as f:
        lignes = f.readlines()
        for i, ligne in enumerate(lignes):
            print(ligne)
            key, value = ligne.strip().split(" :")
            if value == " True":
                if isinstance(key, str) and key in globals():
                    globals()[key](parser)
            if key == "En cours":
                lignes[i] = "En cours : finis       "
                break
        f.seek(0)
        f.writelines(lignes)


