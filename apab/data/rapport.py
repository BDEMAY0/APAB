# Importation des bibliothèques nécessaires
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, PageTemplate, BaseDocTemplate
from datetime import date
import json

# Configuration du fichier PDF
output_file = "rapport_audit_pentest.pdf"
doc = BaseDocTemplate(output_file, pagesize=letter)

# Styles de paragraphe
styles = getSampleStyleSheet()
header_style = styles['Heading1']
subheader_style = styles['Heading2']
normal_style = styles['Normal']


today = date.today()
auj = today.strftime("%d %B %Y")

# Page de couverture
titre_rapport = Paragraph("Rapport d'Audit et Pentest Automatisé\n APAB", header_style)
date_rapport = Paragraph(f'Date : {auj}', normal_style)
elements = [Spacer(1, 0.4 * 72),  Spacer(1, 0.7 * 72), date_rapport, PageBreak()]
im = Image('APAB.png', 8*inch, 6*inch)
elements.insert(1, im)

# Création d'un en-tête personnalisé
def header(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 10)
    # Ajout d'un encadrement coloré autour du texte
    canvas.setFillColorRGB(255, 0, 0) # Couleur de fond
    canvas.setStrokeColorRGB(0, 0, 0) # Couleur de bordure
    canvas.rect(415, 745, 175, 15, fill=1) # Rectangle autour du texte
    # Ajout du texte
    canvas.setFillColorRGB(255, 255, 255) # Couleur du texte
    canvas.drawString(450, 750, "C2 – Document confidentiel")
    # Ajout du numéro de page
    canvas.setFillColorRGB(0, 0, 0) # Couleur du texte
    canvas.drawString(475, 50, f"Page {doc.page}")
    canvas.restoreState()

# Ajout de l'en-tête personnalisé à chaque page
frame = Frame(doc.rightMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
doc.addPageTemplates([PageTemplate(id='custom_header', frames=frame, onPage=header)])


#Page Interlocuteur / Diffusion
my_Style=ParagraphStyle('My Para style',
fontName='Times-Roman',
backColor='#F1F1F1',
fontSize=11,
borderColor='#FFFF00',
borderWidth=2,
borderPadding=(20,20,20),
leading=15,
alignment=0
)
interlocuteur = Paragraph(f'<b>Interlocuteurs : </b><BR/>\
     Société APAB <BR/> \
	 <i>Auditeur.</i>\
', my_Style)

current_dir = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(current_dir, "ressources", "parametres", "options.txt")
path_options = os.path.expanduser(folder)
with open(path_options, "r") as f:
    for line in f:
        key, value = line.strip().split(" :")
        if key == "mail_entreprise":
            mail = value.replace(" ", "")
        elif key == "niveau_diffusion":
            niveau_diffusion = value.replace(" ", "")
	
	
diffusion = Paragraph(f'<b>Interlocuteurs : </b><BR/>\
     Société APAB . . . Contact : projetannuel.apab@gmail.com<BR/> \
	 <i>Auditeur</i><BR/><BR/>\
  <b>Diffusion : </b><BR/>\
     Niveau de classification	: {niveau_diffusion}<BR/><BR/> \
	 <b>Définition des niveaux de classification utilisés : </b><BR/>\
•	C0 – Public : les informations contenues dans ce document peuvent être diffusées sans aucune restriction <BR/> \
•	C1 – Accès limité : les informations contenues dans ce document ne peuvent être communiquées qu’à des personnels du MSI ou de ses partenaires. <BR/>\
•	C2 – Document confidentiel : les informations contenues dans ce document ne peuvent être communiquées qu’à des personnels du MSI ou des tiers explicitement nommés dans la liste de diffusion. <BR/>\
•	C3 – Document secret : les informations contenues dans ce document ne peuvent être communiquées qu’aux personnes physiques identifiées dans la liste de diffusion. <BR/>\
•	DR – Diffusion restreinte : les informations contenues dans ce document bénéficient des mesures de sécurité spécifiques en lien avec la réglementation en vigueur et les politiques de sécurité dédiées du MSI. <BR/>\
', my_Style)
elements.extend([Spacer(1, 0.5 * 50), diffusion, PageBreak()])

# Introduction
intro = Paragraph("Introduction", header_style)
elements.extend([intro, Spacer(1, 0.5 * 50)])
introduction = Paragraph(f'<b>Objet du document :</b><BR/><BR/>\
     ENTREPRISE est une société spécialisée dans activité de l’entreprise. L’entreprise à souhaiter auditer l’application application afin d’évaluer le niveau de sécurité de celle-ci. Cette application consiste expliquer le but de l’application succinctement.<BR/><BR/> \
     Ce document présente les différents résultats obtenus par les auditeurs lors du test d’intrusion et leurs recommandations de remédiation. <BR/><BR/>\
     Le travail de l’équipe d’audit essaye d’être le plus exhaustif possible, mais ne peut pas garantir la détection de toutes les vulnérabilités présentes sur le périmètre.<BR/><BR/><BR/>\
  <b>Contexte et périmètre de l’audit : </b><BR/><BR/>\
     L’audit a été mené depuis les locaux du Pôle Supérieur De La Salle à Rennes, entre le JJ/MM/AAAA et le JJ/MM/AAAA.<BR/><BR/> \
     L’audit a été effectuée avec une approche boite noire|boite grise|boite blanche, c’est-à-dire que les auditeurs disposaient (ou non) de compte d’accès sur l’application, du code source, etc.<BR/><BR/> \
     L’audit portait sur le périmètre suivant : URL , IP, domaine…<BR/> \
', normal_style)
elements.extend([introduction, PageBreak()])

# Synthese des resultats
results = Paragraph("Synthèse des resultats", header_style)
elements.extend([results, Spacer(1, 0.5 * 50)])
synthese = Paragraph(f'L’audit a permis de déterminer un niveau de sécurité : Nul Nul Nul la sécurité de votre entreprise.<BR/><BR/> \
', normal_style)
elements.extend([synthese, PageBreak()])

# Synthese des vulnérabilités
synth_vuln = Paragraph("Synthèse des resultats", header_style)
elements.extend([results, Spacer(1, 0.5 * 50)])
# Données du tableau Ressources
data_synth_vuln = [
    ["Identifiant", "VULNERABILITE","CRITICITE"],
    [1, "Absence d’attribut de sécurité sur les cookies","Majeure"],
]
  
table_synth_vuln = Table(data_synth_vuln)
  
# Mise en forme du tableau synthèse des resultats
table_synth_vuln.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
  
elements.extend([table_synth_vuln, PageBreak()])

#Tableau qui liste toutes les ressources de l'entreprise
ressourcestitle = Paragraph("Phase de découverte :", subheader_style)
elements.append(ressourcestitle)
bruteforce= Paragraph("Voici une liste des ressources identifiées de votre entreprise.")
elements.extend([bruteforce, Spacer(1, 0.5 * 50)])

data_ressources = [
    ["#", "Hostname", "IP", "Port", "Service"]
]

def parse_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

        index = 1
        for ip_address, host_data in data.items():
            hostname = host_data["hostname"]
            ports = host_data["ports"]

            if ports:
                for port in ports:
                    protocol = port["protocol"]
                    port_id = port["port_id"]
                    service_name = port["service_name"]

                    data_ressources.append([index, hostname, ip_address, port_id, service_name])
                    index += 1
            else:
                data_ressources.append([index, hostname, ip_address, "N/A", "N/A"])
                index += 1

# Usage: Specify the path to the JSON file
json_file_path = "ressources/rapport/result.json"
parse_json_file(json_file_path)
  
table_ressources = Table(data_ressources)
  
# Mise en forme du tableau Ressources
table_ressources.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
  
elements.extend([table_ressources, PageBreak()])
#Listing des test à afficher -> True si test effectué
bruteforcessh = True
CVE = True
entete_web = True
share_folder = True
dos = True
dhcp_starvation = True
wifi = True
check_tls = True

vuln_i = 1

def rapport_by_test(test, data_result):
    global vuln_i
    
    with open('ressources/rapport/texte.json') as json_file:
        data = json.load(json_file)

    title = Paragraph(f'Vulnérabilité {vuln_i} : {data[test]["titre"]}  <BR/><BR/>', subheader_style)
    elements.append(title)
    
    # Description de l'attaque
    desc = Paragraph(f'<b>Description :</b><BR/><BR/>\
         {data[test]["description"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([desc, Spacer(1, 0.5 * 50)])
    
    # Constat de l'attaque
    const = Paragraph(f'<b>Constat :</b><BR/><BR/>\
         {data[test]["constat"]} <BR/><BR/>\
         Ci dessous la liste des hôtes impactés : <BR/>\
      ', normal_style)
    elements.extend([const, Spacer(1, 0.5 * 50)])
    
    table_data_result = Table(data_result)
    
    # Mise en forme du tableau
    table_data_result.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.extend([table_data_result, Spacer(1, 0.5 * 72)])
    
    reco = Paragraph(f'<b>Recommandation :</b><BR/><BR/>\
         {data[test]["remediation"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([reco, PageBreak()])
    vuln_i = vuln_i + 1



def create_tableau(test):
# Ouvrir le fichier JSON et le charger en tant que dictionnaire
  with open('ressources/rapport/test.json') as f:
      data = json.load(f)
  
  # Initialiser une liste vide pour stocker les données recréées
  tableau = []
  
  # Ajouter une ligne d'en-tête pour le numéro, l'adresse IP et le port
  tableau.append(['#', 'IP', 'Port'])
  
  # Parcourir la liste d'IP et ajouter chaque élément au tableau
  for i, ip_obj in enumerate(data[test]['IP'], start=1):
      ip = ip_obj['adresse']
      port = ip_obj['port']
      tableau.append([i, ip, port])
  
  return tableau

tableau1 = create_tableau('test1')
tableau2 = create_tableau('test2')

with open('texte.json') as f:
    data = json.load(f)
    
if bruteforcessh == True:
  rapport_by_test("ssh_bf", tableau1)

if CVE == True :
  rapport_by_test("cve", tableau2)

if entete_web == True :
  rapport_by_test("entete_web", tableau1)
  
if share_folder == True:
  rapport_by_test("share_folder", tableau1)

if dos == True :
  rapport_by_test("dos", tableau1)

if dhcp_starvation == True :
  rapport_by_test("dhcp_starvation", tableau1)

if wifi == True :
  rapport_by_test("wifi", tableau1)

if check_tls == True :
  rapport_by_test("check_tls", tableau1)

# Conclusion
conclusion = Paragraph("Ce rapport présente un aperçu des vulnérabilités identifiées lors de l'audit système et du pentest réseau. Il est recommandé de prendre en compte les suggestions pour améliorer la sécurité de l'infrastructure.", normal_style)
elements.append(conclusion)

# Construction du document PDF
doc.build(elements)
