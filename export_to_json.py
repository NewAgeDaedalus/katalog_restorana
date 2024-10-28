import psycopg
import json
from sys import argv

def nadi_lokaciju(lokacija_id:str):
    lok = list(cur.execute(f"SELECT adresa, grad, drzava, postanski_broj FROM Lokacija WHERE id='{lokacija_id}';"))[0]
    return {
        "adresa": lok[0],
        "grad": lok[1],
        "drzava": lok[2],
        "postanski_broj": lok[3]
    }

def nadi_vlasnika(vlasnik_oib:str):
    vlas = list(cur.execute(f"SELECT oib, ime, prezime FROM Osoba WHERE oib='{vlasnik_oib}'"))[0]
    return {
        "oib": vlas[0],
        "ime": vlas[1],
        "prezime": vlas[2],
    }

def nadi_jelovnik(restoran_oib):
    jela_rows = list(cur.execute(f"SELECT naziv, namirnice, kosher, halal, vegan FROM jelo WHERE oib_restorana='{restoran_oib}'"))
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

def nadi_radnike(restoran_oib):
    radni_odnosi_rows = list(
    cur.execute(f"""
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

def nadi_inspekcije(restoran_oib):
    inspekcije_rows = list(
    cur.execute(f"""
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
                "inspektor":nadi_vlasnika(inspekcija[1]),
                "ocjena":inspekcija[2]
            }
        )
    return inspekcije

if __name__ == "__main__":
    conn = psycopg.connect(f"dbname=katalog_restorana user={argv[1]} password={argv[2]}")
    cur = conn.cursor()
    restorani = cur.execute("SELECT * FROM restoran;")
    restorani_json = []
    for rest in list(restorani):
        restorani_json.append( {
            "oib": rest[0],
            "ime": rest[1],
            "datum_otvaranja": str(rest[2]),
            "datum_zatvaranja": str(rest[3]),
            "google_recenzija": rest[4],
            "michelin_zvjezdica": rest[5],
            "lokacija": nadi_lokaciju(rest[6]),
            "vlasnik": nadi_vlasnika(rest[7]),
            "jelovnik": nadi_jelovnik(rest[0]),
            "radnici": nadi_radnike(rest[0]),
            "inspekcije": nadi_inspekcije(rest[0])
        })
    with open("restorani.json", "w") as out_file:
        json.dump(restorani_json, out_file)
