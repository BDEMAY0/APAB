# Importation des bibliothèques nécessaires
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, PageTemplate, BaseDocTemplate
from copy import deepcopy
from datetime import date
from locale import setlocale, LC_TIME
import json
import os
import time

vuln_i = 1
elements = []

current_dir = os.path.dirname(os.path.abspath(__file__))
directory = os.path.join(current_dir, "..", "ressources", "rapport")

with open(f"{directory}/audit.json", "r") as file:
  audit = json.load(file)

with open(f"{directory}/texte.json", "r") as file:
  texte = json.load(file)

with open(f"{directory}/rapport_attaques.json", "r") as file:
  attacks = json.load(file)

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
      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('FONTSIZE', (0, 0), (-1, 0), 12),
      ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
      ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#c9daf5")),
      ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#FFFFFF"))
  ])
#Fonctions 
def month_in_french(month):
  months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
  return months[month-1]

def parse_data_ressources():
    global audit

    index = 1
    data_ressources = [["#", "Hostname", "IP", "Port", "Service"]]
    for ip_address, host_data in audit.items():
        hostname = host_data["hostname"]
        ports = host_data["ports"]

        if ports:
            port_info = ""
            service = ""
            for i, port in enumerate(ports):
                protocol = port["protocol"]
                port_id = port["port_id"]
                service_name = port["service_name"]

                port_info += f"{port_id}\n"
                service += f"{service_name}\n"
            data_ressources.append([index, hostname, ip_address, port_info.strip(), service.strip()])
            index += 1
        else:
            data_ressources.append([index, hostname, ip_address, "N/A", "N/A"])
            index += 1
    return data_ressources


def scoring():
    global texte
    global attacks
    global audit

    ip_counts = {}
    scoring_count = 0	
    nb_ip = 0
    nb_ip = len(audit)
      
    for item in attacks:
        attack_name = item['attack_name']
        hosts = item['hosts']
        ip_addresses = [host['ip_address'] for host in hosts]
        for test in texte:
          if attack_name == test:
            ip_counts[attack_name] = round(len(ip_addresses)  / nb_ip * 100)
            ip_counts[attack_name] = ip_counts[attack_name]
            scoring_count += ip_counts[attack_name] * texte[test]["scoring"] 

    if scoring_count == 0:
      pass
    else :
      scoring_count = round((scoring_count))

    return ip_counts, scoring_count, nb_ip
  
def synthese():
  global elements
  global texte
  global attacks
  
    # Synthese des resultats
  results = Paragraph("Synthèse des resultats", header_style2)
  elements.extend([results, Spacer(1, 0.5 * 50)])
  synthese = Paragraph(f'L’audit a permis de déterminer le niveau de sécurité suivant :<BR/><BR/> \
  ', normal_style)
  elements.extend([synthese, Spacer(1, 0.5 * 50)])
  
  # Données du tableau Ressources
  data_synth_vuln = [["VULNERABILITE","CRITICITE", "% d'hôtes impactés"]]

  count = scoring()
  score_cve = 0
  for attack in attacks:
    if attack['success'] == True:
      vuln = texte[attack['attack_name']]["titre"]
      if count[0][attack['attack_name']] != 0 :
        score = f"{count[0][attack['attack_name']]} %"
      else :
        score = "N/A"
      if attack['attack_name'] == "cve":
        for host in attack["hosts"]:
          details = host["details"]
          for detail in details:
            cvss_score = detail['cvss_score']
            if cvss_score > score_cve:
              score_cve = cvss_score
              if score_cve >= 9:
                criticite = "Majeure"
              elif 5 < score_cve < 9:
                criticite = "Modérée"
              elif score_cve <= 5:
                criticite = "Mineure"
      else:
        criticite = texte[attack['attack_name']]["criticite"]
        
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
      ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#FFFFFF"))
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

  # Mise en place du tableau Score total
  data_score_total = [["Score Total", f"{count[1]}/100"]]
  table_score_total = Table(data_score_total)
  table_score_total.setStyle(table_style)

  phrase_score = f"Votre système d'information possède un score de {count[1]} %"
  
  #Mise en place du tableau explicatif Mineure, Majeure, Modérée
  data_criticite = [["Criticité", "Définition", "Délai de résolution"], ["Majeure", "Faille ou faiblesse au niveau de risque élevé, ayant\n un impact majeur sur les vecteurs de la cybersécurité\net pouvant compromettre activement vos actifs", "24 heures"], ["Modérée", "Faille ou faiblesse de niveau intermédiaire est observée\ndans votre système d'information, ayant un impact modéré\n sur les vecteurs de la cybersécurité et peut présenter une\ncertaine menace pour vos actifs", "1-2 jours"], ["Mineure", "Faille ou faiblesse minime est présente dans votre\n système d'information, mais son impact sur les\nvecteurs de cybersécurité est limité", "7 jours"]]
  table_criticite = Table(data_criticite)
  table_criticite.setStyle(table_style)
  
  elements.extend([table_synth_vuln,  Spacer(1, 0.2 * 72), table_score_total, Spacer(1, 0.5 * 72), table_criticite,  PageBreak()])


def rapport_by_test(test, tableau):
    global vuln_i
    global elements
    global texte

    title = Paragraph(f'Vulnérabilité {vuln_i} : {texte[test]["titre"]} ', subheader_style)
    elements.append(title)
    
    # Description de l'attaque
    desc = Paragraph(f'<BR/><b>Description :</b><BR/><BR/>\
         {texte[test]["description"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([desc, Spacer(1, 0.5 * 50)])
    
    # Constat de l'attaque
    const = Paragraph(f'<b>Constat :</b><BR/><BR/>\
         {texte[test]["constat"]} <BR/><BR/>\
         Ci dessous la liste des hôtes impactés : <BR/>\
      ', normal_style)
    elements.extend([const, Spacer(1, 0.5 * 50)])
    
    elements.extend([tableau, Spacer(1, 0.5 * 72)])
    
    reco = Paragraph(f'<b>Recommandation :</b><BR/><BR/>\
         {texte[test]["remediation"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([reco, PageBreak()])
    vuln_i = vuln_i + 1

def rapport_by_test_without_table(test):
    global vuln_i
    global elements
    global texte

    title = Paragraph(f'Vulnérabilité {vuln_i} : {texte[test]["titre"]} ', subheader_style)
    elements.append(title)
    
    # Description de l'attaque
    desc = Paragraph(f'<BR/><b>Description :</b><BR/><BR/>\
         {texte[test]["description"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([desc, Spacer(1, 0.5 * 50)])
    
    # Constat de l'attaque
    const = Paragraph(f'<b>Constat :</b><BR/><BR/>\
         {texte[test]["constat"]} <BR/>\
      ', normal_style)
    elements.extend([const, Spacer(1, 0.5 * 50)])
    
    reco = Paragraph(f'<b>Recommandation :</b><BR/><BR/>\
         {texte[test]["remediation"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([reco, PageBreak()])
    vuln_i = vuln_i + 1

def rapport_by_test_not_vulnerable(test):
    global vuln_i
    global elements
    global texte
      
    title = Paragraph(f'Vulnérabilité {vuln_i} : {texte[test]["titre"]} ', subheader_style)
    elements.append(title)
    
    # Description de l'attaque
    desc = Paragraph(f'<BR/><b>Description :</b><BR/><BR/>\
         {texte[test]["description"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([desc, Spacer(1, 0.5 * 50)])
    
    # Constat de l'attaque
    const = Paragraph(f'<b>Constat :</b><BR/><BR/>\
         {texte["no_result"]["constat"]} <BR/><BR/>\
      ', normal_style)
    elements.extend([const, PageBreak()])
    vuln_i = vuln_i + 1

def create_tableau(test):
    global attacks
  
    details_table = [["#", "Host"]]
    i = 1

    for attack in attacks:
        if attack["attack_name"] == test:
            for host in attack["hosts"]:
                ip_address = host["ip_address"]

                row = [i] + [ip_address]
                details_table.append(row)
                i += 1
    
    table_data_result = Table(details_table)
    table_data_result.setStyle(table_style)
              
    return table_data_result

def tableau_entete_web():
    details_table = [["#", "Host", "Server", "X-Powered-By", "X-AspNet-Version", "Access-Control\nAllow-Origin"]]
    global attacks
    i = 1

    for attack in attacks:
        if attack["attack_name"] == "entete_web":
            for host in attack["hosts"]:
                ip_address = host["ip_address"]
                details = host["details"][0] if host["details"] else {}
                server = details.get("Server", "")
                powered_by = details.get("X-Powered-By", "")
                aspnet_version = details.get("X-AspNet-Version", "")
                access_control = details.get("Access-Control-Allow-Origin", "")

                row =  [i] + [ip_address] + [server] + [powered_by] + [aspnet_version] + [access_control]
                details_table.append(row)
                i += 1

    table_data_result = Table(details_table)
    # Mise en forme du tableau
    table_data_result.setStyle(table_style)
  
    return table_data_result

def tableau_smb():
    details_table = [["#", "Host", "Dossier accessible"]]
    global attacks
    i = 1

    for attack in attacks:
        if attack["attack_name"] == "smb_scanner":
            for host in attack["hosts"]:
                ip_address = host["ip_address"]
                details = host["details"] if host["details"] else {}
                detail = "\n".join(details[:-1]) if details else ""
                if details:
                    detail += "\n" + details[-1]
                row = [i] + [ip_address, detail]
                details_table.append(row)
                i += 1

    table_data_result = Table(details_table)
    # Mise en forme du tableau
    table_data_result.setStyle(table_style)
  
    return table_data_result

def tableau_banner():
    details_table = [["#", "Host", "Port", "Service", "Version"]]
    global attacks
    i = 1

    for attack in attacks:
        if attack["attack_name"] == "banner":
            for host in attack["hosts"]:
                ip_address = host["ip_address"]
                port = []
                service = []
                version = []
                for detail in host["details"]:
                    port.append(detail.get("Port", "")) 
                    service.append(detail.get("Service", "")) 
                    version.append(detail.get("Version", "")) 

                # Les détails sont joints avec des sauts de ligne pour n'apparaître qu'une seule fois par adresse IP
                row = [i, ip_address, '\n'.join(port), '\n'.join(service), '\n'.join(version)]
                details_table.append(row)
                i += 1

    table_data_result = Table(details_table)
    # Mise en forme du tableau
    table_data_result.setStyle(table_style)
  
    return table_data_result



def tableau_CVE():
    global attacks

    table_style_cve = TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
      ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('FONTSIZE', (0, 0), (-1, 0), 14),
      ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
      ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#c9daf5")),
      ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#FFFFFF"))
  ])
  
    details_table = [["#", "Host", "CVE", "Score CVSS", "Produit", "Version"]]
    i = 1

    for attack in attacks:
        if attack["attack_name"] == "cve":
            for host in attack["hosts"]:
                ip_address = host["ip_address"]
                details = host["details"]
                for detail in details:
                  CVE = detail['id']
                  cvss_score = detail['cvss_score']
                  product = detail['product']
                  version = detail['version']
          
                  row =  [i] + [ip_address] + [CVE] + [cvss_score] + [product] + [version]
                  details_table.append(row)
                  i += 1
    
    table_data_result = Table(details_table)

    color_red_carmin = colors.HexColor("#9c1e1e")
    color_red = colors.HexColor("#f74545")
    color_orange = colors.HexColor("#fa9052")
    color_yellow = colors.HexColor("#f2f063")

    # Parcourir le tableau pour appliquer les couleurs
    for row in range(1, len(details_table)):
      cell_value = details_table[row][3]
      if isinstance(cell_value, (int, float)):
        if cell_value > 9:
            table_style_cve.add('BACKGROUND', (3, row), (3, row), color_red_carmin)
        elif 7 <= cell_value <= 9:
            table_style_cve.add('BACKGROUND', (3, row), (3, row), color_red)
        elif 4 <= cell_value <= 7:
            table_style_cve.add('BACKGROUND', (3, row), (3, row), color_orange)
        elif cell_value < 4:
            table_style_cve.add('BACKGROUND', (3, row), (3, row), color_yellow)
    # Mise en forme du tableau
    table_data_result.setStyle(table_style_cve)
  
    return table_data_result

def if_data_in_attack(attack_name):
  global attacks
  table = 0
  # Parcours des attaques
  for attack in attacks:
    if attack['attack_name'] == attack_name:
      hosts = attack['hosts']
      
      # Vérification des informations dans les hôtes
      for host in hosts:
          ip_address = host['ip_address']
          if not ip_address:
            table = 0
          if ip_address :
            table = 1

  return table

def print_attack():
  global elements
  global attacks

  for attack in attacks:
    if attack['success'] == True:
      if attack['attack_name'] == "cve":
        tableau = tableau_CVE()
      elif attack['attack_name'] == "entete_web":
        tableau = tableau_entete_web()
      elif attack['attack_name'] == "smb_scanner":
        tableau = tableau_smb()
      elif attack['attack_name'] == "banner":
        tableau = tableau_banner()
      else:
        tableau = create_tableau(attack['attack_name'])
      
      if if_data_in_attack(attack['attack_name']) == 1:
        rapport_by_test(attack['attack_name'], tableau)
      else:
        rapport_by_test_without_table(attack['attack_name'])
    else :
      pass

  for attack in attacks :
    if attack['success'] == False:
      rapport_by_test_not_vulnerable(attack['attack_name'])

def annexe():
    global elements
    global texte

    # Synthèse des résultats
    results = Paragraph("Annexe", header_style2)
    elements.extend([results, Spacer(1, 0.5 * 50)])

    data_annexe = [["Attaque", "Multiplicateur"]]

    for attack in texte:
        if attack != "no_result" and attack != "annexe":
            titre = texte[attack]["titre"]
            score = texte[attack]["scoring"]
            row = [titre, score]
            data_annexe.append(row)

    table_annexe = Table(data_annexe)
    table_annexe.setStyle(table_style)
    elements.extend([table_annexe, Spacer(1, 0.5 * 50)])

    

def main_rapport():
  global elements
  global directory
  
  directory_client = os.path.join(current_dir, "..", "ressources", "parametres", "options.txt")

  with open(directory_client, "r") as f:
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
  directory_export = os.path.join(current_dir, "..", "rapport")
  output_file = f"{directory_export}/Rapport_APAB{nom_entreprise}_{timestamp}.pdf"
  doc = BaseDocTemplate(output_file, pagesize=letter)

  today = date.today()
  auj = today.strftime("%d ") + month_in_french(today.month) + today.strftime(" %Y")
  
  # Page de couverture
  nom_entreprise = nom_entreprise.replace("_", " ")
  centered_style = deepcopy(header_style)
  centered_style.alignment = TA_CENTER
  titre_rapport = Paragraph(f"Rapport d'Audit et Pentest Automatisé <BR/> APAB x {nom_entreprise}", centered_style)
  date_rapport = Paragraph(f'Date : {auj}', normal_style)
  image = f"{directory}/APAB.png"
  im = Image(image, 8*inch, 4.5*inch)
  elements = [Spacer(1, 0.4 * 72), im, Spacer(1, 1 * 72), titre_rapport, Spacer(1, 2 * 72), date_rapport, PageBreak()]

  
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
  •	C1 – Accès limité : les informations contenues dans ce document ne peuvent être communiquées qu’à des personnels de APAB ou de ses partenaires. <BR/>\
  •	C2 – Document confidentiel : les informations contenues dans ce document ne peuvent être communiquées qu’à des personnels de APAB ou des tiers explicitement nommés dans la liste de diffusion. <BR/>\
  •	C3 – Document secret : les informations contenues dans ce document ne peuvent être communiquées qu’aux personnes physiques identifiées dans la liste de diffusion. <BR/>\
  •	DR – Diffusion restreinte : les informations contenues dans ce document bénéficient des mesures de sécurité spécifiques en lien avec la réglementation en vigueur et les politiques de sécurité dédiées de APAB. <BR/>\
  ', my_Style)
  elements.extend([Spacer(1, 0.5 * 50), diffusion, PageBreak()])
  
  
  # Introduction
  intro = Paragraph("Introduction", header_style2)
  elements.extend([intro, Spacer(1, 0.5 * 50)])
  introduction = Paragraph(f'<b>Objet du document :</b><BR/><BR/>\
       L’entreprise{nom_entreprise.replace("_", " ")} à souhaiter auditer ses systèmes et réseaux afin d’évaluer le niveau de sécurité de ceux-ci. <BR/><BR/> \
       Ce document présente les différents résultats obtenus lors du test d’intrusion ainsi que des recommandations de remédiation. <BR/><BR/>\
       Le travail de l’équipe d’audit essaye d’être le plus exhaustif possible, mais ne peut pas garantir la détection de toutes les vulnérabilités présentes sur le périmètre.<BR/><BR/><BR/>\
    <b>Contexte et périmètre de l’audit : </b><BR/><BR/>\
       L’audit a été mené depuis les locaux de{nom_entreprise.replace("_", " ")} le {auj}.<BR/><BR/> \
       L’audit portait sur le périmètre suivant : {ip} /{masque_sous_reseau}<BR/> \
  ', normal_style)
  elements.extend([introduction, PageBreak()])
  
  synthese()
  
  #Tableau qui liste toutes les ressources de l'entreprise
  ressourcestitle = Paragraph("Phase de découverte :", header_style2)
  elements.append(ressourcestitle)
  ressources= Paragraph("Voici une liste des ressources identifiées de votre entreprise.")
  elements.extend([ressources, Spacer(1, 0.5 * 50)])
  
  data_ressources = parse_data_ressources()
    
  table_ressources = Table(data_ressources)
    
  # Mise en forme du tableau Ressources
  table_ressources.setStyle(table_style)
    
  elements.extend([table_ressources, PageBreak()])

  print_attack()
  annexe()
  
  # Construction du document PDF
  doc.build(elements)

if __name__ == "__main__":
  main_rapport()
