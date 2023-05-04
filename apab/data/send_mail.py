import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

current_dir = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(current_dir, "ressources", "parametres", "options.txt")
path_options = os.path.expanduser(folder)
with open(path_options, "r") as f:
    for line in f:
        key, value = line.strip().split(" :")
        if key == "mail":
            mail = value.replace(" ", "")
        elif key == "niveau_diffusion":
            niveau_diffusion = value.replace(" ", "")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "projetannuel.apab@gmail.com"
SMTP_PASSWORD = "gsgeduzejuyichtk"
EMAIL_FROM = "projetannuel.apab@gmail.com"
EMAIL_TO = mail
EMAIL_SUBJECT = f'{niveau_diffusion} PROJET APAB'
EMAIL_MESSAGE = "Bonjour, \n Vous trouverez ci-joint le rapport issue de nos tests.\n Cordialemennt,\n APAB"

# création du message
msg = MIMEMultipart()
msg['From'] = EMAIL_FROM
msg['To'] = EMAIL_TO
msg['Subject'] = EMAIL_SUBJECT
msg.attach(MIMEText(EMAIL_MESSAGE))

# ajout de la pièce jointe
with open("nomdefichier.ext", "rb") as f:
    attachment = MIMEApplication(f.read(), _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename="rapport_APAB.pdf")
    msg.attach(attachment)

# envoi du message
s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
s.starttls()
s.login(SMTP_USERNAME, SMTP_PASSWORD)
s.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
s.quit()

print("Rapport envoyé avec succès")
