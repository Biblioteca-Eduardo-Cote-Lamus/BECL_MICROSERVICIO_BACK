from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_email(data: dict, html_template=None, files=None):
    """
    Envía un correo electrónico con los datos proporcionados.

    Args:
        data (dict): Un diccionario con las claves 'subject', 'body', 'from' y 'to'.
        html_template: Una plantilla html convertida a string.
        files: Una lista con los path absolutos de los documentos a enviar.
    """

    mail = EmailMultiAlternatives(
        subject=data["subject"],
        body=data["body"] if not html_template else strip_tags(html_template),
        from_email=data["from"],
        to=[data["to"]],
    )

    if html_template:
        mail.attach_alternative(html_template, 'text/html')

    if files:
       for file in files:
        mail.attach_file(file)

    mail.send()

    return "email was send"


SUBJECTS = {
    "A": ["Préstamo Auditorio", "plantilla_auditorio.html"],
    "S": ["Préstamo Sala de Semilleros", "plantilla_semillero.html"],
    "BD": ["Capacitación Base de Datos.", "plantilla_capacitacion.html"],
}

