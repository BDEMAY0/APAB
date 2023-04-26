import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "projetannuel.apab@gmail.com"
SMTP_PASSWORD = "gsgeduzejuyichtk"
EMAIL_FROM = "projetannuel.apab@gmail.com"
EMAIL_TO = "maxence.giroult35@gmail.com"
EMAIL_SUBJECT = "RAPPORT APAB"
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
