# Topologie GNS3 densifiée — HCY (adaptée aux routeurs à 2 ports)

Cette version tient compte d'une contrainte réelle : les routeurs émulés ne
disposent que de 2 interfaces utilisables. La solution n'est pas de réduire
la densité de l'infrastructure, mais d'insérer des **switches comme points
d'agrégation** partout où un routeur devrait sinon se connecter à plusieurs
voisins à la fois — un switch, lui, n'est jamais limité en nombre de ports.

## Schéma de câblage

```
                    coeur-reseau (10.10.0.1)
                    Gi0/0          Gi0/1
                      |              |
                   sw-core         Cloud (Host-Only) → run_engine.py
              (switch, 0 config,
               autant de ports
                  que voulu)
                      |
        +-------------+-------------+
        |             |             |
   Gi0/0 (10.10.0.2) Gi0/0 (.3)  Gi0/0 (.4)
  routeur-urgences  routeur-secours  routeur-administration
        Gi0/1             Gi0/1           Gi0/1
   192.168.20.1      192.168.21.1     192.168.30.1
        |                 |                 |
   sw-urgences       sw-laboratoire     sw-caisse
   192.168.20.5      192.168.21.5      192.168.30.5
                       Fa0/2 |            Fa0/2 |
                      sw-imagerie        sw-pharmacie
                      192.168.21.6       192.168.30.6
                                           Fa0/2 |
                                        sw-administration
                                          192.168.30.7
```

## Le principe, en une phrase

**Chaque routeur n'utilise jamais que 2 ports : un vers le haut (Gi0/0), un
vers le bas (Gi0/1).** Là où un département a besoin de plusieurs switches
(secours, administration), ils se chaînent entre eux par leurs propres
ports (Fa0/0 = montant, Fa0/2 = vers le switch suivant) — jamais en
ajoutant un port sur le routeur.

## Ordre de configuration

1. `01-coeur-reseau.txt`
2. `01b-sw-core.txt` — souvent aucune config si switch GNS3 natif
3. `02-routeur-urgences.txt` → `04-routeur-administration.txt`
4. `05-sw-urgences.txt` → `10-sw-administration.txt`, dans l'ordre (les
   notes de chaînage dans chaque fichier indiquent quel port relie quel
   switch suivant)

## Câblage physique dans GNS3 (glisser-déposer les liens)

- `coeur-reseau` Gi0/0 ↔ `sw-core` (n'importe quel port)
- `coeur-reseau` Gi0/1 ↔ `Cloud`
- `sw-core` ↔ `routeur-urgences` Gi0/0
- `sw-core` ↔ `routeur-secours` Gi0/0
- `sw-core` ↔ `routeur-administration` Gi0/0
- `routeur-urgences` Gi0/1 ↔ `sw-urgences` Fa0/0
- `routeur-secours` Gi0/1 ↔ `sw-laboratoire` Fa0/0
- `sw-laboratoire` Fa0/2 ↔ `sw-imagerie` Fa0/0
- `routeur-administration` Gi0/1 ↔ `sw-caisse` Fa0/0
- `sw-caisse` Fa0/2 ↔ `sw-pharmacie` Fa0/0
- `sw-pharmacie` Fa0/2 ↔ `sw-administration` Fa0/0
- `sw-core` ↔ `dpi-server` (n'importe quel port libre — voir `11-dpi-server.txt`)

## Si tes routeurs supportent des modules d'extension

Certaines images GNS3 (c3725, c3600, c7200) ont des slots libres : clic
droit sur le routeur → *Configure* → onglet slots → ajouter un module
(NM-1FE-TX, PA-FE-TX...) donne un port physique de plus. Si c'est ton cas,
tu peux revenir à une topologie en étoile directe sans `sw-core` — mais la
version ci-dessus fonctionne sur **n'importe quel routeur**, même les plus
limités, donc c'est celle recommandée par défaut.
