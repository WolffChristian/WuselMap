CREATE DATABASE Kletter_Kompass;

USE Kletter_Kompass;

CREATE TABLE spielplaetze (
    spiel_id INT PRIMARY KEY AUTO_INCREMENT,
    standort VARCHAR(75) NOT NULL,
    ausstattung VARCHAR(255),
    altersfreigabe VARCHAR(20) NOT NULL
);

CREATE TABLE nutzer (
    nutzer_id INT PRIMARY KEY AUTO_INCREMENT,
    benutzername VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    passwort VARCHAR(255) NOT NULL
);


CREATE TABLE bewertungen (
    bewertung_id INT PRIMARY KEY AUTO_INCREMENT,
    sterne TINYINT UNSIGNED,
    kommentar VARCHAR(255),
    nutzer_id INT,
    spiel_id INT,
    FOREIGN KEY (nutzer_id) REFERENCES nutzer(nutzer_id),
    FOREIGN KEY (spiel_id) REFERENCES spielplaetze(spiel_id)
);

CREATE TABLE termine (
    termin_id INT PRIMARY KEY AUTO_INCREMENT,
    titel VARCHAR(75),
    zeitpunkt DATETIME,
    nutzer_id INT,
    spiel_id INT,
    FOREIGN KEY (nutzer_id) REFERENCES nutzer(nutzer_id),
    FOREIGN KEY (spiel_id) REFERENCES spielplaetze(spiel_id));
    



ALTER TABLE nutzer ADD UNIQUE (benutzername);



