#!/bin/bash

curl -X PUT 'http://127.0.0.1:5000/rest/api/restoran' -H "Content-Type: application/json" -d \
'
[
    {
        "oib":"9183961747",
        "ime": "Promijenjeno ime restorana",
        "inspekcije":[
            {
                "id": "1111111666",
                "ocjena":1,
                "inspektor": {
                    "ime": "Jozo",
                    "prezime": "Jozović"
                }
            },
            {
                "ocjena":2,
                "datum":"2020-5-6",
                "inspektor": {
                    "ime": "Fabian",
                    "prezime": "Novčić"
                }
            }
        ]
    }
]
'
