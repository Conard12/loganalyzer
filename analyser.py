import os
import glob
import platform
import collections

def analyser_logs(chemin_source):
    """
    Module 1 : Ingestion et analyse des fichiers logs.
    Calcule les statistiques (total lignes, niveaux, top 5 erreurs) et les métadonnées.
    """
    fichiers_a_traiter = []
    
    # 1. Identification de la cible (dossier ou fichier unique)
    if os.path.isdir(chemin_source):
        # Scan de tous les fichiers .log (requis par le PDF)
        pattern = os.path.join(chemin_source, "*.log")
        fichiers_a_traiter = glob.glob(pattern)
    elif os.path.isfile(chemin_source):
        fichiers_a_traiter = [chemin_source]

    # Arrêt si rien n'est trouvé
    if not fichiers_a_traiter:
        return None

    # 2. Initialisation des compteurs
    total_lignes = 0
    par_niveau = {"ERROR": 0, "WARN": 0, "INFO": 0}
    compteur_erreurs = collections.Counter()

    # 3. Lecture synchronisée des fichiers
    for fichier in fichiers_a_traiter:
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                for ligne in f:
                    ligne = ligne.strip()
                    if not ligne:
                        continue
                        
                    total_lignes += 1
                    
                    # Split limité pour extraire : [DATE] [HEURE] [NIVEAU] [MESSAGE]
                    # Format: YYYY-MM-DD HH:MM:SS NIVEAU Message
                    parties = ligne.split(' ', 3)
                    if len(parties) >= 3:
                        niveau = parties[2].upper()
                        if niveau in par_niveau:
                            par_niveau[niveau] += 1
                        
                        # Stockage du message d'erreur pour le Top 5
                        if niveau == "ERROR" and len(parties) == 4:
                            compteur_erreurs[parties[3]] += 1
        except Exception as e:
            print(f"Erreur lors de la lecture de {fichier} : {e}")

    # 4. Construction de l'objet de statistiques structuré
    stats = {
        "metadata": {
            "date": "", # Sera complété par le module rapport.py
            "utilisateur": os.environ.get('USER') or os.environ.get('USERNAME') or "Inconnu",
            "os": f"{platform.system()} {platform.release()}",
            "source": os.path.abspath(chemin_source)
        },
        "statistiques": {
            "total_lignes": total_lignes,
            "par_niveau": par_niveau,
            "top5_erreurs": dict(compteur_erreurs.most_common(5))
        }
    }
    
    return stats
