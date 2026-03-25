# 📊 LogAnalyzer Pro - Pipeline d'Analyse de Logs

## 1. Description du projet et objectif
LogAnalyzer Pro est un outil d'analyse de logs en ligne de commande (CLI) développé en Python dans le cadre d'un TP de programmation système. Il permet d'analyser des fichiers de logs applicatifs, de générer des rapports structurés au format JSON, d'archiver les fichiers traités et d'appliquer une politique de rétention sur les anciens rapports.

L'objectif est de fournir une solution automatisée et robuste, utilisable dans un environnement DevOps. L'outil respecte les contraintes de programmation système : gestion des erreurs, utilisation de chemins absolus via `__file__`, et compatibilité cross-platform.

## 2. Prérequis et installation
* **Version de Python** : 3.8 ou supérieure.
* **Dépendances** : Aucune (utilisation exclusive de la bibliothèque standard).
* **Systèmes supportés** : Windows, Linux, macOS.

### Installation
1. Cloner le projet : `git clone https://github.com/Conard12/loganalyzer.git`
2. Se déplacer dans le dossier : `cd loganalyzer`
3. Rendre les scripts exécutables : `chmod +x main.py analyser.py rapport.py archiver.py`

## 3. Utilisation : exemples de commandes
* **Analyse standard de tous les logs** : 
  `python3 main.py --source ./logs_test`
* **Filtrage des erreurs uniquement** : 
  `python3 main.py --source ./logs_test --niveau ERROR`
* **Archivage personnalisé et rétention de 15 jours** : 
  `python3 main.py --source ./logs_test --dest ./archives_custom --retention 15`
* **Analyse sans archivage** : 
  `python3 main.py --source ./logs_test --no-archive`

### Arguments disponibles
* `--source` : (Obligatoire) Chemin du dossier ou du fichier .log à analyser.
* `--niveau` : Niveau de filtrage (INFO, WARN, ERROR, ALL). Par défaut : ALL.
* `--dest` : Dossier de destination pour les archives .tar.gz. Par défaut : ./backups.
* `--retention` : Nombre de jours de conservation des rapports JSON. Par défaut : 30.
* `--no-archive` : Désactive l'archivage automatique.

## 4. Description de chaque module
* **main.py** : Orchestrateur central. Il gère les arguments CLI, construit les chemins absolus et coordonne l'exécution des autres modules.
* **analyser.py** : Module 1. Responsable du scan des fichiers via `glob`, du filtrage des lignes et du calcul du Top 5 des erreurs.
* **rapport.py** : Module 2. Formate les données et génère le fichier JSON incluant les métadonnées (OS, utilisateur, date).
* **archiver.py** : Module 3. Gère la compression en `.tar.gz`, vérifie l'espace disque avec `subprocess` et supprime les rapports obsolètes.

## 5. Ligne Cron complète et expliquée
Pour une exécution automatique chaque dimanche à 03h00 du matin :
`0 3 * * 0 cd /chemin/vers/loganalyzer && /usr/bin/python3 main.py --source /chemin/vers/logs --retention 30 >> /var/log/loganalyzer.log 2>&1`

**Explication :**
* `0 3` : Déclenchement à 3h00 pile.
* `* * 0` : Chaque dimanche.
* `>> ... 2>&1` : Enregistre les messages et les erreurs dans un fichier journal.

## 6. Répartition des tâches au sein du groupe
* **Module 1 (Ingestion et Analyse)** : BELLO Mantinou
* **Module 2 (Génération du Rapport JSON)** : VODOUNON Majorelle
* **Module 3 (Archivage et Nettoyage)** : OKOTCHE Jean-Marie
* **Module 4 (Point d'entrée et Orchestration)** : SALOU Mouhamed
* **README Technique et Tests** : Fadilath ADEGNILE

## 7. Données de test
Le dossier `logs_test/` contient des fichiers (app1.log, app2.log, app3.log) avec au minimum 20 lignes chacun. Ils respectent le format : `YYYY-MM-DD HH:MM:SS NIVEAU Message`.

## 8. Structure du projet
* `main.py` : Point d'entrée.
* `analyser.py` : Moteur d'analyse.
* `rapport.py` : Création du rapport.
* `archiver.py` : Maintenance système.
* `logs_test/` : Dossier des fichiers logs.
* `rapports/` : Dossier des sorties JSON (généré).
* `backups/` : Dossier des archives (généré).

## 9. Gestion des erreurs
* Le script vérifie l'existence du dossier source avant de commencer.
* L'archivage est annulé si l'espace disque est insuffisant pour éviter de saturer le système.
* Les erreurs d'importation de modules sont interceptées avec un message explicatif.
* Chaque étape est protégée par un bloc try/except pour éviter les plantages brutaux.

## 10. Contraintes techniques respectées
* Utilisation exclusive de la bibliothèque standard Python.
* Chemins de fichiers absolus via l'utilisation de `__file__`.
* Présence du shebang et de l'encodage UTF-8 dans chaque fichier.
* Documentation complète via les docstrings de fonctions.

## 11. Auteurs
Projet réalisé dans le cadre du TP de Programmation Système en Python (L3).
Date : 25 Mars 2026.

## 12. Licence
Ce projet est à but pédagogique pour l'Université ESGIS.

## 13. Remerciements
Merci à l'équipe pour la collaboration technique et à l'enseignant pour les directives du projet.