import os
import glob
import platform
import argparse
import datetime

def analyser_logs(chemin_source, niveau_filtrage="ALL"):
    """
    Module 1 : Ingestion et Analyse.
    Cette fonction scanne les fichiers de logs, filtre les entrées selon le niveau spécifié
    et calcule des statistiques détaillées (total, par niveau, top 5 erreurs).
    """
    # Initialisation d'une liste vide pour stocker les chemins des fichiers à analyser
    fichiers_a_traiter = []
    
    # Vérification : si le chemin fourni est un dossier
    if os.path.isdir(chemin_source):
        # Création du motif de recherche pour cibler uniquement les fichiers se terminant par .log
        pattern = os.path.join(chemin_source, "*.log")
        # Utilisation de glob pour récupérer tous les fichiers correspondants au motif
        fichiers_a_traiter = glob.glob(pattern)
    
    # Sinon, on vérifie si le chemin fourni correspond à un fichier existant unique
    elif os.path.isfile(chemin_source):
        # On ajoute ce fichier seul dans la liste pour qu'il soit traité par la suite
        fichiers_a_traiter = [chemin_source]

    # Condition d'arrêt : si aucun fichier log n'a été trouvé dans le chemin spécifié
    if not fichiers_a_traiter:
        # On retourne None pour indiquer à l'appelant qu'il n'y a rien à analyser
        return None

    # Initialisation du compteur pour le nombre total de lignes après filtrage
    total_lignes = 0
    # Initialisation du compteur pour les messages de niveau ERROR
    compteur_error = 0
    # Initialisation du compteur pour les messages de niveau WARN
    compteur_warn = 0
    # Initialisation du compteur pour les messages de niveau INFO
    compteur_info = 0
    
    # Création d'un dictionnaire vide pour compter la fréquence de chaque message d'erreur unique
    messages_erreur = {}
    
    # Boucle principale : on parcourt chaque fichier identifié dans l'étape d'ingestion
    for fichier in fichiers_a_traiter:
        # Bloc try-except pour capturer d'éventuels problèmes de lecture (ex: permissions)
        try:
            # Ouverture du fichier en mode lecture avec encodage UTF-8
            with open(fichier, 'r', encoding='utf-8') as f:
                # Boucle secondaire : lecture du fichier ligne par ligne
                for ligne in f:
                    # Nettoyage de la ligne en supprimant les espaces et sauts de ligne inutiles
                    ligne = ligne.strip()
                    # Si la ligne est vide après nettoyage, on passe à la suivante
                    if not ligne:
                        continue
                    
                    # Découpage de la ligne en maximum 4 parties (Date, Heure, Niveau, Message)
                    parties = ligne.split(' ', 3)
                    # Vérification : la ligne doit contenir au moins la date, l'heure et le niveau
                    if len(parties) >= 3:
                        # Extraction du niveau (3ème colonne) et conversion en capitales
                        niveau_ligne = parties[2].upper()
                        
                        # Vérification du niveau : si on filtre (pas ALL) et que le niveau ne correspond pas
                        if niveau_filtrage != "ALL" and niveau_ligne != niveau_filtrage:
                            # Alors on ignore cette ligne et on passe à la suivante
                            continue
                            
                        # Si la ligne passe le filtre, on incrémente le compteur total
                        total_lignes += 1
                        
                        # Condition : si le niveau est une erreur
                        if niveau_ligne == "ERROR":
                            # On incrémente le compteur spécifique aux erreurs
                            compteur_error += 1
                        # Sinon, si le niveau est un avertissement (WARN)
                        elif niveau_ligne == "WARN":
                            # On incrémente le compteur des avertissements
                            compteur_warn += 1
                        # Sinon, si le niveau est une information (INFO)
                        elif niveau_ligne == "INFO":
                            # On incrémente le compteur des informations
                            compteur_info += 1
                        
                        # Condition spécifique : pour les erreurs, on veut aussi isoler le message
                        if niveau_ligne == "ERROR" and len(parties) == 4:
                            # Le message se trouve dans la 4ème partie de la ligne splitée
                            message_erreur = parties[3]
                            # On ajoute 1 au compteur de ce message spécifique dans notre dictionnaire
                            messages_erreur[message_erreur] = messages_erreur.get(message_erreur, 0) + 1
                            
        except Exception as e:
            # Si une erreur survient (ex: fichier bloqué), on affiche l'erreur et on passe au fichier suivant
            print(f"Erreur lors de la lecture de {fichier} : {e}")
    
    # Préparation du dictionnaire pour le Top 5 des erreurs les plus fréquentes
    top5_erreurs = {}
    # Tri des erreurs par valeur (nombre d'occurrences) dans l'ordre décroissant
    messages_tries = sorted(messages_erreur.items(), key=lambda x: x[1], reverse=True)
    
    # Boucle pour extraire les 5 premiers éléments de la liste triée
    for i in range(min(5, len(messages_tries))):
        # Récupération du message et de son nombre d'occurrences
        message, count = messages_tries[i]
        # Ajout dans le dictionnaire final du Top 5
        top5_erreurs[message] = count
    
    # Préparation du dictionnaire de statistiques par niveau
    par_niveau = {}
    
    # Condition : si le filtre est "ALL", on inclut tous les niveaux
    if niveau_filtrage == "ALL":
        # On remplit le dictionnaire avec les trois compteurs
        par_niveau = {
            "ERROR": compteur_error,
            "WARN": compteur_warn,
            "INFO": compteur_info
        }
    # Sinon, si un niveau spécifique a été demandé (ex: WARN)
    else:
        # On ne crée l'entrée que pour le niveau qui a été filtré
        if niveau_filtrage == "ERROR":
            par_niveau["ERROR"] = compteur_error
        elif niveau_filtrage == "WARN":
            par_niveau["WARN"] = compteur_warn
        elif niveau_filtrage == "INFO":
            par_niveau["INFO"] = compteur_info

    # Construction du sous-dictionnaire de statistiques
    stats = {
        # Nombre total de lignes validées par le filtre
        "total_lignes": total_lignes,
        # Ajout des totaux par niveau (filtré ou complet)
        "par_niveau": par_niveau,
        # Ajout de la liste des fichiers traités (noms de base pour le rapport)
        "fichiers_traites": [os.path.basename(f) for f in fichiers_a_traiter]
    }
    
    # Condition : si on a du ERROR ou du ALL, on inclut le Top 5 des messages d'erreurs
    if niveau_filtrage in ["ALL", "ERROR"]:
        # On ajoute la clé des erreurs les plus fréquentes au dictionnaire stats
        stats["top5_erreurs"] = top5_erreurs

    # Construction de l'objet de résultat final structuré
    resultat = {
        "metadata": {
            # On stocke l'heure précise de l'analyse
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # On récupère le nom de l'utilisateur qui a lancé le script
            "utilisateur": os.environ.get('USER', os.environ.get('USERNAME', 'Inconnu')),
            # On identifie le système d'exploitation et sa version
            "os": f"{platform.system()} {platform.release()}",
            # On enregistre le chemin absolu de la source analysée
            "source": os.path.abspath(chemin_source)
        },
        "statistiques": stats
    }
    
    # On retourne le dictionnaire complet à l'appelant
    return resultat

# Bloc d'exécution principal du script
if __name__ == "__main__":
    # Création du gestionnaire d'arguments pour la ligne de commande
    parser = argparse.ArgumentParser(description="Module 1 - Ingestion et Analyse des logs")
    
    # Définition de l'argument obligatoire --source
    parser.add_argument("--source", required=True, help="Dossier ou fichier contenant les logs")
    # Définition de l'argument optionnel --niveau avec des choix limités
    parser.add_argument("--niveau", default="ALL", choices=["ERROR", "WARN", "INFO", "ALL"], 
                        help="Niveau de filtrage des logs (ERROR, WARN, INFO, ALL)")
    
    # Analyse des arguments passés par l'utilisateur lors du lancement
    args = parser.parse_args()
    
    # Appel de la fonction principale avec les arguments fournis
    resultat = analyser_logs(args.source, args.niveau)
    
    # Vérification : si un résultat a été produit
    if resultat is not None:
        # Importation du module json pour un affichage propre
        import json
        # Impression du dictionnaire au format JSON lisible
        print(json.dumps(resultat, indent=4, ensure_ascii=False))
    # Sinon, si aucun fichier n'a été trouvé
    else:
        # Affichage d'un message d'erreur explicatif
        print(f"Aucun fichier log trouvé dans : {args.source}")