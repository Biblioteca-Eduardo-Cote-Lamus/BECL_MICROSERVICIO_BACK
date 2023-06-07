from BECL_PDB.models import Eventos

event = Eventos.objects.get(id=3)
emails = event.encargados
print(event[0])