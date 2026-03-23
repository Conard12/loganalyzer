import os
import glob
import platform
import collections
import argparse

def analyser_logs(chemin_source, niveau_filtrage="ALL"):
    """
    Module 1 : Ingestion et Analyse.
    Filtre les logs selon le niveau et renvoie les statistiques.
    """
    fichiers_a_traiter = []
    
    if os.path.isdir(chemin_source):
        # Scan de tous les fichiers .log (requis par le PDF)
        pattern = os.path.join(chemin_source, "*.log")
        fichiers_a_traiter = glob.glob(pattern)
    elif os.path.isfile(chemin_source):
        fichiers_a_traiter = [chemin_source]

    if not fichiers_a_traiter:
        return None

    total_lignes = 0
    par_niveau = {"ERROR": 0, "WARN": 0, "INFO": 0}
    compteur_erreurs = collections.Counter()

    for fichier in fichiers_a_traiter:
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                for ligne in f:
                    ligne = ligne.strip()
                    if not ligne:
                        continue
                    
                    # Format: YYYY-MM-DD HH:MM:SS NIVEAU Message
                    parties = ligne.split(' ', 3)
                    if len(parties) >= 3:
                        niveau_ligne = parties[2].upper()
                        
                        # FILTAGE (Règle Module 1)
                        if niveau_filtrage != "ALL" and niveau_ligne != niveau_filtrage:
                            continue
                            
                        total_lignes += 1
                        if niveau_ligne in par_niveau:
                            par_niveau[niveau_ligne] += 1
                        
                        if niveau_ligne == "ERROR" and len(parties) == 4:
                            compteur_erreurs[parties[3]] += 1
                            
        except Exception as e:
            print(f"Erreur lors de la lecture de {fichier} : {e}")

    return {
        "metadata": {
            "date": "", # Complété par Module 2
            "utilisateur": os.environ.get('USER', os.environ.get('USERNAME', 'Inconnu')),
            "os": f"{platform.system()} {platform.release()}",
            "source": os.path.abspath(chemin_source)
        },
        "statistiques": {
            "total_lignes": total_lignes,
            "par_niveau": par_niveau,
            "top5_erreurs": dict(compteur_erreurs.most_common(5))
        }
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Module 1 - Ingestion et Analyse")
    parser.add_argument("--source", required=True, help="Dossier contenant les logs")
    parser.add_argument("--niveau", default="ALL", choices=["ERROR", "WARN", "INFO", "ALL"])
    args = parser.parse_args()
    print(analyser_logs(args.source, args.niveau))
