CREATE TABLE Osoba(
    oib CHAR(10),
    ime VARCHAR,
    prezime VARCHAR,
    PRIMARY KEY(oib)
);

CREATE TABLE Lokacija(
    id CHAR(10),
    adresa VARCHAR,
    grad VARCHAR,
    drzava VARCHAR,
    postanski_broj VARCHAR,
    PRIMARY KEY(id)
);

CREATE TABLE Restoran(
    oib CHAR(10),
    ime VARCHAR,
    datum_otvaranja DATE,
    datum_zatvaranja DATE,
    google_recenzija INTEGER,
    michelin_zvjezdica INTEGER,
    lokacija_id char(10),
    vlasnik_oib char(10),
    PRIMARY KEY(oib),
    FOREIGN KEY(lokacija_id) REFERENCES Lokacija(id),
    FOREIGN KEY(vlasnik_oib) REFERENCES Osoba(oib)
);

CREATE TABLE Radni_odnos(
    id VARCHAR,
    oib_radnika VARCHAR,
    oib_poslodavca VARCHAR,
    uloga VARCHAR,
    plaća FLOAT,
    valuta VARCHAR,
    početak_radnog_odnosa DATE,
    kraj_radnog_odnosa DATE,
    PRIMARY KEY(id),
    FOREIGN KEY(oib_radnika) REFERENCES Osoba(oib),
    FOREIGN KEY(oib_poslodavca) REFERENCES Restoran(oib)
);

CREATE TABLE Inspekcija(
    datum DATE,
    oib_inspektora CHAR(10),
    oib_restorana CHAR(10),
    ocjena INTEGER,
    PRIMARY KEY(datum, oib_restorana),
    FOREIGN KEY(oib_inspektora) REFERENCES Osoba(oib)
);

CREATE TABLE Jelo(
    id CHAR(10),
    oib_restorana CHAR(10),
    naziv VARCHAR,
    namirnice VARCHAR,
    kosher BOOLEAN,
    halal BOOLEAN,
    vegan BOOLEAN,
    PRIMARY KEY(id),
    FOREIGN KEY(oib_restorana) REFERENCES Restoran(oib)
);

