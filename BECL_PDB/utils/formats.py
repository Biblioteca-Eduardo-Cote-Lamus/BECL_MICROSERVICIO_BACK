from datetime import datetime 
from docxtpl import DocxTemplate
from BECL_Login.models import Usuarios

def __get_list_emails(emails):
    tics = list(Usuarios.objects.filter(cargo_id=1).values())
    list_email = list(map(lambda tic: tic["email"], tics))
    for email in emails:
        if not email in list_email:
            list_email.append(email)
    return list(map(lambda e: {'email': e} , list_email))

def get_general_document(
    date, title, dependece, people, name, code, start, end, typeEvent
):
    # Se genera el documento dependiendo del typeEvent
    doc = (
        DocxTemplate("BECL_PDB/doc/formato auditorio.docx")
        if typeEvent == "A"
        else DocxTemplate("BECL_PDB/doc/formato semilleros.docx")
    )
    # titulo y semillero pueden ser lo mismo. De igual manera con el departamento y dependencia.
    data_docx = {
        "fecha": date,
        "titulo": title,
        "dependencia": dependece,
        "personas": people,
        "nombre": name,
        "codigo": code,
        "inicio": start,
        "fin": end,
    }
    # se genera la terminacion del formato.
    loan = "formato-auditorio" if typeEvent == "A" else "formato-semillero"
    name_file = f"{date}-{code}-{'-'.join(title.split(' '))}-{loan}"
    folder = (
        f"BECL_PDB/doc/doc_auditorio/{name_file}.docx"
        if typeEvent == "A"
        else f"BECL_PDB/doc/doc_semillero/{name_file}.docx"
    )
    # folderPDf = f'BECL_PDB/doc/doc_auditorio_pdf/{name_file}.pdf' if typeEvent == 'A' else f'BECL_PDB/doc/doc_semillero_pdf/{name_file}.pdf'
    # se renderiza y guarda la data en el documento.
    doc.render(data_docx)
    doc.save(folder)
    # convert(folder,  folderPDf)

    return f"{name_file}"

def format_event(title, date, start, end, emails):
    list_emails = __get_list_emails(emails)
    hour_format_24_s = datetime.strptime(start, "%I:%M %p").strftime("%H:%M:%S")
    hour_format_24_e = datetime.strptime(end, "%I:%M %p").strftime("%H:%M:%S")
    event = {
        "summary": f"{title}",
        "location": "",
        "description": "",
        "start": {
            "dateTime": f"{date}T{hour_format_24_s}-05:00",
            "timeZone": "America/Bogota",
        },
        "end": {
            "dateTime": f"{date}T{hour_format_24_e}-05:00",
            "timeZone": "America/Bogota",
        },
        "attendees": list_emails,
        "reminders": {
            "useDefault": False,
        },
    }
    return event
