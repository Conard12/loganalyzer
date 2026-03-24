import os
import tarfile
import shutil
import datetime
import time
import subprocess

def _lister_logs(chemin_source):
    if os.path.isdir(chemin_source):
        return sorted(
            [
                os.path.join(chemin_source, f)
                for f in os.listdir(chemin_source)
                if f.lower().endswith(".log")
            ]
        )
    if os.path.isfile(chemin_source) and chemin_source.lower().endswith(".log"):
        return [chemin_source]
    return []


def verifier_espace_disque(dossier):
    """
    Vérifie l'espace disque disponible via subprocess.
    Retourne l'espace libre en octets (int).
    """
    dossier = os.path.abspath(dossier)
    try:
        if os.name == "nt":
            drive, _ = os.path.splitdrive(dossier)
            if not drive:
                drive, _ = os.path.splitdrive(os.getcwd())
            drive_letter = drive.replace(":", "")
            commande = [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-PSDrive -Name '{drive_letter}').Free",
            ]
            sortie = subprocess.check_output(commande, text=True, stderr=subprocess.STDOUT).strip()
            return int(float(sortie))

        resultat = subprocess.check_output(["df", "-Pk", dossier], text=True, stderr=subprocess.STDOUT)
        lignes = [l for l in resultat.splitlines() if l.strip()]
        if len(lignes) < 2:
            raise RuntimeError("Sortie 'df' inattendue.")
        colonnes = lignes[1].split()
        espace_libre_ko = int(colonnes[3])
        return espace_libre_ko * 1024
    except Exception as e:
        print(f"Erreur lors de la vérification de l'espace disque : {e}")
        return 0


def archiver_log(chemin_source, dossier_dest):
    """
    Archive tous les fichiers .log traités dans une archive backup_YYYY-MM-DD.tar.gz (mode w:gz),
    puis déplace l'archive vers le dossier de destination (--dest).
    """
    if not os.path.exists(dossier_dest):
        os.makedirs(dossier_dest)

    fichiers_logs = _lister_logs(chemin_source)
    if not fichiers_logs:
        print("AVERTISSEMENT : Aucun fichier .log à archiver.")
        return False

    taille_totale = 0
    for f in fichiers_logs:
        try:
            taille_totale += os.path.getsize(f)
        except OSError:
            pass
    taille_estimee_archive = int(taille_totale * 1.10) + (5 * 1024 * 1024)

    espace_libre = verifier_espace_disque(dossier_dest)
    if espace_libre < taille_estimee_archive:
        libre_go = espace_libre / (1024**3) if espace_libre else 0
        requis_go = taille_estimee_archive / (1024**3)
        print(
            "AVERTISSEMENT : Espace disque insuffisant pour archiver "
            f"({libre_go:.2f} Go libres, ~{requis_go:.2f} Go requis)."
        )
        return False

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    nom_archive = f"backup_{date_str}.tar.gz"
    chemin_archive_finale = os.path.join(dossier_dest, nom_archive)

    try:
        chemin_archive_temp = os.path.abspath(nom_archive)
        if os.path.exists(chemin_archive_temp):
            i = 1
            while True:
                candidat = os.path.abspath(f"backup_{date_str}_{i}.tar.gz")
                if not os.path.exists(candidat):
                    chemin_archive_temp = candidat
                    break
                i += 1

        # Création de l'archive (mode w:gz)
        with tarfile.open(chemin_archive_temp, "w:gz") as tar:
            for fichier_log in fichiers_logs:
                tar.add(fichier_log, arcname=os.path.basename(fichier_log))
        
        # Déplacer l'archive vers la destination (shutil)
        if os.path.exists(chemin_archive_finale):
            os.remove(chemin_archive_finale)
        shutil.move(chemin_archive_temp, chemin_archive_finale)
        print(f"Archive créée et déplacée : {chemin_archive_finale}")
        return True
    except Exception as e:
        print(f"Erreur lors de l'archivage : {e}")
        try:
            if "chemin_archive_temp" in locals() and os.path.exists(chemin_archive_temp):
                os.remove(chemin_archive_temp)
        except Exception:
            pass
        return False

def nettoyer_anciens_rapports(dossier_rapports, retention_jours=30):
    """
    Supprime les fichiers JSON vieux de plus de N jours.
    """
    if not os.path.exists(dossier_rapports):
        return

    maintenant = time.time()
    seconde_retention = retention_jours * 24 * 3600
    
    compteur = 0
    try:
        for fichier in os.listdir(dossier_rapports):
            if fichier.endswith(".json"):
                chemin_complet = os.path.join(dossier_rapports, fichier)
                # Utiliser os.path.getmtime() pour calculer l'âge
                age_fichier = maintenant - os.path.getmtime(chemin_complet)
                
                if age_fichier > seconde_retention:
                    os.remove(chemin_complet)
                    print(f"Fichier supprimé (obsolète) : {fichier}")
                    compteur += 1
        if compteur > 0:
            print(f"Nettoyage terminé : {compteur} rapport(s) supprimé(s).")
    except Exception as e:
        print(f"Erreur lors du nettoyage : {e}")
