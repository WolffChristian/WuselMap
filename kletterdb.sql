-- 1. Datenbank erstellen und nutzen
CREATE DATABASE IF NOT EXISTS kletterdb;
USE kletterdb;

-- 2. Tabelle für die Spielplätze (Das Herzstück)
CREATE TABLE IF NOT EXISTS spielplaetze (
    id INT AUTO_INCREMENT PRIMARY KEY,
    standort VARCHAR(255) NOT NULL,
    lat DOUBLE NOT NULL,
    lon DOUBLE NOT NULL,
    altersfreigabe VARCHAR(100),
    bild_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabelle für die Nutzer (Login-System)
CREATE TABLE IF NOT EXISTS nutzer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    benutzername VARCHAR(100) UNIQUE NOT NULL,
    passwort VARCHAR(255) NOT NULL,
    rolle VARCHAR(50) DEFAULT 'user'
);

-- 4. Tabelle für neue Vorschläge (wenn Nutzer etwas melden)
CREATE TABLE IF NOT EXISTS vorschlaege (
    id INT AUTO_INCREMENT PRIMARY KEY,
    standort VARCHAR(255),
    adresse VARCHAR(255),
    altersfreigabe VARCHAR(100),
    status VARCHAR(50) DEFAULT 'offen',
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --- TESTDATEN EINFÜGEN ---

-- Ein erster Spielplatz in Varel
INSERT INTO spielplaetze (standort, lat, lon, altersfreigabe) 
VALUES ('Varel Testpark', 53.397, 8.138, '3-12 Jahre');

-- Ein Test-Admin (Passwort ist hier 'admin123' als Hash-Beispiel)
-- Hinweis: In der App nutzt du hash_passwort(), um echte Passwörter zu speichern
INSERT INTO nutzer (benutzername, passwort, rolle) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin');




USE kletterdb;
SET SQL_SAFE_UPDATES = 0;
DROP TABLE IF EXISTS nutzer;

CREATE TABLE nutzer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    benutzername VARCHAR(100) UNIQUE NOT NULL,
    passwort VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    vorname VARCHAR(100),
    nachname VARCHAR(100),
    alter_jahre INT,
    rolle VARCHAR(50) DEFAULT 'user',
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



USE kletterdb;
ALTER TABLE nutzer ADD COLUMN agb_akzeptiert BOOLEAN DEFAULT FALSE;

SET SQL_SAFE_UPDATES = 0;
USE kletterdb;

-- Falls du den Admin-User manuell anlegen willst:
INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_jahre, agb_akzeptiert, rolle)
VALUES ('AdminChristian', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Wolff2387@gmail.com', 'Christian', 'Wolff', 38, 1, 'admin')
ON DUPLICATE KEY UPDATE rolle='admin';


SET SQL_SAFE_UPDATES = 0;

UPDATE nutzer 
SET passwort = SHA2('19Lonkoncra19', 256) 
WHERE benutzername = 'AdminChristian';
SET SQL_SAFE_UPDATES = 1;


USE kletterdb;

-- 1. Tabelle für Vorschläge (Was Nutzer einsenden)
CREATE TABLE IF NOT EXISTS vorschlaege (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    adresse VARCHAR(255),
    alter_gruppe VARCHAR(100),
    eingereicht_von VARCHAR(100),
    status VARCHAR(50) DEFAULT 'offen',
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabelle für Bewertungen
CREATE TABLE IF NOT EXISTS bewertungen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spielplatz_id INT,
    nutzername VARCHAR(100),
    sterne INT,
    kommentar TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabelle für allgemeines Feedback zur App
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nutzername VARCHAR(100),
    nachricht TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
);


USE kletterdb;
ALTER TABLE nutzer ADD COLUMN profil_emoji VARCHAR(10) DEFAULT '🧗';

SET SQL_SAFE_UPDATES = 1;

-- Tabellen erweitern
ALTER TABLE spielplaetze 
ADD COLUMN bundesland VARCHAR(100), 
ADD COLUMN plz VARCHAR(10), 
ADD COLUMN stadt VARCHAR(100),
ADD COLUMN bild_data LONGTEXT;

ALTER TABLE vorschlaege 
ADD COLUMN bundesland VARCHAR(100), 
ADD COLUMN plz VARCHAR(10), 
ADD COLUMN stadt VARCHAR(100),
ADD COLUMN bild_data LONGTEXT;

USE kletterdb;
SET SQL_SAFE_UPDATES = 0;

-- Spalte für Foto-Datenschutz hinzufügen
ALTER TABLE vorschlaege ADD COLUMN foto_datenschutz BOOLEAN DEFAULT FALSE;
ALTER TABLE spielplaetze ADD COLUMN foto_datenschutz BOOLEAN DEFAULT FALSE;

SELECT * FROM nutzer;


-- Das stellt sicher, dass auch große Bilder gespeichert werden können
ALTER TABLE vorschlaege MODIFY COLUMN bild_data LONGTEXT;
ALTER TABLE spielplaetze MODIFY COLUMN bild_data LONGTEXT;

-- Tabellen-Struktur für Spielplätze
ALTER TABLE spielplaetze ADD COLUMN IF NOT EXISTS hat_wc BOOLEAN DEFAULT FALSE;

ALTER TABLE spielplaetze ADD COLUMN IF NOT EXISTS zuletzt_bestaetigt DATE;
ALTER TABLE spielplaetze MODIFY COLUMN bild_data LONGTEXT;

-- Tabellen-Struktur für Vorschläge
ALTER TABLE vorschlaege ADD COLUMN IF NOT EXISTS hat_wc BOOLEAN DEFAULT FALSE;
ALTER TABLE vorschlaege MODIFY COLUMN bild_data LONGTEXT;

UPDATE nutzer 
SET vorname = 'Sabrina', 
    nachname = 'Haase' 
WHERE benutzername = 'Biene';

UPDATE nutzer SET benutzername = LOWER(benutzername);

-- Reparatur der Spielplatz-Tabelle
ALTER TABLE spielplaetze MODIFY COLUMN bild_data LONGTEXT;
ALTER TABLE spielplaetze ADD COLUMN IF NOT EXISTS foto_datenschutz BOOLEAN DEFAULT TRUE;

-- Reparatur der Vorschlags-Tabelle
ALTER TABLE vorschlaege MODIFY COLUMN bild_data LONGTEXT;
ALTER TABLE vorschlaege ADD COLUMN IF NOT EXISTS foto_datenschutz BOOLEAN DEFAULT TRUE;

-- Sicherstellen, dass die Nutzer-Tabelle passt
ALTER TABLE nutzer MODIFY COLUMN profil_emoji VARCHAR(10) DEFAULT '🧗';


SELECT count(*) FROM vorschlaege;


CREATE TABLE nachrichten (
    id INT AUTO_INCREMENT PRIMARY KEY,
    von_nutzer VARCHAR(255),
    an_nutzer VARCHAR(255),
    nachricht TEXT,
    zeitpunkt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gelesen INT DEFAULT 0
);


CREATE TABLE freunde (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nutzer VARCHAR(255),
    freund VARCHAR(255),
    UNIQUE KEY unique_friendship (nutzer, freund)
    
);



ALTER TABLE freunde ADD COLUMN status VARCHAR(20) DEFAULT 'offen';


SELECT id, standort, stadt FROM spielplaetze WHERE standort LIKE '%Hochkamp%';
DELETE FROM spielplaetze WHERE id = 30002;


/* 1. Status-Spalte für Wartung hinzufügen */
ALTER TABLE spielplaetze ADD COLUMN status VARCHAR(20) DEFAULT 'aktiv';

/* 2. Tabelle für die Sterne-Bewertungen erstellen */
CREATE TABLE IF NOT EXISTS bewertungen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spot_id INT,
    nutzername VARCHAR(255),
    sterne INT,
    zeitstempel TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE spielplaetze ADD COLUMN status VARCHAR(20) DEFAULT 'aktiv';

CREATE TABLE IF NOT EXISTS bewertungen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spot_id INT,
    nutzername VARCHAR(255),
    sterne INT,
    zeitstempel TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_bewertung (spot_id, nutzername)
);


SELECT * from spielplaetze;

DELETE FROM spielplaetze 
WHERE id = 1;



ALTER TABLE nachrichten
ADD COLUMN recipient_id VARCHAR(255) DEFAULT 'GLOBAL',
ADD COLUMN is_private BOOLEAN DEFAULT FALSE;
-- Spalten für vorschlaege ergänzen
ALTER TABLE vorschlaege 
ADD COLUMN ausstattung TEXT, 
ADD COLUMN hat_schatten TINYINT(1) DEFAULT 0, 
ADD COLUMN hat_sitze TINYINT(1) DEFAULT 0;

-- Spalten für spielplaetze ergänzen
ALTER TABLE spielplaetze 
ADD COLUMN ausstattung TEXT, 
ADD COLUMN hat_schatten TINYINT(1) DEFAULT 0, 
ADD COLUMN hat_sitze TINYINT(1) DEFAULT 0;
ALTER TABLE nachrichten 
ADD COLUMN spot_name VARCHAR(255) DEFAULT 'Allgemein';
DELETE FROM nachrichten WHERE is_private = FALSE;
ALTER TABLE vorschlaege 
ADD COLUMN lat DECIMAL(10, 8), 
ADD COLUMN lon DECIMAL(11, 8);
-- Spalten für GPS und Ausstattung in beiden Tabellen
ALTER TABLE vorschlaege ADD COLUMN lat DECIMAL(10, 8), ADD COLUMN lon DECIMAL(11, 8), ADD COLUMN ausstattung TEXT, ADD COLUMN hat_schatten TINYINT(1), ADD COLUMN hat_sitze TINYINT(1);
ALTER TABLE spielplaetze ADD COLUMN lat DECIMAL(10, 8), ADD COLUMN lon DECIMAL(11, 8), ADD COLUMN ausstattung TEXT, ADD COLUMN hat_schatten TINYINT(1), ADD COLUMN hat_sitze TINYINT(1);

-- Spalte für den Funk (falls noch nicht geschehen)
ALTER TABLE nachrichten ADD COLUMN spot_name VARCHAR(255) DEFAULT 'Allgemein';
ALTER TABLE nutzer ADD COLUMN agb_version INT DEFAULT 1;
-- 2. Tabelle für Foto-Nachreichungen (damit sie nicht direkt live gehen)
CREATE TABLE IF NOT EXISTS foto_nachreichungen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spielplatz_id INT,
    bild_data LONGTEXT,
    nutzername VARCHAR(255),
    zeitpunkt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'neu'
);

ALTER TABLE spielplaetze ADD COLUMN adresse VARCHAR(255) AFTER Standort;
SELECT * FROM spielplaetze;

ALTER TABLE nutzer ADD COLUMN profilbild LONGTEXT;

ALTER TABLE spielplaetze ADD COLUMN hat_parkplatz TINYINT(1) DEFAULT 0;
ALTER TABLE vorschlaege ADD COLUMN hat_parkplatz TINYINT(1) DEFAULT 0;