-- 1. DATENBANK ERSTELLEN & NUTZEN
CREATE DATABASE IF NOT EXISTS KletterKompass;
USE KletterKompass;

-- 2. TABELLEN LÖSCHEN (Falls Reste existieren)
DROP TABLE IF EXISTS meldungen;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS spielplaetze;
DROP TABLE IF EXISTS nutzer;

-- 3. NUTZER-TABELLE (Exakt für deine App)
CREATE TABLE nutzer (
    nutzer_id INT PRIMARY KEY AUTO_INCREMENT,
    benutzername VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    passwort VARCHAR(255) NOT NULL,
    vorname VARCHAR(100),
    nachname VARCHAR(100),
    alter_wert INT,
    rolle VARCHAR(20) DEFAULT 'user',
    akzeptiert_agb BOOLEAN DEFAULT FALSE
);

-- 4. SPIELPLATZ-TABELLE (Mit Geo-Daten)
CREATE TABLE spielplaetze (
    spiel_id INT PRIMARY KEY AUTO_INCREMENT,
    standort VARCHAR(255) NOT NULL,
    ausstattung TEXT,
    altersfreigabe VARCHAR(50),
    lat DOUBLE NOT NULL,
    lon DOUBLE NOT NULL,
    auslastung INT DEFAULT 0
);

-- 5. FEEDBACK-TABELLE
CREATE TABLE feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    nutzer_id INT,
    nachricht TEXT,
    zeitstempel DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nutzer_id) REFERENCES nutzer(nutzer_id)
);

-- 6. MELDUNGEN-TABELLE (Crowdsourcing)
CREATE TABLE meldungen (
    melde_id INT PRIMARY KEY AUTO_INCREMENT,
    spiel_id INT,
    nutzer_id INT,
    grund TEXT,
    zeitpunkt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (spiel_id) REFERENCES spielplaetze(spiel_id),
    FOREIGN KEY (nutzer_id) REFERENCES nutzer(nutzer_id)
);


CREATE TABLE IF NOT EXISTS vorschlaege (
    vorschlag_id INT PRIMARY KEY AUTO_INCREMENT,
    nutzer_id INT,
    platz_name VARCHAR(255) NOT NULL,
    adresse VARCHAR(255) NOT NULL,
    kategorie ENUM('Spielplatz', 'Park', 'Freizeitpark') NOT NULL,
    ausstattung SET('Rutsche', 'Schaukel', 'Sandkasten', 'Seilbahn', 'Klettergerüst', 'Wasserspiel', 'Wippe', 'Karussell') DEFAULT NULL,
    bild BLOB,
    zeitstempel DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nutzer_id) REFERENCES nutzer(nutzer_id)
);






-- 7. DEINE 11 SPIELPLÄTZE EINFÜGEN
INSERT INTO spielplaetze (standort, ausstattung, altersfreigabe, lat, lon) VALUES
('Im Tulpengrund 7, Varel', 'Rutsche, Schaukel, Sandkasten', '0-12 Jahre', 53.3965, 8.1374),
('Waldstraße, Varel', 'Klettergerüst, Seilbahn', '6-14 Jahre', 53.3852, 8.1401),
('Dangast, Varel', 'Wasserspielplatz, Kletternetz', '2-12 Jahre', 53.4479, 8.1183),
('Brookmerlandring, Jever', 'Klettergerüst, Rutsche, Schaukel', '0-12 Jahre', 53.5714, 7.8921),
('Kleiner Moorweg, Jever', 'Doppelschaukel, Rodelhügel', '0-14 Jahre', 53.5785, 7.9150),
('Peter-Grave-Straße, Schortens', 'Lokomotive, Sandbereich, Schaukel', '0-10 Jahre', 53.5352, 7.9481),
('Breslauer Straße, Sande', 'Sportgeräte, Klettern', '6-14 Jahre', 53.5042, 8.0125),
('Heidebergstraße, Varel', 'Sandkasten, Seilreck, Kletternetz', '0-12 Jahre', 53.3950, 8.1420),
('Schlosspark Jever', 'Spazierwege, Teiche, Enten', 'Alle Altersgruppen', 53.5730, 7.9030),
('Kurpark Dangast, Varel', 'Meerblick, Grünflächen, Kunst', 'Alle Altersgruppen', 53.3820, 8.1150),
('Freizeitpark Dorf Wangerland', 'Indoor-Spielplatz, Fahrgeschäfte', '2-14 Jahre', 53.6660, 7.9550);

-- Tabellenerweiterung

-- 1. Bundesland zu den bestehenden Spielplätzen hinzufügen
ALTER TABLE spielplaetze ADD COLUMN bundesland VARCHAR(50) DEFAULT 'Niedersachsen';

-- 2. Bundesland zu den Vorschlägen hinzufügen
ALTER TABLE vorschlaege ADD COLUMN bundesland VARCHAR(50);

-- 3. Wegbeschreibung hinzufügen (falls Adresse unbekannt)
ALTER TABLE vorschlaege ADD COLUMN beschreibung TEXT;

-- Wir fügen eine Spalte hinzu, um die ID eines existierenden Platzes zu speichern
ALTER TABLE vorschlaege ADD COLUMN existierende_id INT DEFAULT NULL;

-- Wir fügen ein Feld für die Art der Meldung hinzu
ALTER TABLE vorschlaege ADD COLUMN melde_typ ENUM('Neu', 'Update') DEFAULT 'Neu';

-- 1. Emoji-Spalte zu den Nutzern hinzufügen
ALTER TABLE nutzer ADD COLUMN avatar_emoji VARCHAR(10) DEFAULT '👤';

USE KletterKompass;
-- Admin festlegen
UPDATE nutzer 
SET rolle = 'admin' 
WHERE benutzername = 'AdminChristian';
-- 1. Schutz kurz ausschalten
SET SQL_SAFE_UPDATES = 0;

-- 2. Die Tabelle leeren (Sicherer Schnitt für das neue Passwort-System)
USE KletterKompass;
DELETE FROM nutzer;

-- 3. Schutz wieder einschalten (für die Sicherheit deiner Daten)
SET SQL_SAFE_UPDATES = 1;


UPDATE nutzer SET rolle = 'admin' WHERE benutzername = 'AdminChristian';
