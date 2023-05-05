from docxtpl import DocxTemplate
from datetime import datetime
from docx2pdf import convert

def get_format_document_A(title, name, code, dependence, start, end, num_people):
    doc = DocxTemplate('BECL_PDB/doc/formato auditorio.docx')
    now = datetime.utcnow()
    
    hour = now.strftime('%H-%M-%S')
    date = now.strftime('%d-%m-%Y')
    data_docx = {
        'fecha': date,
        'titulo': title,
        'dependencia': dependence,
        'personas': num_people,
        'nombre': name,
        'codigo': code,
        'inicio': start,
        'fin': end,
    }
    
    name_docx = f'{hour} Prestamo Auditorio.docx'
    doc.render(data_docx)
    doc.save(name_docx)
    
    return name_docx
    
name = get_format_document_A('SIA', 'Andres', '233424', 'Biblioteca', '8:00 PM', '7;00 PM', '100')

convert(name)
