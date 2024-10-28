#!/bin/bash
psql -d katalog_restorana -c "\copy (SELECT Restoran.oib, Restoran.ime, datum_otvaranja, datum_zatvaranja,
            google_recenzija, 
            michelin_zvjezdica, Osoba.oib as vlasnik_oib, Osoba.ime as vlasnik_ime, 
            Osoba.prezime as vlasnik_prezime,
            Inspektor.oib as inspektor_oib, Inspektor.ime as inspektor_ime,
            Radnik.oib as oib_radnik, Radnik.ime as radnik_ime, Radnik.prezime as radnik_prezime,
            plaća, valuta, početak_radnog_odnosa, kraj_radnog_odnosa,
            Jelo.naziv, Jelo.namirnice, Jelo.kosher, Jelo.halal, Jelo.vegan
        FROM Restoran
        JOIN Osoba on vlasnik_oib=Osoba.oib
        JOIN Radni_odnos on Restoran.oib=oib_poslodavca
        JOIN Jelo on Restoran.oib=Jelo.oib_restorana
        JOIN Lokacija on lokacija_id=Lokacija.id
        JOIN Inspekcija on Restoran.oib = Inspekcija.oib_restorana
        JOIN Osoba as Inspektor on Inspekcija.oib_inspektora=Inspektor.oib
        JOIN Osoba as Radnik on Radnik.oib=Radni_odnos.oib_radnika) 
    TO '${1}' DELIMITER ';' csv header;"
