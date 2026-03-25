#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module 2 - Génération du Rapport JSON
Ce module est responsable de générer un rapport structuré au format JSON
contenant les statistiques d'analyse des logs et les métadonnées système.
"""

import os
import json
import datetime
import platform


def generer_rapport(stats, nom_log, dossier_rapports):
    """
    Génère un fichier rapport_YYYY-MM-DD.json avec les statistiques d'analyse.
    
    Args:
        stats (dict): Dictionnaire contenant les statistiques d'analyse des logs
        nom_log (str): Nom du fichier log traité
        dossier_rapports (str): Chemin du dossier où sauvegarder le rapport
        
    Returns:
        bool: True si succès, False en cas d'erreur
    """
    try:
        # Création du dossier rapports s'il n'existe pas
        if not os.path.exists(dossier_rapports):
            os.makedirs(dossier_rapports)
        
        # Génération du nom de fichier avec timestamp
        date_actuelle = datetime.datetime.now().strftime("%Y-%m-%d")
        nom_fichier = f"rapport_{date_actuelle}.json"
        chemin_fichier = os.path.join(dossier_rapports, nom_fichier)
        
        # Construction du rapport JSON selon la structure imposée
        rapport = {
            "metadata": {
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "utilisateur": os.environ.get("USER", os.environ.get("USERNAME", "inconnu")),
                "os": platform.system(),
                "source": nom_log
            },
            "statistiques": {
                "total_lignes": stats.get("total_lignes", 0),
                "par_niveau": stats.get("par_niveau", {"ERROR": 0, "WARN": 0, "INFO": 0}),
                "top5_erreurs": stats.get("top5_erreurs", [])
            },
            "fichiers_traites": stats.get("fichiers_traites", [nom_log])
        }
        
        # Écriture du fichier JSON
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(rapport, f, indent=2, ensure_ascii=False)
        
        print(f"Rapport généré avec succès : {chemin_fichier}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la génération du rapport : {e}")
        return False