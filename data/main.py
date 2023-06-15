from Package_Manage.NmapParser import NmapParser
import os
from Package_Manage.launcher import * 
from Package_Export.ManageExport import ManageExport
from Package_Rapport.rapport import main_rapport

# Le point d'entrée du programme
def main():

    # Chemin du répertoire courant
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Chemin absolu pour le fichier output.json
    nmap_output_file = os.path.join(current_dir, "ressources", "nmap", "output.json")
    parameter_file = os.path.join(current_dir, "ressources", "parametres", "pentest.txt")

    # Création d'un objet NmapParser et chargement du fichier JSON
    parser = NmapParser(nmap_output_file)

    #Appel de fonction d'audit qui est considérer par défaut et comme cela n'est pas dans le fichier texte
    #Cela va traiter le Netbios et les bannières des services et les ports tel que http
    audit(parser)
    # Récupère les attaques cochées de l'application
    with open(parameter_file, "r+") as f:
        lignes = f.readlines()
        for i, ligne in enumerate(lignes):
            key, value = ligne.strip().split(" :")
            if value == " True":
                if isinstance(key, str) and key in globals():
                    globals()[key](parser)
            if key == "En cours":
                lignes[i] = "En cours : finis       "
                break
               
        f.seek(0)
        f.writelines(lignes)
        ManageExport.export_all_to_json("rapport_attaques.json")
        main_rapport()


if __name__ == "__main__":
    main()
