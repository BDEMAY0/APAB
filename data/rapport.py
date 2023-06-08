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
import os
import time

vuln_i = 1
elements = []

# Styles de paragraphe
styles = getSampleStyleSheet()
header_style = styles['Heading1']
header_style2 = ParagraphStyle(
    name='SubtitleStyle',
    parent=getSampleStyleSheet()['Heading1'],
    textColor=colors.white,
    leftIndent=0, 
    bulletIndent=20,
    border=0.5,
    borderColor=colors.HexColor("#003366"),  
    backColor=colors.HexColor("#003366"),  #
)
subheader_style = ParagraphStyle(
    name='SubtitleStyle',
    parent=getSampleStyleSheet()['Heading2'],
    textColor=colors.white,
    fontSize=14,
    leftIndent=0, 
    bulletIndent=20,
    border=0.5,
    borderColor=colors.HexColor("#003366"),  
    backColor=colors.HexColor("#003366"),  #
)
normal_style = styles['Normal']

table_style = TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
      ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('FONTSIZE', (0, 0), (-1, 0), 14),
      ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
      ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#c9daf5")),
      ('GRID', (0, 0), (-1, -1), 1, colors.black)
  ])
#Fonctions 
def parse_result():
    with open("ressources/rapport/result.json", "r") as file:
        data = json.load(file)

        index = 1
        data_ressources = [["#", "Hostname", "IP", "Port", "Service"]]
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
    return data_ressources

def scoring():
    ip_counts = {}
    scoring_count = 0
    with open('ressources/rapport/jsonfinal.json') as f:
      data = json.load(f)

    for item in data:
        attack_name = item['attack_name']
        hosts = item['hosts']
        ip_addresses = [host['ip_address'] for host in hosts]
        if attack_name == "entete_web":
          ip_counts[attack_name] = 3 * len(ip_addresses)
          scoring_count += 3 * len(ip_addresses)
        elif attack_name == "cve":
          ip_counts[attack_name] = 2 * len(ip_addresses)
          scoring_count += 2 * len(ip_addresses)
        elif attack_name =="ssh_bf":
          ip_counts[attack_name] = 3 * len(ip_addresses)
          scoring_count += 3 * len(ip_addresses)

    return ip_counts, scoring_count
  
def synthese():
  global elements
  
    # Synthese des resultats
  results = Paragraph("Synthèse des resultats", header_style2)
  elements.extend([results, Spacer(1, 0.5 * 50)])
  synthese = Paragraph(f'L’audit a permis de déterminer un niveau de sécurité : Texte en fonction du scoring<BR/><BR/> \
  ', normal_style)
  elements.extend([synthese, Spacer(1, 0.5 * 50)])
  
  # Données du tableau Ressources
  data_synth_vuln = [["VULNERABILITE","CRITICITE", "SCORE"]]

  count = scoring()
  
  with open("ressources/rapport/texte.json", "r") as file:
    data = json.load(file)

  with open('ressources/rapport/jsonfinal.json') as f:
    attacks = json.load(f)
    
  for attack in attacks:
    if attack['success'] == True:
      vuln = data[attack['attack_name']]["titre"]
      criticite = data[attack['attack_name']]["criticite"]
      score = count[0][attack['attack_name']]
      row =  [vuln] + [criticite] + [score]
      data_synth_vuln.append(row)
      
  table_synth_vuln = Table(data_synth_vuln)
  
  table_style_synth =  TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
      ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('FONTSIZE', (0, 0), (-1, 0), 14),
      ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
      ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#c9daf5")),
      ('GRID', (0, 0), (-1, -1), 1, colors.black)
  ])
  
  color_red = colors.HexColor("#f74545")
  color_orange = colors.HexColor("#fa9052")
  color_yellow = colors.HexColor("#f2f063")
  
  # Parcourir le tableau pour appliquer les couleurs
  for row in range(1, len(data_synth_vuln)):
      cell_value = data_synth_vuln[row][1]
      if isinstance(cell_value, str):
          if cell_value == 'Majeure':
              table_style_synth.add('BACKGROUND', (1, row), (1, row), color_red)
          elif cell_value == 'Modérée':
              table_style_synth.add('BACKGROUND', (1, row), (1, row), color_orange)
          elif cell_value == 'Mineure':
              table_style_synth.add('BACKGROUND', (1, row), (1, row), color_yellow)
  
  # Mise en forme du tableau synthèse des resultats
  table_synth_vuln.setStyle(table_style_synth)

  elements.extend([table_synth_vuln, PageBreak()])

def rapport_by_test(test, tableau):
    global vuln_i
    global elements

    with open('ressources/rapport/texte.json') as json_file:
        data = json.load(json_file)

    title = Paragraph(f'Vulnérabilité {vuln_i} : {data[test]["titre"]} ', subheader_style)
    elements.append(title)
    
    # Description de l'attaque
    desc = Paragraph(f'<BR/><b>Description :</b><BR/><BR/>\
         {data[test]["description"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([desc, Spacer(1, 0.5 * 50)])
    
    # Constat de l'attaque
    const = Paragraph(f'<b>Constat :</b><BR/><BR/>\
         {data[test]["constat"]} <BR/><BR/>\
         Ci dessous la liste des hôtes impactés : <BR/>\
      ', normal_style)
    elements.extend([const, Spacer(1, 0.5 * 50)])
    
    elements.extend([tableau, Spacer(1, 0.5 * 72)])
    
    reco = Paragraph(f'<b>Recommandation :</b><BR/><BR/>\
         {data[test]["remediation"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([reco, PageBreak()])
    vuln_i = vuln_i + 1

def rapport_by_test_not_vulnerable(test):
    global vuln_i
    global elements
    
    with open('ressources/rapport/texte.json') as json_file:
        data = json.load(json_file)
      
    title = Paragraph(f'Vulnérabilité {vuln_i} : {data[test]["titre"]} ', subheader_style)
    elements.append(title)
    
    # Description de l'attaque
    desc = Paragraph(f'<BR/><b>Description :</b><BR/><BR/>\
         {data[test]["description"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([desc, Spacer(1, 0.5 * 50)])
    
    # Constat de l'attaque
    const = Paragraph(f'<b>Constat :</b><BR/><BR/>\
         {data["no_result"]["constat"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([const, PageBreak()])
    vuln_i = vuln_i + 1

def create_tableau(test):
    details_table = [["Host"]]
    with open('ressources/rapport/jsonfinal.json') as f:
        data = json.load(f)

    for attack in data:
        if attack["attack_name"] == test:
            for host in attack["hosts"]:
                ip_address = host["ip_address"]

                row =  [ip_address]
                details_table.append(row)
    
    table_data_result = Table(details_table)
    table_data_result.setStyle(table_style)
              
    return table_data_result

def tableau_entete_web():
    details_table = [["Host", "Server", "X-Powered-By", "X-AspNet-Version", "Access-Control-Allow-Origin"]]
    with open('ressources/rapport/jsonfinal.json') as f:
        data = json.load(f)

    for attack in data:
        if attack["attack_name"] == "entete_web":
            for host in attack["hosts"]:
                ip_address = host["ip_address"]
                details = host["details"][0] if host["details"] else {}
                server = details.get("Server", "")
                powered_by = details.get("X-Powered-By", "")
                aspnet_version = details.get("X-AspNet-Version", "")
                access_control = details.get("Access-Control-Allow-Origin", "")

                row =  [ip_address] + [server] + [powered_by] + [aspnet_version] + [access_control]
                details_table.append(row)

    table_data_result = Table(details_table)
    # Mise en forme du tableau
    table_data_result.setStyle(table_style)
  
    return table_data_result

def tableau_CVE():
    table_style_cve = TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
      ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('FONTSIZE', (0, 0), (-1, 0), 14),
      ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
      ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#c9daf5")),
      ('GRID', (0, 0), (-1, -1), 1, colors.black)
  ])
  
    details_table = [["Host", "CVE", "Score CVSS", "Produit", "Version"]]
    with open('ressources/rapport/jsonfinal.json') as f:
        data = json.load(f)

    for attack in data:
        if attack["attack_name"] == "cve":
            for host in attack["hosts"]:
                ip_address = host["ip_address"]
                details = host["details"]
                for detail in details:
                  CVE = detail['id']
                  cvss_score = detail['cvss_score']
                  product = detail['product']
                  version = detail['version']
          
                  row =  [ip_address] + [CVE] + [cvss_score] + [product] + [version]
                  details_table.append(row)
    
    table_data_result = Table(details_table)

    color_red_carmin = colors.HexColor("#9c1e1e")
    color_red = colors.HexColor("#f74545")
    color_orange = colors.HexColor("#fa9052")
    color_yellow = colors.HexColor("#f2f063")

    # Parcourir le tableau pour appliquer les couleurs
    for row in range(1, len(details_table)):
      cell_value = details_table[row][2]
      if isinstance(cell_value, (int, float)):
        if cell_value > 9:
            table_style_cve.add('BACKGROUND', (2, row), (2, row), color_red_carmin)
        elif 7 <= cell_value <= 9:
            table_style_cve.add('BACKGROUND', (2, row), (2, row), color_red)
        elif 4 <= cell_value <= 7:
            table_style_cve.add('BACKGROUND', (2, row), (2, row), color_orange)
        elif cell_value < 4:
            table_style_cve.add('BACKGROUND', (2, row), (2, row), color_yellow)
    # Mise en forme du tableau
    table_data_result.setStyle(table_style_cve)
  
    return table_data_result

def print_attack():
  global elements
  
  with open('ressources/rapport/jsonfinal.json') as f:
    attacks = json.load(f)

  for attack in attacks:
    if attack['success'] == True:
      if attack['attack_name'] == "cve":
        tableau = tableau_CVE()
      elif attack['attack_name'] == "entete_web":
        tableau = tableau_entete_web()
      else:
        tableau = create_tableau(attack['attack_name'])
      rapport_by_test(attack['attack_name'], tableau)
    else :
      rapport_by_test_not_vulnerable(attack['attack_name'])

def main():
  global elements
  
  current_dir = os.path.dirname(os.path.abspath(__file__))
  folder = os.path.join(current_dir, "ressources", "parametres", "options.txt")
  path_options = os.path.expanduser(folder)
  with open(path_options, "r") as f:
      for line in f:
          key, value = line.strip().split(" :")
          if key == "mail_entreprise":
              mail = value.replace(" ", "")
          elif key == "niveau_diffusion":
              niveau_diffusion = value
          elif key == "nom_entreprise":
              nom_entreprise = value.replace(" ", "_")
          elif key == "ip":
              ip = value.replace(" ", "")
          elif key == "masque_sous_reseau":
              masque_sous_reseau = value.replace(" ", "")
  
  # Obtenir l'horodatage actuel
  timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
  
  # Configuration du fichier PDF
  output_file = f"rapport/Rapport_APAB{nom_entreprise}_{timestamp}.pdf"
  doc = BaseDocTemplate(output_file, pagesize=letter)
  
  today = date.today()
  auj = today.strftime("%d %B %Y")
  
  # Page de couverture
  titre_rapport = Paragraph("Rapport d'Audit et Pentest Automatisé\n APAB", header_style)
  date_rapport = Paragraph(f'Date : {auj}', normal_style)
  elements = [Spacer(1, 0.4 * 72),  Spacer(1, 0.7 * 72), date_rapport, PageBreak()]
  im = Image('ressources/rapport/APAB.png', 8*inch, 6*inch)
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
      canvas.drawString(450, 750, niveau_diffusion)
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
  backColor='#c9daf5',
  fontSize=11,
  borderColor='#003366',
  borderWidth=2,
  borderPadding=(20,20,20),
  leading=15,
  alignment=0
  )
  interlocuteur = Paragraph(f'<b>Interlocuteurs : </b><BR/>\
       Société APAB <BR/> \
  	 <i>Auditeur.</i>\
  ', my_Style)
            
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
  intro = Paragraph("Introduction", header_style2)
  elements.extend([intro, Spacer(1, 0.5 * 50)])
  introduction = Paragraph(f'<b>Objet du document :</b><BR/><BR/>\
       L’entreprise{nom_entreprise.replace("_", " ")} à souhaiter auditer ses systèmes et réseaux afin d’évaluer le niveau de sécurité de ceux-ci. <BR/><BR/> \
       Ce document présente les différents résultats obtenus par les auditeurs lors du test d’intrusion et leurs recommandations de remédiation. <BR/><BR/>\
       Le travail de l’équipe d’audit essaye d’être le plus exhaustif possible, mais ne peut pas garantir la détection de toutes les vulnérabilités présentes sur le périmètre.<BR/><BR/><BR/>\
    <b>Contexte et périmètre de l’audit : </b><BR/><BR/>\
       L’audit a été mené depuis les locaux de{nom_entreprise.replace("_", " ")} le {auj}.<BR/><BR/> \
       L’audit a été effectuée avec une approche boite noire|boite grise|boite blanche, c’est-à-dire que les auditeurs disposaient (ou non) de compte d’accès sur l’application, du code source, etc.<BR/><BR/> \
       L’audit portait sur le périmètre suivant : {ip} {masque_sous_reseau}<BR/> \
  ', normal_style)
  elements.extend([introduction, PageBreak()])
  
  synthese()
  
  #Tableau qui liste toutes les ressources de l'entreprise
  ressourcestitle = Paragraph("Phase de découverte :", header_style2)
  elements.append(ressourcestitle)
  bruteforce= Paragraph("Voici une liste des ressources identifiées de votre entreprise.")
  elements.extend([bruteforce, Spacer(1, 0.5 * 50)])
  
  data_ressources = parse_result()
    
  table_ressources = Table(data_ressources)
    
  # Mise en forme du tableau Ressources
  table_ressources.setStyle(table_style)
    
  elements.extend([table_ressources, PageBreak()])

  print_attack()
  # Construction du document PDF
  doc.build(elements)
  
main()
