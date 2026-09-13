# Méthodologie de vérification de ce code

Ce document explique **précisément** ce qui a été vérifié dans le code de ce
dépôt avant sa livraison, comment, et surtout ce qui **n'a pas pu être
vérifié** dans l'environnement de développement utilisé — par honnêteté
académique (cf. Chapitre 4 du mémoire, §4.1.2, sur la nécessité de ne jamais
présenter un résultat comme acquis sans en préciser les conditions de
mesure).

## 1. Contrainte de l'environnement de développement

L'environnement dans lequel ce code a été écrit et vérifié n'a **pas accès
au dépôt de fichiers PyPI** (`files.pythonhosted.org` renvoie une erreur
`403 host_not_allowed`, vérifié par une requête directe). Concrètement :

- `pip install fastapi psycopg2-binary netmiko streamlit pytest pytest-cov flake8 ...` **échoue** avec « No matching distribution found ».
- Seuls les paquets déjà présents dans l'environnement sont utilisables
  directement : bibliothèque standard Python 3.12, `PyJWT`, `requests`,
  `PyYAML`, `python-dotenv`.

Ceci ne remet pas en cause le code livré : sur une machine avec un accès
réseau normal, `pip install -r requirements.txt` puis `pytest --cov`
fonctionneront sans aucune adaptation, sur les mêmes fichiers de tests que
ceux du dépôt. Cela signifie seulement que la vérification ci-dessous a
nécessité une méthodologie de substitution, décrite intégralement ici.

## 2. Ce qui a été vérifié, et comment

### 2.1. Vérification syntaxique (100% du code)

Chaque fichier `.py` du dépôt (44 fichiers) a été compilé avec
`python -m py_compile`. **44 fichiers, 0 erreur de syntaxe.**

### 2.2. Exécution réelle de la suite de tests (48 tests, contre le vrai code)

Les paquets tiers indisponibles (`psycopg2` + `psycopg2.extras`,
`prometheus_client`, `netmiko`, `fastapi` + `fastapi.security`,
`bcrypt`, `pydantic`, `streamlit`) ont été remplacés par des
**doubles minimalistes**, structurés en vrais sous-paquets Python quand
l'original l'est (ex. `psycopg2/extras.py`), injectés dans `sys.path` avant
l'import des modules du projet — une technique standard pour tester du code
qui dépend de bibliothèques lourdes sans les installer réellement. Ces
doubles ne servent qu'à permettre l'import ; la logique testée est celle du
**vrai code du projet**, jamais celle des doubles.

De même, `pytest` lui-même n'étant pas installable, un module `pytest.py`
minimal fournissant uniquement `pytest.raises()` (la seule fonctionnalité
pytest utilisée dans les fichiers de tests) a permis d'exécuter les fichiers
de `tests/` **tels qu'écrits**, sans les modifier pour l'occasion.

Un script d'exécution (`run_tests.py`, outil de vérification interne, non
livré dans ce dépôt) a importé chaque `tests/test_*.py` et appelé chaque
fonction `test_*` directement, en capturant `AssertionError` comme un échec
— reproduisant le comportement de collecte/exécution de base de pytest.

**Résultat de la dernière exécution (reproductible, voir §4) :**

| Indicateur | Valeur mesurée |
|---|---|
| Fichiers de tests | 13 |
| Tests exécutés | 48 |
| Tests réussis | 48 |
| Tests échoués | 0 |
| Erreurs de collecte (import) | 0 |

### 2.3. Couverture de lignes réelle (module standard `trace`)

`pytest-cov` n'étant pas installable, la couverture a été mesurée avec le
module de la bibliothèque standard `trace` (`trace.Trace(count=True)`), qui
enregistre chaque ligne réellement exécutée pendant l'exécution des tests
ci-dessus. Le pourcentage rapporte les lignes exécutées aux lignes non
vides/non purement commentaires de chaque fichier — une approximation
raisonnable de ce que rapporterait `coverage.py`, mais pas strictement
identique dans le détail (docstrings multi-lignes notamment).

**Résultat mesuré :**

| Périmètre | Lignes couvertes | Total | % |
|---|---|---|---|
| `core/` + `strategies/` + `observers/` + `repositories/` (couche métier, Figure 2.4) | 367 | 553 | **66,4 %** |
| Périmètre ci-dessus + `api/` | 390 | 685 | 56,9 % |

Le détail par fichier (reproductible via `measure_coverage.py`) montre deux
cas de figure distincts :

- Les interfaces pures (`strategies/base.py`, `observers/base.py`,
  `repositories/base.py` — 0% chacune) sont des classes abstraites
  (`ABC`) dont le corps de méthode est un simple `raise
  NotImplementedError` : non significatif à exécuter directement, puisque
  ce sont leurs implémentations concrètes qui sont testées.
- `api/main.py` (0%) et `api/schemas.py` (0%) ne sont couverts par aucun
  test : `tests/test_auth.py` teste la logique JWT pure d'`api/auth.py`,
  mais aucun test n'exerce encore les routes FastAPI elles-mêmes (cela
  nécessiterait `fastapi.testclient.TestClient`, non disponible ici). C'est
  un écart réel, cohérent avec celui déjà identifié au Chapitre 4 (4.4.2,
  OS3) sur la validation empirique du contrôle d'accès.

### 2.4. Vérification de style (approximation manuelle, flake8 non installable)

- Longueur de ligne (seuil 99 caractères) : **3 lignes** dépassaient
  initialement ce seuil (`core/engine.py`, `ui/streamlit_app.py`,
  `tests/test_engine.py`) ; **corrigées, 0 ligne restante** à la vérification
  finale.
- Détection heuristique d'imports inutilisés (via `ast`) : les seuls signaux
  obtenus sont des faux positifs systématiques sur `from __future__ import
  annotations` (directive de compilation, jamais « utilisée » au sens
  littéral) — **aucun import mort réel détecté**.
- **Non couvert par cette vérification manuelle** : les règles flake8 plus
  fines (espacement PEP8 précis, conventions de nommage, complexité de
  McCabe si activée). Un `flake8 core/ strategies/ observers/ repositories/
  api/` réel, sur une machine avec accès PyPI, reste nécessaire avant de
  considérer ce point définitivement clos.

### 2.5. Complexité cyclomatique (approximation manuelle, radon non installable)

Calcul manuel via `ast` (formule standard : 1 + nombre de points de
branchement `if`/`for`/`while`/`except`/`with`/opérateurs booléens/gardes de
comprehension) sur les fonctions et méthodes des paquets `core/`,
`strategies/`, `observers/`, `repositories/`, `api/` :

| Indicateur | Valeur |
|---|---|
| Fonctions/méthodes analysées | 46 |
| Complexité cyclomatique moyenne | **1,37** |
| Complexité maximale | `api/main.py::login` (4) |

Une valeur proche de 1 est attendue pour un code structuré en petites
méthodes à responsabilité unique (cf. Chapitre 1, 1.2.1, justification des
patterns de conception). Ce chiffre n'est pas strictement identique à ce que
rapporterait `radon` (règles plus fines sur comprehensions/ternaires), mais
la méthode de calcul est documentée intégralement ci-dessus et reproductible.

## 3. Ce qui n'a PAS pu être vérifié dans cet environnement

Par honnêteté, voici ce que cette vérification ne couvre pas et qui reste à
faire avant tout déploiement réel :

- **Aucune connexion SSH réelle** vers un équipement Cisco (GNS3 ou
  physique) : `core/netmiko_ssh_client.py` n'a été testé qu'avec un double
  de `ConnectHandler`.
- **Aucune base PostgreSQL réelle** : `repositories/postgres_repository.py`
  n'a été testé qu'avec un double de `psycopg2.connect`.
- **Aucun serveur Prometheus/Grafana réel**, aucune requête PromQL exécutée.
- **Aucune requête HTTP réelle** vers l'API FastAPI (le serveur n'a jamais
  été démarré, `api/main.py` a une couverture de tests de 0% — cf. 2.3) ni
  vers le portail Streamlit.
- **Le hachage bcrypt réel** n'a été exercé qu'avec un double qui décale
  chaque octet (jamais le vrai algorithme) — suffisant pour valider la
  logique de `hash_password`/`verify_password`, pas pour garantir les
  propriétés cryptographiques réelles de bcrypt lui-même.
- **`flake8`, `pytest-cov` et `radon` eux-mêmes** n'ont jamais tourné : les
  chiffres ci-dessus sont des mesures réelles obtenues par des moyens
  alternatifs (bibliothèque standard), pas les sorties de ces outils.

## 4. Reproduire cette vérification (ou la suite complète, réelle)

Sur une machine avec un accès réseau normal, la vérification légitime et
complète consiste simplement à :

```bash
pip install -r requirements.txt
pytest --cov=core --cov=strategies --cov=observers --cov=repositories --cov=api --cov-report=term-missing
flake8 core/ strategies/ observers/ repositories/ api/
```

Ces commandes exécuteront exactement les mêmes fichiers de tests, sans
aucun double ni adaptation — les fichiers de `tests/` n'ont pas été écrits
différemment pour cette vérification interne.
