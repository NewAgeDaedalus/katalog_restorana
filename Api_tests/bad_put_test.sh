#!/bin/bash

curl -X PUT 'http://127.0.0.1:5000/rest/api/restoran' -H "Content-Type: application/json" -d \
'
[
    {
        "oib":"9183961747",
        "ime": "neki neki drugi restoran",
        "michelin_zvjezdica": 1,
        "vlasnik":{
            "oib":"8230983394"
        },
        "nista":1
    }
]
'
