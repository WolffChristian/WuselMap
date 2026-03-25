INSERT INTO spielplaetze (standort, ausstattung, altersfreigabe) VALUES
('Im Tulpengrund 7, Varel', 'Rutsche, Schaukel, Sandkasten', '0-12 Jahre'),
('Waldstraße, Varel', 'Klettergerüst, Seilbahn', '6-14 Jahre'),
('Dangast, Varel', 'Wasserspielplatz, Kletternetz', '2-12 Jahre');

INSERT INTO nutzer (benutzername, email, passwort) VALUES
('KletterMax', 'max@test.de', 'passwort123'),
('SpielPlatzHeldin', 'heldin@test.de', 'geheim456');

INSERT INTO bewertungen (sterne, kommentar, nutzer_id, spiel_id) VALUES 
(3, 'abgenutzt', 1, 1),
(4, 'macht spaß', 2, 3);

INSERT INTO termine (titel, zeitpunkt, nutzer_id, spiel_id) VALUES
('Klettern am Wochenende', '2026-04-04 14:00:00', 1, 2),
('Sandburg bauen', '2026-04-05 10:30:00', 2, 1);


INSERT INTO spielplaetze (standort, ausstattung, altersfreigabe, lat, lon) VALUES
('Brookmerlandring, Jever', 'Klettergerüst, Rutsche, Schaukel', '0-12 Jahre', 53.5714, 7.8921),
('Kleiner Moorweg, Jever', 'Doppelschaukel, Rodelhügel', '0-14 Jahre', 53.5785, 7.9150),
('Peter-Grave-Straße, Schortens', 'Lokomotive, Sandbereich, Schaukel', '0-10 Jahre', 53.5352, 7.9481),
('Breslauer Straße, Sande', 'Sportgeräte, Klettern', '6-14 Jahre', 53.5042, 8.0125),
('Heidebergstraße, Varel', 'Sandkasten, Seilreck, Kletternetz', '0-12 Jahre', 53.3950, 8.1420);



SELECT * FROM spielplaetze;


ALTER TABLE spielplaetze ADD lat DECIMAL(9,6);
ALTER TABLE spielplaetze ADD lon DECIMAL(9,6);

UPDATE spielplaetze SET lat = 53.3965, lon = 8.1374 WHERE spiel_id = 1;
UPDATE spielplaetze SET lat = 53.3852, lon = 8.1401 WHERE spiel_id = 2;
UPDATE spielplaetze SET lat = 53.4479, lon = 8.1183 WHERE spiel_id = 3;


INSERT INTO spielplaetze (standort, ausstattung, altersfreigabe, lat, lon, kategorie) VALUES
('Schlosspark Jever', 'Spazierwege, Teiche, Enten', 'Alle Altersgruppen', 53.5730, 7.9030, 'Park'),
('Kurpark Dangast, Varel', 'Meerblick, Grünflächen, Kunst', 'Alle Altersgruppen', 53.3820, 8.1150, 'Park'),
('Freizeitpark Dorf Wangerland', 'Indoor-Spielplatz, Fahrgeschäfte', '2-14 Jahre', 53.6660, 7.9550, 'Freizeitpark');




-- 1. Neuen Orten einen Status geben (standardmäßig 'ausstehend')
ALTER TABLE spielplaetze ADD COLUMN status VARCHAR(20) DEFAULT 'ausstehend';

-- Alle bisherigen 11 Plätze auf 'freigegeben' setzen, damit sie sichtbar bleiben
UPDATE spielplaetze SET status = 'freigegeben' WHERE spiel_id > 0;

-- 2. Nutzern eine Rolle geben (admin oder user)
ALTER TABLE nutzer ADD COLUMN rolle VARCHAR(20) DEFAULT 'user';

-- Dich selbst (oder den Account 'Entwickler') zum Admin machen
UPDATE nutzer SET rolle = 'admin' WHERE benutzername = 'Entwickler';

ALTER TABLE spielplaetze ADD COLUMN webseite VARCHAR(255);

ALTER TABLE spielplaetze 
ADD COLUMN auslastung VARCHAR(50) DEFAULT 'Unbekannt',
ADD COLUMN letztes_update DATETIME;


ALTER TABLE nutzer 
ADD COLUMN vorname VARCHAR(100),
ADD COLUMN nachname VARCHAR(100),
ADD COLUMN alter_wert INT,
ADD COLUMN geschlecht VARCHAR(20),
ADD COLUMN akzeptiert_agb BOOLEAN DEFAULT FALSE;