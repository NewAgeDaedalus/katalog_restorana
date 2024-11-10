import psycopg
import json
from datetime import datetime, timedelta

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
    def str_in_dict(self, attr:str, dic:dict, searchstr:str):
        cur_attr = attr.split(".")[0]
        if type(dic) == list:
            for elem in dic:
                ret =  self.str_in_dict(attr, elem, searchstr)
                if ret:
                    return ret
        if type(dic) == dict:
            if type(dic[cur_attr]) != list and type(dic[cur_attr]) != dict and searchstr in str(dic[cur_attr]):
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
    def fetch(self, args:dict=None):
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
        try:
            return self.fuzzy(restorani_json, args["fuzzy"])
        except KeyError:
            pass
        for attr, val in args.items():
            i = 0
            while i < len(restorani_json):
                restoran = restorani_json[i]
                if not self.str_in_dict(attr, restoran, val):
                    restorani_json.pop(i)
                    continue
                i+=1
        return restorani_json;


if __name__ == "__main__":
    fetcher = Restoran_fetcher()
    a = [{"1":str(1), "2":3}, "3"]
    print(fetcher.str_in_dict("2", a, "5"))
