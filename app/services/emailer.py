import smtplib
from email.message import EmailMessage
import os

def enviar_enlace(destinatario, enlace):
    remitente = "auxsistemas@forgesa.net"
    contrasena = "FG_Systems20"
    smtp_host = "mail.forgesa.net"
    smtp_port = 587

    mensaje = EmailMessage()
    mensaje["Subject"] = "Evaluación psicométrica"
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje.set_content(f"""Hola, por favor accede al siguiente enlace para completar tu evaluación:

{enlace}
""")

    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(remitente, contrasena)
        smtp.send_message(mensaje)
