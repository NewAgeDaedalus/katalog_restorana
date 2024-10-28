# Katalog restorana

# Licencija
Katalog restorana by Fabian Penezić is marked with CC0 1.0 

Ovo je repozitorij za laboratorijske vježbe iz predmenta Otvorenog računarstva. Sadrži skup otvorenih
kataloških podataka restorana u Republici hrvatskoj.

## Preuzimanje
Podaci se preuzimaju s kloniranjem ovog repozitorija.

### Ovisnosti
* python3
* psycopg
* postgresql

### Stvaranje baze podataka
Logirajte se kao korisnik postgres.
``` bash
    su postgres
```
Zatim stvorite bazu podataka s naredbom.
``` bash
    psql -c "CREATE DATABASE katalog\_restorana OWNER [username];"
```
Nakon toga se od logirajte s postgres korisnika i stvorite tablice i napunite ih.
``` bash
    exit
    bash -d katalog\_restorana -f create\_relations.sql
    bash -d katalog\_restorana -f fill\_tables.sql
```

### Izvoz podataka

#### CSV format
'''bash
    ./export\_csv.sh [datoteka]
'''
#### Json format
'''bash
    python export\_to\_json.py "[korisnik baze podataka]" "[lozinka]"
'''

## Opis podataka
Baza podataka se sastoji od 6 tablica:
* Inspekcija
* Jelo
* Lokacija
* Osoba
* Radni\_odnos
* Restoran

### Restoran
|-----|-----|------------------|-------------------|------------------|----------------------|--------------|--------------|
| oib | ime | datum\_otvaranja | datum\_zatvaranja | google\_recenzija | michelin\_zvjezdica | lokacija\_id | vlasnik\_oib |
|-----|------|-----------------|-------------------|--------------------|---------------------|-------------|--------------|
| CHAR(10) | VARCHAR | DATE | DATE | INTEGER | INTEGER | CHAR(10) | CHAR(10) |

* oib - jedinstveni identifikator restorana
* ime - ime restorana
* datum\_otvaranja - datum kad otvaranja restorana za javnost, format YYYY-MM-DD
* datum\_zatvaranja - datum zatvaranje restorana, istog formata kao datum\_otvaranja, ako je vrijednost atributa NULL restoran još nije zatvoren
* lokacija\_id - vanjski ključ za tablicu Lokaciju, definira lokaciju restorana
* vlaksnik\_oib - vanjski ključ za tablicu Osoba, definira vlasnika restorana

### Osoba
|-----|-----|---------|
| oib | ime | prezime |
|-----|-----|---------|
| CHAR(10) | VARCHAR | VARCHAR |

* oib - jedinstveni identifikator osobe
* ime - ime osobe
* prezime - prezime osobe

### lokacija
|-----|-----|---------|-------|-----------------|
| id | adresa | grad | drzava | postanski\_broj |
|-----|-----|---------|-------|-----------------|
| CHAR(10) | VARCHAR | VARCHAR | VARCHAR | VARCHAR |

* id - jedinstveni identifikator lokacije
* adresa - adresa lokacije
* grad - grad u kojoj se lokacija nalazi
* drzava - drzava u kojoj se lokacija nalazi
* postanski\_broj

### Radni\_odnos
|-----|-----|----------|------|-----|----|------|-----|-------|------|
| id | oib\_radnika | oib\_poslodavca | uloga | plaća | valuta | početak\_radnog\_odnosa | kraj\_radnog\_odnosa |
|-----|-----|----------|------|-----|----|------|-----|-------|------|
| CHAR(10) | CHAR(10) | VARCHAR | VARCHAR | FLOAT | VARCHAR | DATE | DATE | 
 
 * id - jedinstveni identifikator radnog odnosa
 * oib\_radnika - vanjski ključ na tablicu Osoba, označava radnika koji je ušao radni odnosa
 * oib\_poslodavca - vanjski ključ na tablicu Restoran, označava restroran u kojem je radnik radi/o
 * uloga - uloga radnika koju je radnik odrađivao
 * plaća - iznos mjesećne plaće koji je radnik primao od poslodavca
 * valuta - valuta u kojoj radnik prima plaću
 * početak\_radnog\_odnosa - datum u formatu YYYY-MM-DD, kad je radnik stupio u radni odnos s poslodavcem
 * kraj\_radnog\_odnosa - datum u formatu YYYY-MM-DD, kad je radni odnos raskinut. Ako je vrijednost NULL, radni odnos je još na snazi

 ### Jelo
|-----|-----|----------|------|-----|-------|-------|-------|------|
| id | oib\_restorana | naziv | namirnice | kosher | halal | vegan |
|-----|-----|----------|------|-----|-------|-------|-------|------|
| CHAR(10) | CHAR(10) | VARCHAR | VARCHAR | BOOLEAN | BOOLEAN | BOOLEAN |

 * id - jedinstveni identifikator pojedinog jela
 * oib\_restorana - vansjki ključ na tablicu Restoran, identificira restoran koji ima ovo jelo u jelovniku
 * naziv - ime jela
 * namirnice - sastojci od kojeg je jelo sačinjeno

 ### Inspekcija 
 | datum | oib\_inspektora | oib\_restorana | ocjena |
 | DATE  | CHAR(10) |  CHAR(10) | INTEGER |

 * datum - datum formata YYYY-MM-DD kad je inspkcija izvršena
 * oib\_inspektora - vanjski ključ na tablicu Osoba, identificira inspektora koji je izvršio inspekciju
 * oib\_restorana - vanjski ključ na tablicu Restoran, identificira restoran nad kojim je provedena inspekcija
 * ocjena - ocjena inspekcije, od 1 do 5




