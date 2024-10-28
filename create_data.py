#!/bin/python

from random import randrange
from datetime import datetime, timedelta
import random

adrese = [
    "Avenija dubrovnik 10",
    "Zagrebačka cesta 15",
    "Ilica 36",
    "Ilica 336",
    "Sarajevska ulica 45",
    "Maksimirska 67",
    "Maksimirska 45",
    "Vodnikova 35",
    "Radićeva 100",
    "Radnička 42",
    "Zvonimirova 52",
    "Zvonimirova 100",
    "Heinzelova 57",
    "Heinzelova 89",
    "Gospodska 16",
    "Bolnička 14",
    "Vrapčanska 64",
    "Malešnica 92"
]

gradovi = [
    "Zagreb",
    "Split",
    "Rijeka",
    "Osijek"
]

drzava = "Hrvatska"

imena_restorana = [
    "Klopica",
    "Restoran Zagreb",
    "Johan Frank",
    "Kralj Melkior",
    "Dubravi dvori"
    "Novi mlin",
    "Krilca",
    "Stara dvojka",
    "Borić",
    "Kuglana",
    "Stara pečenjara",
    "Babi Kebaba",
    "Kod Jože",
    "Mata Hari",
    "Dunav",
    "Sava",
    "Jadran",
    "Medin Brlog",
    "Crveni Lisac",
    "Mekani čvarak",
    "Janina konoba",
    "Brat Martin",
    "Magla",
    "Rosa",
    "Žito",
    "Zlatna grdobina",
    "Fina klopica",
    "Crna roda",
    "Ribički klub čaplja",
    "Stara taverna",
    "Marijina Tikvana"
]

jela = [
    ("Falafel", "Bob i slanutka", True, True, True),
    ("Purica s mlincima", "Purica i mlinci", True, True, False),
    ("Rižoto s plodovima mora", "Riža, lignje, maslinovo ulje", True, True, False),
    ("Odojak", "Svinja", False, False, False),
    ("Rižoto od cikle", "Riži, cikla, maslac", True, True, False),
    ("Janjetina ispod peke", "Janje", True, True, False),
    ("Kokošja juha", "Koka, povrće. voda", True, True, False),
    ("Čvaraci", "Salo od svinje", False, False, False),
    ("Lazanje", "Sir, mljeveno meso, tjesto", False, False, False),
    ("Teleća rolada", "Teletina, špek, krastavac", False, False, False),
]

imena = [
    "Ivan",
    "Josip",
    "Marko",
    "Luka",
    "Tomislav",
    "Stjepan",
    "Željko",
    "Ivica",
    "Ante",
    "Mario",
    "Marija",
    "Ana",
    "Ivana",
    "Mirjana",
    "Katarina",
    "Vesna",
    "Nada",
    "Marina",
    "Petra",
    "Martina"
]

prezimena = [
    "Knežević",
    "Horvat",
    "Kovačević",
    "Pavlović",
    "Blažević",
    "Božić",
    "Lovrić",
    "Babić",
    "Marković",
    "Bošnjak",
    "Grgić",
    "Brkić",
    "Filipović",
    "Vidović",
    "Kovačić",
    "Tomić",
    "Jukić",
    "Novak",
    "Martinović",
    "Petrović",
    "Mandić",
    "Šimunović",
    "Nikolić",
    "Jurković",
    "Lončar",
    "Barišić",
    "Živković",
    "Šimić",
    "Jurić",
    "Rukavina",
]

def generate_oib():
    return "".join([str(randrange(0,10)) for i in range(10)])

def select_random_element(l:list):
    return l[randrange(0, len(l))]

def generate_table(table_name:str, fields:tuple, values:set):
    out_str = f"INSERT INTO {table_name}{fields} VALUES\n"
    for value in values:
        out_str += str(value) + ",\n"
    out_str = out_str[:-2] + ";\n"
    return out_str

def random_date(begin: str, end: str) -> str:
    if end == "NULL":
        end = "31-12-2024"
    # Convert input strings to datetime objects
    begin_date = datetime.strptime(begin, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    if begin_date > end_date:
        raise ValueError("Begin date must be earlier than end date")
    
    delta = end_date - begin_date
    random_days = random.randint(0, delta.days)
    
    random_date = begin_date + timedelta(days=random_days)
    
    return random_date.strftime("%Y-%m-%d")


if __name__ == "__main__":
    #Generate people
    people = set()
    while len(people) != 50:
        people.add((generate_oib(), select_random_element(imena), select_random_element(prezimena)))
    print(generate_table("Osoba", ("oib", "ime", "prezime"), people))
    #Generate locations
    locations = set()
    while len(locations) != 12:
        locations.add(
                (generate_oib(), select_random_element(adrese), 
                 select_random_element(gradovi), drzava, randrange(10000,99999))
        )
    print(generate_table("Lokacija", ("id", "adresa", "grad", "drzava", "postanski_broj"), locations))
    #Generate Restorantes
    restorantes = set()
    while (len(restorantes) != 10):
        open_date = random_date("1-1-2001", "31-12-2024")
        end_date = "NULL"
        if randrange(2):
            end_date = random_date(open_date, "31-12-2024")
        restorantes.add(
                (generate_oib(), select_random_element(imena_restorana), 
                 open_date, end_date, randrange(1,5), randrange(3), select_random_element(list(locations))[0],
                 select_random_element(list(people))[0])
        )
    print(generate_table("Restoran", 
                         ("oib", "ime", "datum_otvaranja", 
                          "datum_zatvaranja", "google_recenzija", "michelin_zvjezdica", "lokacija_id", "vlasnik_oib"),
                         restorantes))
    #Generate Radni odnose
    work_relations = set()
    for restoran in restorantes:
        konobar = select_random_element(list(people))[0]
        while konobar == restoran[7]:
            konobar = select_random_element(list(people))[0]
        kuhar = select_random_element(list(people))[0]
        while kuhar == konobar and kuhar == restoran[7]:
            kuhar = select_random_element(list(people))[0]
        kuhar_begin_date = random_date(restoran[2], restoran[3])
        konobar_begin_date = random_date(restoran[2], restoran[3])
        work_relations.add((generate_oib(), konobar, restoran[0], "konobar", randrange(1000, 2000, 50), "eur",
                            kuhar_begin_date, restoran[3]))
        work_relations.add((generate_oib(), kuhar, restoran[0], "kuhar", randrange(1000, 2000, 50), "eur",
                            konobar_begin_date, restoran[3]))
    print(generate_table("Radni_odnos", 
        ("id", "oib_radnika", "oib_poslodavca", 
         "uloga", "plaća", "valuta", "početak_radnog_odnosa", "kraj_radnog_odnosa"), list(work_relations)))
    #Generate inspekcije
    inspekcije = set()
    inspektori = [select_random_element(list(people))[0], select_random_element(list(people))[0]]
    for inspektor in inspektori:
        for restoran in restorantes:
            restoran_id = restoran[0]
            inspekcije.add((random_date(restoran[2], restoran[3]), inspektor, randrange(1, 5)))
    print(generate_table("Inspekcija", ("datum", "oib_inspektora", "oib_restorana", "ocjena"), inspekcije))
    #Generate menu    
    jelovnik = set()
    for restoran in restorantes:
        jela_izabrana = [ select_random_element(list(jela)), select_random_element(list(jela)) ]
        for jelo in jela_izabrana:
            jelovnik.add(
                (generate_oib(), restoran[0], jelo[0], jelo[1], jelo[2], jelo[3], jelo[4])
            )
    print(generate_table("Jelo", 
            ("id", "oib_restorana", "naziv", "namirnice", "kosher", "halal", "vegan"),
            list(jelovnik)))

