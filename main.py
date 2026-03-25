import os
import sys
import argparse

# Récupération du chemin absolu du dossier du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Importation des modules
import sys
sys.path.insert(0, BASE_DIR)

try:
    from analyser import analyser_logs
    from rapport import generer_rapport
    from archiver import archiver_log, nettoyer_anciens_rapports
except ImportError as e:
    print(f"ERREUR FATALE : Impossible d'importer les modules nécessaires : {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="LogAnalyzer Pro - Module 4 Orchestration")
    parser.add_argument("cible", help="Nom du fichier log dans logs_test ou chemin absolu")
    parser.add_argument("--niveau", default="ALL", choices=["ERROR", "WARN", "INFO", "ALL"], help="Niveau de filtrage")
    parser.add_argument("--archive", action="store_true", help="Archiver après traitement")
    parser.add_argument("--dest", default=os.path.join(BASE_DIR, "backups"), help="Dossier de destination pour les archives")
    parser.add_argument("--retention", type=int, default=30, help="Nombre de jours de rétention des rapports")
    
    args = parser.parse_args()
    
    # Construction du chemin absolu de la cible
    if os.path.isabs(args.cible):
        chemin_cible = args.cible
    elif os.path.exists(args.cible):
        # Si le chemin existe déjà tel quel (ex: "logs_test" ou un fichier local)
        chemin_cible = os.path.abspath(args.cible)
    else:
        # On assume que c'est dans logs_test si c'est un nom simple absent du dossier local
        chemin_cible = os.path.join(BASE_DIR, "logs_test", args.cible)
    
    if not os.path.exists(chemin_cible):
        print(f"ERREUR FATALE : Le chemin spécifié n'existe pas : {chemin_cible}")
        sys.exit(1)

    print(f"--- Début de l'orchestration pour : {os.path.basename(chemin_cible)} ---")

    # 1. Étape d'Analyse (Module 1)
    try:
        print("[1/3] Analyse des logs...")
        stats = analyser_logs(chemin_cible, args.niveau)
        if stats is None:
            raise ValueError("Le module d'analyse a retourné None.")
    except Exception as e:
        print(f"ERREUR CRITIQUE (Analyse) : {e}")
        sys.exit(1)

    # 2. Étape de Rapport (Module 2)
    try:
        print("[2/3] Génération du rapport...")
        nom_log = os.path.basename(chemin_cible)
        # Chemin absolu pour le dossier rapports
        dossier_rapports = os.path.join(BASE_DIR, "rapports")
        # On passe uniquement la partie statistiques au module de rapport
        succes_rapport = generer_rapport(stats["statistiques"], nom_log, dossier_rapports)
        if not succes_rapport:
            print("AVERTISSEMENT : La génération du rapport a échoué.")
        
        # Nettoyage des anciens rapports (Module 3 exigence)
        nettoyer_anciens_rapports(dossier_rapports, args.retention)
    except Exception as e:
        print(f"ERREUR CRITIQUE (Rapport) : {e}")
        # On peut décider si c'est fatal ou non. Ici on considère que oui pour respecter la consigne.
        sys.exit(1)

    # 3. Étape d'Archivage (Module 3 - Optionnel)
    if args.archive:
        try:
            print("[3/3] Archivage du fichier...")
            # On utilise le dossier spécifié par --dest ou par défaut
            dossier_backups = args.dest if os.path.isabs(args.dest) else os.path.join(BASE_DIR, args.dest)
            succes_archive = archiver_log(chemin_cible, dossier_backups)
            if not succes_archive:
                print("AVERTISSEMENT : L'archivage a échoué.")
        except Exception as e:
            print(f"ERREUR CRITIQUE (Archivage) : {e}")
            sys.exit(1)
    else:
        print("[3/3] Archivage sauté (pas de flag --archive).")

    print("\nOrchestration terminée avec succès.")

if __name__ == "__main__":
    main()
