# HCY Network Automation

Système d'automatisation, de diagnostic et de remédiation réseau pour
l'Hôpital Central de Yaoundé — code source correspondant au mémoire
*Conception et mise en œuvre d'une solution de diagnostic et remédiation
automatisés du réseau informatique : cas de l'Hôpital Central de Yaoundé*
(Chapitres 2 et 3).

Chaque module référence explicitement, dans sa docstring, la section du
mémoire et/ou l'extrait de code dont il est la traduction (ex. « Extrait
3.3 », « Tableau 2.7 ») afin de garder le code et le rapport harmonisés.

## Structure du projet

Voir Chapitre 3, §3.5 (« Organisation du code source ») et l'Extrait 3.1
pour le détail de l'arborescence et sa correspondance avec l'architecture en
couches (Figure 2.7).

## Installation

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # puis renseigner de vraies valeurs
```

## Lancer la stack d'infrastructure

```bash
docker compose up -d
```

Démarre `postgres-hcy` (avec le schéma `sql/init.sql` appliqué
automatiquement), `prometheus-hcy`, `grafana-hcy` et l'API FastAPI
conteneurisée (`api`, port 8080).

## Lancer le moteur de surveillance (processus hôte)

```bash
python run_engine.py
```

Démarre la boucle continue RF-01 (Collector → Analyzer → Factory/Strategy →
Observers) décrite en 1.4.6 et Figure 2.5, ainsi que le serveur de métriques
Prometheus sur le port 8000 (scrapé par `prometheus.yml`). À exécuter sur la
machine hôte, avec accès réseau vers la topologie GNS3 (interface Host-Only
VirtualBox, cf. 3.4) — jamais dans un conteneur Docker.

## Lancer le portail Streamlit

```bash
streamlit run ui/streamlit_app.py
```

Toutes les données affichées (grille d'équipements, incidents, panneaux
d'observabilité) viennent réellement de l'API → PostgreSQL/Prometheus. Le
menu « Observabilité (Grafana) » intègre directement le vrai Grafana
(iframe, dashboard `hcy-overview` provisionné automatiquement au démarrage
de `docker compose` — aucune capture, aucune donnée reconstituée).

## Exécuter la suite de tests (3.9)

```bash
pytest --cov=core --cov=strategies --cov=observers --cov=repositories --cov=api --cov-report=term-missing
flake8 core/ strategies/ observers/ repositories/ api/
```

## Modules nécessitant un environnement complet

Certains modules dépendent de paquets tiers (`netmiko`, `psycopg2`,
`prometheus_client`, `fastapi`, `streamlit`) et ne peuvent être exécutés que
dans un environnement où `pip install -r requirements.txt` a réussi. Le
détail de ce qui a été vérifié lors du développement de ce dépôt (tests
exécutés vs. simple vérification syntaxique) est documenté dans
`VERIFICATION.md`.
