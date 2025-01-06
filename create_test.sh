#!/bin/bash

curl -X POST 'http://127.0.0.1:5000/rest/api/restoran' -H "Content-Type: application/json" -d \
'
[
    {
        "ime": "neki restoran",
        "google_recenzija": 4,
        "datum_otvaranja": "2020-08-3",
        "datum_zatvaranja": "2022-09-1",
        "michelin_zvjezdica": 0,
        "inspekcije": [
            {
                "datum": "2020-09-10",
                "inspektor": {
                    "ime": "Damjan",
                    "prezime": "Brkić"
                },
                "ocjena": 5
            }
        ],
        "jelovnik": [
            {
                "halal": true,
                "kosher": false,
                "namirnice": "Sastojci1",
                "vegan": false,
                "naziv": "Jelo1"
            }
        ],
        "lokacija": {
            "adresa": "Brčićeva 1",
            "država": "Hrvatska",
            "grad": "Zagreb",
            "poštanski_broj": 10090
        },
        "radnici": [
            {
                "ime": "Svetko",
                "prezime": "Svetkić",
                "plaća": 300,
                "početak_radnog_odnosa": "2020-08-3",
                "kraj_radnog_odnosa": "2022-09-1",
                "uloga": "sve",
                "valuta": "eur"
            }
        ],
        "vlasnik": {
            "ime": "Marijan",
            "prezime": "Marijanović"
        }
    }
]
'
