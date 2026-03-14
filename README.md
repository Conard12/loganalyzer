# LogAnalyzer Pro

Un outil CLI de traitement automatisé des fichiers de logs applicatifs.

## Structure du Projet

- `main.py` : Point d'entrée principal (Orchestration).
- `analyser.py` : Module 1 : Ingestion et analyse.
- `rapport.py` : Module 2 : Génération du rapport JSON.
- `archiver.py` : Module 3 : Archivage et nettoyage.
- `logs_test/` : Dossier contenant les fichiers de logs pour les tests.
- `rapports/` : Dossier où sont générés les rapports.
- `backups/` : Dossier où sont archivés les logs traités.

## Installation

Assurez-vous d'avoir Python 3.x installé.

## Utilisation

```bash
python main.py [nom_log_ou_chemin] [--archive]
```

## Automatisation (Cron)

Pour exécuter l'analyse automatiquement tous les dimanches à 03h00 :

```cron
0 3 * * 0 /usr/bin/python3 d:/loganalyzer/main.py d:/loganalyzer/logs_test --archive >> d:/loganalyzer/cron.log 2>&1
```

> [!NOTE]
> Remplacez `/usr/bin/python3` par le chemin vers votre exécutable Python si nécessaire. Sous Windows, utilisez le Task Scheduler pour un résultat équivalent.
