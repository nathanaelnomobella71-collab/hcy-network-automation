-- Schéma physique de données — Chapitre 2, Tableau 2.7.
-- Monté dans /docker-entrypoint-initdb.d/ (docker-compose.yml) : exécuté
-- automatiquement à la première initialisation du conteneur postgres-hcy.

CREATE TABLE IF NOT EXISTS equipments (
    id             SERIAL PRIMARY KEY,
    hostname       VARCHAR(100) NOT NULL,
    ip_address     VARCHAR(45)  NOT NULL UNIQUE,
    equipment_type VARCHAR(50)  NOT NULL,
    location       VARCHAR(100),
    status         VARCHAR(20)  NOT NULL DEFAULT 'UP',
    -- Extension au Tableau 2.7 : paramètres nécessaires à l'exécution réelle
    -- des stratégies de remédiation (Chapitre 3, 3.6.2), sans lesquels
    -- MacIsolationStrategy/FailoverRoutingStrategy ne sauraient quelle
    -- interface ou quelle passerelle utiliser pour cet équipement précis.
    interface       VARCHAR(50),
    backup_gateway  VARCHAR(45),
    -- Sous-réseau desservi par un routeur de distribution : permet à
    -- FailoverRoutingStrategy d'injecter une route ciblée plutôt qu'une
    -- route par défaut globale, nécessaire dès qu'il y a plusieurs routeurs
    -- de distribution (cf. strategies/failover_routing.py, corrigé après
    -- densification de la topologie).
    lan_subnet      VARCHAR(45)
);

CREATE TABLE IF NOT EXISTS incidents (
    id            SERIAL PRIMARY KEY,
    equipment_id  INT NOT NULL REFERENCES equipments(id),
    incident_type VARCHAR(50)  NOT NULL,
    severity      VARCHAR(20)  NOT NULL,
    detected_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved      BOOLEAN      NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS remediations (
    id               SERIAL PRIMARY KEY,
    incident_id      INT NOT NULL REFERENCES incidents(id),
    action_taken     VARCHAR(255) NOT NULL,
    execution_status VARCHAR(20)  NOT NULL,
    executed_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table users (nouveau) : porte l'authentification RBAC (RF-07, cf. 2.7.1).
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    login         VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'technician',
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_incidents_equipment_id ON incidents(equipment_id);
CREATE INDEX IF NOT EXISTS idx_incidents_detected_at ON incidents(detected_at);
CREATE INDEX IF NOT EXISTS idx_remediations_incident_id ON remediations(incident_id);

-- Inventaire de départ — topologie GNS3 densifiée, adaptée aux routeurs à
-- 2 ports (voir gns3-configs/00-README.md) : 1 routeur de cœur, 3 routeurs
-- de distribution reliés au cœur via un switch d'agrégation (sw-core, non
-- répertorié ici car purement L2, jamais ciblé par le moteur), 6
-- commutateurs d'accès avec port security, certains chaînés entre eux.
INSERT INTO equipments (hostname, ip_address, equipment_type, location, status, interface, backup_gateway, lan_subnet)
VALUES
    -- Cœur de réseau
    ('coeur-reseau',        '10.10.0.1',    'routeur_coeur',        'Datacenter HCY',     'UP', NULL, NULL, NULL),

    -- Routeurs de distribution (backbone partagé 10.10.0.0/24 via sw-core)
    ('routeur-urgences',    '192.168.20.1', 'routeur_distribution', 'Pavillon Urgences',  'UP', NULL, '10.10.0.3', '192.168.20.0/24'),
    ('routeur-secours',     '192.168.21.1', 'routeur_distribution', 'Datacenter HCY',      'UP', NULL, NULL, NULL),
    ('routeur-administration', '192.168.30.1', 'routeur_distribution', 'Bâtiment Administratif', 'UP', NULL, '10.10.0.3', '192.168.30.0/24'),

    -- Accès — département Urgences (derrière routeur-urgences, switch unique)
    ('sw-urgences',         '192.168.20.5', 'switch_acces', 'Pavillon Urgences',   'UP', 'FastEthernet0/1', NULL, NULL),

    -- Accès — département Médical secondaire (derrière routeur-secours, switches chaînés)
    ('sw-laboratoire',      '192.168.21.5', 'switch_acces', 'Laboratoire',         'UP', 'FastEthernet0/1', NULL, NULL),
    ('sw-imagerie',         '192.168.21.6', 'switch_acces', 'Imagerie médicale',   'UP', 'FastEthernet0/1', NULL, NULL),

    -- Accès — département Administratif (derrière routeur-administration, switches chaînés)
    ('sw-caisse',           '192.168.30.5', 'switch_acces', 'Caisse centrale',     'UP', 'FastEthernet0/1', NULL, NULL),
    ('sw-pharmacie',        '192.168.30.6', 'switch_acces', 'Pharmacie',           'UP', 'FastEthernet0/1', NULL, NULL),
    ('sw-administration',   '192.168.30.7', 'switch_acces', 'Bâtiment Administratif', 'UP', 'FastEthernet0/1', NULL, NULL),

    -- Serveur applicatif — Dossier Patient Informatisé (VPCS, cf. gns3-configs/11-dpi-server.txt).
    -- Enjeu central du mémoire (Introduction générale, 3.10.4) : sa
    -- joignabilité continue, y compris pendant une panne de routeur-urgences,
    -- est la preuve empirique de la continuité de service revendiquée.
    ('dpi-server',          '10.10.0.10',   'serveur_applicatif', 'Datacenter HCY', 'UP', NULL, NULL, NULL)
ON CONFLICT (ip_address) DO NOTHING;

