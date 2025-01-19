import psycopg
from psycopg.types.json import Jsonb 
import json
from datetime import datetime, timedelta
from random import randrange

class ChangeException(Exception):
    pass

class Restoran_fetcher:
    def __init__(self):
        self.conn = psycopg.connect(f"dbname=katalog_restorana")
        self.cur = self.conn.cursor()

    def nadi_lokaciju(self, lokacija_id:str):
        lok = list(self.cur.execute(f"SELECT adresa, grad, drzava, postanski_broj FROM Lokacija WHERE id='{lokacija_id}';"))[0]
        return {
            "adresa": lok[0],
            "grad": lok[1],
            "drzava": lok[2],
            "postanski_broj": lok[3]
        }

    def nadi_vlasnika(self, vlasnik_oib:str):
        vlas = list(self.cur.execute(f"SELECT oib, ime, prezime FROM Osoba WHERE oib='{vlasnik_oib}'"))[0]
        return {
            "oib": vlas[0],
            "ime": vlas[1],
            "prezime": vlas[2],
        }

    def nadi_jelovnik(self, restoran_oib):
        jela_rows = list(self.cur.execute(f"SELECT naziv, namirnice, kosher, halal, vegan FROM jelo WHERE oib_restorana='{restoran_oib}'"))
        jelovnik = []
        for jelo in jela_rows:
            jelovnik.append(
                {
                    "naziv": jelo[0],
                    "namirnice": jelo[1],
                    "kosher": jelo[2],
                    "halal": jelo[3],
                    "vegan": jelo[4]
                }
            )
        return jelovnik

    def nadi_radnike(self, restoran_oib):
        radni_odnosi_rows = list(
            self.cur.execute(f"""
                 SELECT Osoba.oib, Osoba.ime, Osoba.prezime, uloga, plaća, valuta, 
                        početak_radnog_odnosa, kraj_radnog_odnosa
                        FROM Radni_odnos 
                        JOIN Osoba ON oib_radnika=Osoba.oib
                        JOIN Restoran ON oib_poslodavca=Restoran.oib
                        WHERE oib_poslodavca='{restoran_oib}'
                        """
                )
        )
        radnici = []
        for radni_odnos in radni_odnosi_rows:
            radnici.append(
                {
                    "oib":radni_odnos[0],
                    "ime":radni_odnos[1],
                    "prezime":radni_odnos[2],
                    "uloga": radni_odnos[3],
                    "plaća": radni_odnos[4],
                    "valuta": radni_odnos[5],
                    "početak_radnog_odnosa": str(radni_odnos[6]),
                    "kraj_radnog_odnosa": str(radni_odnos[7])
                }
            )
        return radnici

    def nadi_inspekcije(self, restoran_oib):
        inspekcije_rows = list(
            self.cur.execute(f"""
                 SELECT datum, oib_inspektora, ocjena
                        FROM Inspekcija 
                        WHERE oib_restorana='{restoran_oib}'
                        """
                )
        )
        inspekcije = []
        for inspekcija in inspekcije_rows:
            inspekcije.append(
                {
                    "datum": str(inspekcija[0]),
                    "inspektor":self.nadi_vlasnika(inspekcija[1]),
                    "ocjena":inspekcija[2]
                }
            )
        return inspekcije
    
    def close(self):
        self.cur.close()

    def fuzzy(self, restorani:list, searchstr:str):
        cstr = lambda l: list(map(lambda elem: str(elem), l))
        filtered_restorani = []
        for restoran in restorani:
            if searchstr in str(restoran["oib"]):
                filtered_restorani.append(restoran)
            elif searchstr in str(restoran["ime"]):
                filtered_restorani.append(restoran)
            elif searchstr in str(restoran["datum_otvaranja"]):
                filtered_restorani.append(restoran)
            elif searchstr in str(restoran["datum_zatvaranja"]):
                filtered_restorani.append(restoran)
            elif searchstr in str(restoran["google_recenzija"]):
                filtered_restorani.append(restoran)
            elif searchstr in str(restoran["michelin_zvjezdica"]):
                filtered_restorani.append(restoran)
            elif searchstr in "|".join(restoran["lokacija"].values()):
                filtered_restorani.append(restoran)
            elif searchstr in "|".join(restoran["vlasnik"].values()):
                filtered_restorani.append(restoran)
            elif searchstr in "|".join(list(map(lambda jelo: "|".join(cstr(jelo.values())), restoran["jelovnik"]))):
                filtered_restorani.append(restoran)
            elif searchstr in "|".join(list(map(lambda radnik: "|".join(cstr(radnik.values())), restoran["radnici"]))):
                filtered_restorani.append(restoran)
            elif searchstr in "|".join(list(map(lambda inspekcija: "|".join(cstr(inspekcija.values())), restoran["inspekcije"]))):
                filtered_restorani.append(restoran)
        return filtered_restorani

    # Critical, overcomplicated
    def str_in_dict(self, attr:str, dic:dict, searchstr:str, fuzzy=True):
        cur_attr = attr.split(".")[0]
        if type(dic) == list:
            for elem in dic:
                ret =  self.str_in_dict(attr, elem, searchstr)
                if ret:
                    return ret
        if type(dic) == dict:
            if (type(dic[cur_attr]) != list and type(dic[cur_attr]) != dict and 
                    (fuzzy and searchstr in str(dic[cur_attr])) or (not fuzzy and searchstr==str(dic[cur_attr]))):
                return True
            if type(dic[cur_attr]) == list:
                for elem in dic[cur_attr]:
                    ret =  self.str_in_dict(".".join(attr.split(".")[1:]), elem, searchstr)
                    if ret:
                        return ret
            if type(dic[cur_attr]) == dict:
                    ret =  self.str_in_dict(".".join(attr.split(".")[1:]), dic[cur_attr], searchstr)
                    if ret:
                        return ret
        return False

    # @params
    def fetch(self, args:dict=None, fuzzy:bool=True):
        restorani = self.cur.execute("SELECT * FROM restoran;")
        restorani_json = []
        for rest in list(restorani):
                restorani_json.append( {
                    "oib": rest[0],
                    "ime": rest[1],
                    "datum_otvaranja": str(rest[2]),
                    "datum_zatvaranja": str(rest[3]),
                    "google_recenzija": rest[4],
                    "michelin_zvjezdica": rest[5],
                    "lokacija": self.nadi_lokaciju(rest[6]),
                    "vlasnik": self.nadi_vlasnika(rest[7]),
                    "jelovnik": self.nadi_jelovnik(rest[0]),
                    "radnici": self.nadi_radnike(rest[0]),
                    "inspekcije": self.nadi_inspekcije(rest[0])
                })
        if args == None:
            return restorani_json

        for attr, val in args.items():
            i = 0
            while i < len(restorani_json):
                restoran = restorani_json[i]
                print(restoran["oib"])
                if not self.str_in_dict(attr, restoran, val, fuzzy=fuzzy):
                    restorani_json.pop(i)
                    continue
                i+=1
        return restorani_json;

class Restoran_manager:
    def __init__(self):
        self.conn = psycopg.connect(f"dbname=katalog_restorana")
        self.cur = self.conn.cursor()

    def create_restoran_row(self, rest:dict, lokacija_id:str, vlanik_oib:str):
        return [
                 "".join([str(randrange(0,10)) for i in range(10)]),
                 rest["ime"],
                 rest["datum_otvaranja"],
                 rest["datum_zatvaranja"],
                 rest["google_recenzija"],
                 rest["michelin_zvjezdica"],
                 lokacija_id,
                 vlanik_oib
        ]

    def create_osoba_row(self, osoba):
        return [
                 "".join([str(randrange(0,10)) for i in range(10)]),
                 osoba["ime"],
                 osoba["prezime"]
        ]

    def create_lokacija_row(self, lokacija):
        return [
                 "".join([str(randrange(0,10)) for i in range(10)]),
                 lokacija["adresa"],
                 lokacija["grad"],
                 lokacija["država"],
                 lokacija["postanski_broj"]
        ]

    def create_jelo_row(self, jelo, oib_restorana):
        return [
                 "".join([str(randrange(0,10)) for i in range(10)]),
                 oib_restorana,
                 jelo["naziv"],
                 jelo["namirnice"],
                 jelo["kosher"],
                 jelo["halal"],
                 jelo["vegan"]
        ]
    def create_radni_odnos_row(self, radnik, oib_restorana, oib_radnika):
        return [
                "".join([str(randrange(0,10)) for i in range(10)]),
                oib_radnika,
                oib_restorana,
                radnik["uloga"],
                radnik["plaća"],
                radnik["valuta"],
                radnik["početak_radnog_odnosa"],
                radnik["kraj_radnog_odnosa"]
        ]

    def create_inspkecija_row(self, inspekcija, oib_restorana, oib_inspektora):
        return [
                "".join([str(randrange(0,10)) for i in range(10)]),
                oib_restorana,
                inspekcija["datum"],
                oib_inspektora,
                inspekcija["ocjena"]
        ]


    def create_restoran(self, rest:dict):
        #Create people
        owner = self.create_osoba_row(rest["vlasnik"])
        inspektori = [self.create_osoba_row(obj["inspektor"]) for obj in rest["inspekcije"]]
        radnici = [self.create_osoba_row(obj) for obj in rest["radnici"]]
        for osoba in [owner]+inspektori+radnici:
            print()
            print(osoba)
            print()
            self.cur.execute("INSERT INTO OSOBA VALUES (%s, %s, %s)", osoba)
        #Create location
        location = self.create_lokacija_row(rest["lokacija"])
        print(location)
        self.cur.execute("INSERT INTO Lokacija VALUES (%s, %s, %s, %s, %s)", location)
        #Create Restoran
        restoran = self.create_restoran_row(rest, location[0], owner[0])
        self.cur.execute("INSERT INTO restoran VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", restoran)
        #Create Jelovnik
        jela = [self.create_jelo_row(jelo, restoran[0]) for jelo in rest["jelovnik"]]
        print(jela)
        for jelo in jela:
            self.cur.execute("INSERT INTO jelo VALUES (%s, %s, %s, %s, %s, %s, %s)", jelo)
        #Create Inspekcije
        inspekcije = [
                self.create_inspkecija_row(inspekcija, restoran[0], inspektor[0]) 
                for inspekcija, inspektor in zip(rest["inspekcije"], inspektori)
        ]
        for inspekcija in inspekcije:
            print(inspekcija)
            self.cur.execute("INSERT INTO inspekcija VALUES (%s, %s, %s, %s, %s)", inspekcija)
        #Create radni odnosi
        radni_odnosi = [ 
                        self.create_radni_odnos_row(radnik, restoran[0], radnik_oib[0]) 
                        for radnik, radnik_oib in zip(rest["radnici"], radnici)
        ]
        for radni_odnos in radni_odnosi:
            self.cur.execute("INSERT INTO radni_odnos VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", radni_odnos)
        self.conn.commit()

    def create_restorani(self, restorani:list):
        i = 0
        failed = []
        for restoran in restorani:
            try:
                self.create_restoran(restoran)
            except:
                failed += i
            i+=1
        return failed

    def change_vlasnik(self, novi_vlasnik, restoran_oib):
        self.cur.execute(f"SELECT vlasnik_oib from restoran where oib='{restoran_oib}'")
        stari_vlasnik_oib = self.cur.fetchone()[0]
        #Ako nema oib stvori novog
        if not "oib" in novi_vlasnik.keys():
            if "ime" not in novi_vlasnik.keys() and "prezime" not in novi_vlasnik.keys():
                raise  ChangeException("Novi vlasnik ne sadrži ime ili prezime")
            novi_vlasnik_oib = "".join([str(randrange(0,10)) for i in range(10)])
            self.curs.execute(
                    "INSERT INTO osobe VALUES (%s, %s, %s)", 
                    [
                        novi_vlasnik_oib,
                        novi_vlasnik["ime"],
                        novi_vlasnik["prezime"]
                    ]
            )
            self.curs.execute(f"UPDATE restorani SET vlasnik_oib = '{novi_vlasnik_oib}' WHERE oib = '{restoran_oib}'")
        #Ako ima je oib jednak starom, promijeni ime i prezime starog vlasnika
        elif novi_vlasnik["oib"] == stari_vlasnik_oib:
            if "ime" in novi_vlasnik.keys():
                self.curs.execute(f"UPDATE osoba SET ime = '{novi_vlasnik["ime"]}' WHERE oib = '{stari_vlasnik_oib}'")
            if "prezime" in novi_vlasnik.keys():
                self.curs.execute(f"UPDATE osoba SET prezime = '{novi_vlasnik["prezime"]}' WHERE oib = '{stari_vlasnik_oib}'")
        else:
            print(f"Mijenjam vlasnika na {novi_vlasnik['oib']}")
            self.cur.execute(f"SELECT * from osoba where oib='{novi_vlasnik['oib']}'")
            if self.cur.fetchone() == None:
                raise ChangeException(f"Ne postoji osoba s oibom '{novi_vlasnik['oib']}'")
            self.cur.execute(f"UPDATE restoran SET vlasnik_oib='{novi_vlasnik["oib"]}' WHERE oib='{restoran_oib}'")
            

    def change_inspekcije(self, inspekcije:list, oib_restorana:str):
        for inspekcija in inspekcije:
            if "id" in inspekcija.keys():
                self.cur.execute(f"SELECT id from inspekcija where id='{inspekcija['id']}'")
                inspekcija_id = self.cur.fetchone()
                if inspekcija_id == None:
                    raise ChangeException(f"Ne postoji inspekcija s ID-om {inspekcija['id']}")
                inspekcija_id = inspekcija_id[0]
                for key in set(inspekcija.keys()).intersection(["datum", "ocjena"]):
                    self.cur.execute(f"UPDATE inspekcija SET {key} = '{inspekcija[key]}' WHERE id = '{inspekcija_id}'")
            else: #stvori novu inspekciju
                if "inspektor" not in inspekcija.keys():
                    raise ChangeException("Nova inspekcija ne sadrži inpektora")
                inspektor = inspekcija["inspektor"]
                id_nove_inspekcije = "".join([str(randrange(0,10)) for i in range(10)])
                if "oib" not in inspektor.keys():
                    #stvori novog inspektora
                    if "ime" not in inspektor.keys() or "prezime" not in inspektor.keys():
                        raise ChangeException("Novi inspektor mora imati ime i prezime")
                    oib_novog_inspektora = "".join([str(randrange(0,10)) for i in range(10)])

                    print([oib_novog_inspektora, inspektor["ime"], inspektor["prezime"]])
                    self.cur.execute(
                            "INSERT INTO osoba VALUES (%s, %s, %s)", 
                            [oib_novog_inspektora, inspektor["ime"], inspektor["prezime"]]
                    )
                    if "datum" not in inspekcija.keys() and "ocjena" not in inspekcija.keys():
                        raise ChangeException("Nova inspekcija mora sadržavati datum i ocjenu")
                    self.cur.execute(
                            "INSERT INTO inspekcija VALUES (%s, %s, %s, %s, %s)",
                            [id_nove_inspekcije, oib_restorana, inspekcija["datum"], oib_novog_inspektora, inspekcija["ocjena"]]
                    )
                else:
                    self.cur.execute(f"SELECT oib from osoba where oib='{inspektor['oib']}'")
                    if self.cur.fetchone() == None:
                        raise ChangeException(f"Ne postoji inspektor s oibom {inspektor['oib']}")
                    if "datum" not in inspekcija.keys() and "ocjena" not in inspekcija.keys():
                        raise ChangeException("Nova inspekcija mora sadržavati datum i ocjenu")
                    self.cur.execute(
                            "INSERT INTO inspekcija VALUES (%s %s %s %s %s)",
                            [
                                id_nove_inspekcije, 
                                oib_restorana,
                                inspekcija["datum"],
                                inspektor["oib"],
                                inspekcija["ocjena"]
                            ]
                    )


    def change_radni_odnosi(self, radni_odnosi:list, oib_poslodavca):
        for radni_odnos in radni_odnosi:
            if "id" in radni_odnos.keys():
                self.curs.execute("SELECT id from radni_odnos where id='{radni_odnos['id']}'")
                radni_odnos_id = self.cur.fetchone()
                if radni_odnos_id == None:
                    raise ChangeException(f"Ne postoji inspekcija s ID-om {inspekcija['id']}")
                radni_odnos_id = radni_odnos_id[0]
                for key in set(inspekcija.keys()).intersection(
                        ["uloga", "plaća", "valuta", "početak_radnog_odnosa", "kraj_radnog_odnosa"]
                        ):
                    self.curs.execute(f"UPDATE radni_odnos SET {key} = '{radni_odnos['key']}' WHERE cd = {radni_odnos_id}")
            else: #stvori novi radni odnos
                #Provijeri je li ima sve potrebne elemente
                if len(set(radni_odnos.keys()).intersection(
                        set(["uloga", "plaća", "valuta", "početak_radnog_odnosa"]))) != 5 :
                    raise ChangeException("Za Dodavanje novog radnog odnosa elementi radnici moraju imati polja (oib_poslodavca, uloga, plaća, valuta, početak_radnog_odnosa)")
                id_novog_radnog_odnosa = "".join([str(randrange(0,10)) for i in range(10)])
                #Provijeri je li postoji
                if "oib_radnika" in radni_odnos.keys():
                    # Provijeri je li postoji oib te osobe
                    self.cur.execute(f"SELECT oib from osoba where oib='{radni_odnos['oib_radnika']}'")
                    if self.cur.fetchone() == None:
                        raise ChangeException(f"Ne postoji osoba s oibom '{radni_odnos['oib_radnika']}'")
                    self.cur.execute("INSERT INTO radni_odnos VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                     id_novog_radnog_odnosa, radni_odnos['oib_radnika'], oib_poslodavca,
                                     radni_odnos['uloga'], radni_odnos['plaća'], radni_odnos['valuta'],
                                     radni_odnos['početak_radnog_odnosa'], radni_odnos['kraj_radnog_odnosa'])
                else:
                    # Stvori novu osobu radnika
                    if "ime" not in radni_odnos.keys() or "prezime" not in radni_odnos.keys():
                        raise ChangeException("Novi radni odnos ne sadrži ime i prezime novog radnika")
                    novi_radnik_oib = "".join([str(randrange(0,10)) for i in range(10)])
                    self.cur.execute("INSERT INTO osoba VALUES (%s %s %s)", 
                                     novi_radnik_oib, radni_odnos['ime'], radni_odnos['prezime']
                    )
                    #Stvori novi radni_odnos
                    self.cur.execute("INSERT INTO radni_odnos VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                     id_novog_radnog_odnosa, novi_radnik_oib, oib_poslodavca,
                                     radni_odnos['uloga'], radni_odnos['plaća'], radni_odnos['valuta'],
                                     radni_odnos['početak_radnog_odnosa'], radni_odnos['kraj_radnog_odnosa']
                    )


    def change_lokacija(self, lokacija:dict, restoran_oib:str):
        try:
            novi_id = "".join([str(randrange(0,10)) for i in range(10)])
            self.cur.execute(
                    "INSERT INTO Lokacija VALUES (%s, %s, %s, %s, %s)",
                    [
                        novi_id,
                        lokacija["adresa"],
                        lokacija["grad"],
                        lokacija["drzava"],
                        lokacija["postanski_broj"]
                    ]
            )
            self.cur.execute(f"UPDATE restoran SET lokacija_id='{novi_id}' where oib='{restoran_oib}'")
        except KeyError:
            raise ChangeException("Atribut lokacija ne sadrži sve potrebne ključeve (adresa, grad, drzava, postanki_broj)")

    def update_restoran(self, restoran:dict):
        self.cur.execute(f"SELECT oib FROM restoran where oib='{restoran['oib']}'")
        original_restoran_id = self.cur.fetchone()
        if original_restoran_id == None:
            raise ChangeException(f"Ne postoji restoran s OIB-om '{restoran['oib']}'")
        original_restoran_id = original_restoran_id[0]
        for key in restoran.keys():
            if key == "oib":
                continue
            elif key == "vlasnik":
                self.change_vlasnik(restoran["vlasnik"], restoran["oib"])
            elif key == "radici":
                self.change_radni_odnosi(restoran["radnici"])
            elif key == "lokacija":
                self.change_lokacija(restoran["lokacija"], original_restoran_id)
            elif key == "inspekcije":
                self.change_inspekcije(restoran["inspekcije"], original_restoran_id)
            elif key in set(["ime", "datum_otvaranja", "datum_zatvaranja", "google_recenzija", "michelin_zvjezdica"]):
                self.cur.execute(f"UPDATE restoran SET {key}='{restoran[key]}' WHERE oib='{original_restoran_id}'")
            else:
                raise ChangeException(f"Objekt sadrži element '{key}' koji nije dopušten.")

    def update_restorani(self, restorani:list):
        restoran_indx = 0
        for restoran in restorani:
            try:
                self.update_restoran(restoran)
            except ChangeException as e:
                return restoran_indx, str(e)
            restoran_indx += 1
        self.conn.commit()
        return None, None

    def delete_restoran(self, restoran_oib):
        self.cur.execute(f"SELECT oib FROM restoran where oib='{restoran_oib}'")
        original_restoran_id = self.cur.fetchone()[0]
        if original_restoran_id == None:
            raise ChangeException(f"Restoran koji pokušavate izbrisati ne postoji")
        self.cur.execute(f"DELETE FROM restoran WHERE oib='{restoran_oib}'")
        self.conn.commit()
        
        

if __name__ == "__main__":
    fetcher = Restoran_fetcher()
    a = [{"1":str(1), "2":3}, "3"]
    print(fetcher.str_in_dict("2", a, "5"))
