import os
import smtplib
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def f_send_mail(name_file):
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

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "projetannuel.apab@gmail.com"
    SMTP_PASSWORD = "gsgeduzejuyichtk"
    EMAIL_FROM = "projetannuel.apab@gmail.com"
    EMAIL_TO = mail
    EMAIL_SUBJECT = f'{niveau_diffusion} PROJET APAB'
    EMAIL_MESSAGE = "Bonjour, \n\nVous trouverez ci-joint le rapport issue de nos tests.\n\nCordialement,\n\nSociété APAB"

    # création du message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = EMAIL_SUBJECT
    msg.attach(MIMEText(EMAIL_MESSAGE))

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_zip = f'{current_dir}/ressources/mail/{name_file}.zip'
    file_pdf = name_file.replace(".pdf", "")
    file_zip = f'{file_pdf}.zip'

    # ajout de la pièce jointe
    with open(path_zip, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="zip")
        attachment.add_header("Content-Disposition", "attachment", filename=file_zip)
        msg.attach(attachment)

    # envoi du message
    s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    s.starttls()
    s.login(SMTP_USERNAME, SMTP_PASSWORD)
    s.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    s.quit()
    subprocess.run(f'rm {path_zip}', shell=True)
