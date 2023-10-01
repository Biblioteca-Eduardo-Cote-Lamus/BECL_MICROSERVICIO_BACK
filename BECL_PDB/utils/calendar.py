from datetime import datetime

"""
    list_event_today = events_today(service,date[0],date[1],type_event)
    list_possible_hours = possible_hours(list_event_today,list_hours_today.copy())
    ranges = generate_ranges(list_possible_hours)
    answer = generate_possible_end_times(ranges)
    service.close()
"""

list_events = []
list_hours_today = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]


def get_events_today(events_list, option):
    events = list(filterByOption(events_list, option))
    results = realization_events(events)
    # obtenmos la lista de posibles horas
    list_possible_hours = possible_hours(results, list_hours_today.copy())
    available_hours = generate_possible_end_times(generate_ranges(list_possible_hours))
    return available_hours


# Funcion que me devuelve los eventos a realizar
def realization_events(list_event):
    list_hours_events = []
    for event in list_event:
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        start_time = datetime.strptime(
            datetime.fromisoformat(start).strftime("%I:%M %p"), "%I:%M %p"
        ).strftime("%H")
        end_time = datetime.strptime(
            datetime.fromisoformat(end).strftime("%I:%M %p"), "%I:%M %p"
        ).strftime("%H")
        list_hours_events.append([int(start_time), int(end_time)])
    return list_hours_events


# Funcion que me remueve las horas que no estan disponibles
def possible_hours(list_events, list_hours):
    for schedule in list_events:
        if len(schedule) == 0:
            return
        else:
            for hora in range(schedule[0], schedule[1]):
                list_hours.remove(hora)
    return list_hours


# Funcion que genera los posbles rangos de las horas
def generate_ranges(list_schedule):
    ranges = []
    if len(list_schedule) == 0:
        return ranges
    start_hours = list_schedule[0]
    if len(list_schedule) == 14:
        ranges.append([6, 19])
        return ranges
    for i in range(len(list_schedule) - 1):
        if list_schedule[i + 1] - list_schedule[i] != 1:
            if start_hours == list_schedule[i]:
                ranges.append([start_hours])
            else:
                ranges.append([start_hours, list_schedule[i]])
            start_hours = list_schedule[i + 1]
    ranges.append([start_hours, list_schedule[-1]])
    return ranges


# Funcion que genera los rangos de las horas: Ejemplo empieza a las 6 lo max es a las 10 tiempo de apartado de 4h
def generate_ranges_hours(start, end):
    max_possible_hours = start + 4
    if max_possible_hours in range(start, end + 1):
        return {
            "hours": str(start) + ":00 am"
            if start <= 12
            else str(abs(start - 12)) + ":00 pm",
            "possible": [x for x in range(start + 1, max_possible_hours + 1)],
        }
    else:
        return {
            "hours": str(start) + ":00 am"
            if start <= 12
            else str(abs(start - 12)) + ":00 pm",
            "possible": [x for x in range(start + 1, end + 2)],
        }


# Funcion que genera los rangos posibles si solo hay una hora
def generate_possible_end_times(ranges):
    hours = []
    for range_hours in ranges:
        lists = (
            list(range(range_hours[0], range_hours[1] + 1))
            if len(range_hours) == 2
            else list(range(range_hours[0], range_hours[0] + 1))
        )
        for i in lists:
            hours.append(generate_ranges_hours(i, range_hours[-1]))
    return hours


# Funcion que filtar los eventos por la opciones: A: Auditorio, S: semillero, BD: Base de datos
def filterByOption(events, option):
    return filter(lambda event: option in event["summary"].split(":")[0], events)
