from zk import ZK, const

import json
import os
from datetime import datetime

# Fichier pour sauvegarder les données des utilisateurs désactivés
DISABLED_USERS_FILE = "d:\\Desktop\\ZK\\disabled_users.json"
# Fichier pour sauvegarder les pointages
ATTENDANCE_FILE = "d:\\Desktop\\ZK\\attendance.json"

def load_attendance_data():
    """Charger les données de pointage depuis le fichier JSON"""
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_attendance_data(data):
    """Sauvegarder les données de pointage dans le fichier JSON"""
    with open(ATTENDANCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_disabled_users_data():
    """Charger les données des utilisateurs désactivés"""
    if os.path.exists(DISABLED_USERS_FILE):
        with open(DISABLED_USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_disabled_users_data(data):
    """Sauvegarder les données des utilisateurs désactivés"""
    with open(DISABLED_USERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_user_interactive(conn):
    """Ajouter un utilisateur de manière interactive"""
    print("\n=== Ajouter un nouvel utilisateur ===")
    
    uid = int(input("Entrez l'UID (numéro unique): "))
    name = input("Entrez le nom: ")
    user_id = input("Entrez l'ID utilisateur: ")
    password = input("Entrez le mot de passe (ou laissez vide): ")
    
    priv_input = input("Privilège (0=User, 14=Admin) [0]: ")
    privilege = int(priv_input) if priv_input else 0
    
    group_id = input("Entrez le Group ID (ou laissez vide): ")
    
    card_input = input("Entrez le numéro de carte (ou 0): ")
    card = int(card_input) if card_input else 0
    
    conn.set_user(uid=uid, name=name, privilege=privilege, password=password, group_id=group_id, user_id=user_id, card=card)
    print(f"Utilisateur '{name}' ajouté avec succès!")

def list_users(conn):
    """Afficher tous les utilisateurs"""
    print("\n" + "="*50)
    print("         LISTE DES UTILISATEURS")
    print("="*50)
    
    users = conn.get_users()
    
    if not users:
        print("Aucun utilisateur trouvé.")
        return
    
    print(f"Nombre total d'utilisateurs: {len(users)}\n")
    print("-"*50)
    
    for user in users:
        privilege = 'User'
        if user.privilege == const.USER_ADMIN:
            privilege = 'Admin'
        
        print(f'| UID        : {user.uid}')
        print(f'| Nom        : {user.name}')
        print(f'| User ID    : {user.user_id}')
        print(f'| Privilège  : {privilege}')
        print(f'| Mot de passe: {user.password if user.password else "(aucun)"}')
        print(f'| Group ID   : {user.group_id if user.group_id else "(aucun)"}')
        print(f'| Carte      : {user.card if user.card else "(aucune)"}')
        print("-"*50)
    
    print(f"\nTotal: {len(users)} utilisateur(s)")

def delete_user_interactive(conn):
    """Supprimer un utilisateur"""
    print("\n=== Supprimer un utilisateur ===")
    uid = int(input("Entrez l'UID de l'utilisateur à supprimer: "))
    conn.delete_user(uid=uid)
    print(f"Utilisateur UID #{uid} supprimé avec succès!")

def disable_user_interactive(conn):
    """Désactiver un utilisateur (le supprime de l'appareil mais sauvegarde ses données)"""
    print("\n=== Désactiver un utilisateur ===")
    
    # Charger les utilisateurs déjà désactivés
    disabled_data = load_disabled_users_data()
    
    # Afficher la liste des utilisateurs actifs sur l'appareil
    users = conn.get_users()
    
    if not users:
        print("Aucun utilisateur trouvé sur l'appareil.")
        return
    
    print("Utilisateurs actifs sur l'appareil:")
    for user in users:
        print(f"  UID #{user.uid} - {user.name} (User ID: {user.user_id})")
    
    uid = int(input("\nEntrez l'UID de l'utilisateur à désactiver: "))
    
    # Trouver l'utilisateur
    target_user = None
    for user in users:
        if user.uid == uid:
            target_user = user
            break
    
    if not target_user:
        print(f"Utilisateur UID #{uid} non trouvé.")
        return
    
    # Sauvegarder les données de l'utilisateur avant de le supprimer
    user_data = {
        'uid': target_user.uid,
        'name': target_user.name,
        'privilege': target_user.privilege,
        'password': target_user.password,
        'group_id': target_user.group_id,
        'user_id': target_user.user_id,
        'card': target_user.card
    }
    
    # Sauvegarder dans le fichier JSON
    disabled_data[str(uid)] = user_data
    save_disabled_users_data(disabled_data)
    
    # Supprimer l'utilisateur de l'appareil (bloque l'accès)
    conn.delete_user(uid=uid)
    
    print(f"Utilisateur '{target_user.name}' désactivé avec succès!")
    print(f"L'utilisateur ne peut plus accéder à l'appareil.")
    print(f"Ses données sont sauvegardées pour une réactivation future.")

def enable_user_interactive(conn):
    """Réactiver un utilisateur (restaure depuis la sauvegarde)"""
    print("\n=== Réactiver un utilisateur ===")
    
    # Charger les utilisateurs désactivés depuis le fichier
    disabled_data = load_disabled_users_data()
    
    if not disabled_data:
        print("Aucun utilisateur désactivé trouvé.")
        return
    
    print("Utilisateurs désactivés (sauvegardés):")
    for uid, user_data in disabled_data.items():
        if isinstance(user_data, dict) and 'name' in user_data:
            print(f"  UID #{uid} - {user_data['name']} (User ID: {user_data['user_id']})")
    
    uid = input("\nEntrez l'UID de l'utilisateur à réactiver: ")
    
    if uid not in disabled_data:
        print(f"Utilisateur UID #{uid} non trouvé dans les utilisateurs désactivés.")
        return
    
    user_data = disabled_data[uid]
    
    # Afficher les restrictions existantes
    print(f"\n=== Restrictions existantes pour l'utilisateur '{user_data['name']}' ===")
    
    has_restrictions = False
    
    # Vérifier les restrictions par jour
    if 'day_restrictions' in disabled_data and uid in disabled_data['day_restrictions']:
        jours = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 5: 'Vendredi', 6: 'Samedi', 7: 'Dimanche'}
        jours_restringés = disabled_data['day_restrictions'][uid]
        jours_noms = [jours.get(j, f'Jour {j}') for j in jours_restringés]
        print(f"\n⚠️  Restriction par jour détectée:")
        print(f"   L'utilisateur est DÉSACTIVÉ les jours suivants:")
        for jour_num, jour_nom in zip(jours_restringés, jours_noms):
            print(f"     - {jour_nom} (jour {jour_num})")
        has_restrictions = True
    
    # Vérifier les activations par jour
    if 'day_activations' in disabled_data and uid in disabled_data['day_activations']:
        jours = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 5: 'Vendredi', 6: 'Samedi', 7: 'Dimanche'}
        jours_activés = disabled_data['day_activations'][uid]
        jours_noms = [jours.get(j, f'Jour {j}') for j in jours_activés]
        print(f"\n✓ Activation par jour détectée:")
        print(f"   L'utilisateur est ACTIVÉ UNIQUEMENT les jours suivants:")
        for jour_num, jour_nom in zip(jours_activés, jours_noms):
            print(f"     - {jour_nom} (jour {jour_num})")
        has_restrictions = True
    
    if not has_restrictions:
        print("\n✓ Aucune restriction de jour détectée.")
    
    # Question sur la gestion des restrictions
    if has_restrictions:
        print(f"\n⚠️  Les restrictions peuvent empêcher la réactivation correcte!")
        choix = input("\nSouhaitez-vous supprimer TOUTES les restrictions avant de réactiver? (oui/non) [oui]: ").lower()
        
        if choix != 'non':
            # Supprimer les restrictions
            if 'day_restrictions' in disabled_data and uid in disabled_data['day_restrictions']:
                del disabled_data['day_restrictions'][uid]
                print("✓ Restrictions par jour supprimées")
            if 'day_activations' in disabled_data and uid in disabled_data['day_activations']:
                del disabled_data['day_activations'][uid]
                print("✓ Activations par jour supprimées")
            save_disabled_users_data(disabled_data)
    
    try:
        # Convertir group_id - la lib ZK l'attend comme une STRING, pas un int!
        group_id = user_data['group_id']
        if isinstance(group_id, str):
            # Vérifier si c'est une chaîne vide ou contient uniquement des caractères non-imprimables
            if not group_id or not group_id.strip() or not group_id.isdigit():
                group_id = ""  # Retourner une string vide, pas 0
            else:
                try:
                    # Si c'est un chiffre valide, le garder comme string
                    group_id = str(int(group_id))
                except (ValueError, TypeError):
                    group_id = ""  # Retourner une string vide en cas d'erreur
        else:
            # Si ce n'est pas une string, le convertir
            group_id = "" if not group_id else str(int(group_id))
        
        # Afficher les paramètres qui seront envoyés au device
        print("\n--- Paramètres d'envoi au device ---")
        print(f"UID: {int(uid)} (type: {type(int(uid)).__name__})")
        print(f"Nom: '{str(user_data['name'])}' (type: {type(str(user_data['name'])).__name__})")
        print(f"Privilege: {int(user_data['privilege'])} (type: {type(int(user_data['privilege'])).__name__})")
        print(f"Password: '{str(user_data['password'])}' (type: {type(str(user_data['password'])).__name__})")
        print(f"Group ID: '{group_id}' (type: {type(group_id).__name__})")
        print(f"User ID: '{str(user_data['user_id'])}' (type: {type(str(user_data['user_id'])).__name__})")
        print(f"Card: {int(user_data['card']) if user_data['card'] else 0} (type: {type(int(user_data['card']) if user_data['card'] else 0).__name__})")
        print("-----------------------------------\n")
        
        # Restaurer l'utilisateur sur l'appareil
        result = conn.set_user(
            uid=int(uid),
            name=str(user_data['name']),
            privilege=int(user_data['privilege']),
            password=str(user_data['password']) if user_data['password'] else "",
            group_id=group_id,
            user_id=str(user_data['user_id']),
            card=int(user_data['card']) if user_data['card'] else 0
        )
        
        print(f"Résultat de set_user(): {result}")
        
        # Vérifier que l'utilisateur a bien été restauré
        import time
        time.sleep(1)  # Attendre un peu que le device traite la commande
        
        users = conn.get_users()
        user_found = False
        restored_user = None
        
        for user in users:
            if user.uid == int(uid):
                user_found = True
                restored_user = user
                break
        
        if user_found:
            print(f"\n✓ Utilisateur '{user_data['name']}' réactivé avec succès!")
            print(f"✓ UID: {restored_user.uid}")
            print(f"✓ Nom: {restored_user.name}")
            print(f"✓ User ID: {restored_user.user_id}")
            print(f"✓ L'utilisateur peut maintenant accéder à l'appareil.")
            print("\nNOTE: Les empreintes doivent être réenregistrées manuellement.")
            
            # Supprimer l'utilisateur de la liste des désactivés
            del disabled_data[uid]
            save_disabled_users_data(disabled_data)
        else:
            print(f"\n✗ ERREUR: L'utilisateur n'a pas pu être restauré sur le device.")
            print(f"\nUtilisateurs actuellement sur le device:")
            if users:
                for user in users:
                    print(f"  - UID {user.uid}: {user.name}")
            else:
                print("  Aucun utilisateur trouvé sur le device")
            print(f"\nVérifications à faire:")
            print(f"  - Assurez-vous que le device ZK est connecté")
            print(f"  - Vérifiez les paramètres de connexion")
            print(f"  - UID #{uid} n'a pas été trouvé sur l'appareil après la tentative de restauration")
    except Exception as e:
        print(f"ERREUR lors de la réactivation: {str(e)}")
        print("Assurez-vous que l'appareil ZK est connecté et que les paramètres sont valides.")

def disable_user_by_day_interactive(conn):
    """Désactiver un utilisateur pour certains jours de la semaine"""
    print("\n=== Désactiver un utilisateur par jour ===")
    
    # Charger les données
    disabled_data = load_disabled_users_data()
    
    # Initialiser la clé pour les restrictions par jour si elle n'existe pas
    if 'day_restrictions' not in disabled_data:
        disabled_data['day_restrictions'] = {}
    
    # Afficher les utilisateurs actifs
    users = conn.get_users()
    
    if not users:
        print("Aucun utilisateur trouvé sur l'appareil.")
        return
    
    print("Utilisateurs actifs sur l'appareil:")
    for user in users:
        print(f"  UID #{user.uid} - {user.name} (User ID: {user.user_id})")
    
    uid = input("\nEntrez l'UID de l'utilisateur: ")
    
    # Trouver l'utilisateur
    target_user = None
    for user in users:
        if str(user.uid) == uid:
            target_user = user
            break
    
    if not target_user:
        print(f"Utilisateur UID #{uid} non trouvé.")
        return
    
    # Afficher les jours de la semaine
    jours = {
        '1': 'Lundi',
        '2': 'Mardi',
        '3': 'Mercredi',
        '4': 'Jeudi',
        '5': 'Vendredi',
        '6': 'Samedi',
        '7': 'Dimanche'
    }
    
    print(f"\nConfiguration pour '{target_user.name}':")
    print("Sélectionnez les jours où l'utilisateur sera DÉSACTIVÉ:")
    for num, jour in jours.items():
        print(f"  {num}. {jour}")
    
    # Vérifier les restrictions existantes
    existing_days = disabled_data['day_restrictions'].get(uid, [])
    if existing_days:
        jours_noms = [jours[str(d)] for d in existing_days if str(d) in jours]
        print(f"\nJours actuellement désactivés: {', '.join(jours_noms)}")
    
    print("\nEntrez les numéros des jours séparés par des virgules (ex: 1,2,3)")
    print("Ou tapez 'aucun' pour supprimer toutes les restrictions")
    
    choix = input("Jours à désactiver: ").strip()
    
    if choix.lower() == 'aucun':
        if uid in disabled_data['day_restrictions']:
            del disabled_data['day_restrictions'][uid]
        save_disabled_users_data(disabled_data)
        print(f"\nToutes les restrictions de jour supprimées pour '{target_user.name}'.")
        return
    
    # Parser les jours sélectionnés
    try:
        jours_selectionnes = [int(j.strip()) for j in choix.split(',') if j.strip()]
        jours_valides = [j for j in jours_selectionnes if 1 <= j <= 7]
        
        if not jours_valides:
            print("Aucun jour valide sélectionné.")
            return
        
        # Sauvegarder les restrictions
        disabled_data['day_restrictions'][uid] = jours_valides
        save_disabled_users_data(disabled_data)
        
        jours_noms = [jours[str(j)] for j in jours_valides]
        print(f"\nUtilisateur '{target_user.name}' sera désactivé les:")
        print(f"  {', '.join(jours_noms)}")
        print("\nNote: Utilisez 'Appliquer restrictions du jour' pour activer/désactiver selon le jour actuel.")
        
    except ValueError:
        print("Format invalide. Utilisez des chiffres séparés par des virgules.")

def apply_day_restrictions(conn):
    """Appliquer les restrictions basées sur le jour actuel"""
    import datetime
    
    print("\n=== Appliquer les restrictions du jour ===")
    
    # Obtenir le jour actuel (1=Lundi, 7=Dimanche)
    jour_actuel = datetime.datetime.now().isoweekday()
    jours = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 5: 'Vendredi', 6: 'Samedi', 7: 'Dimanche'}
    
    print(f"Jour actuel: {jours[jour_actuel]}")
    
    disabled_data = load_disabled_users_data()
    day_restrictions = disabled_data.get('day_restrictions', {})
    
    if not day_restrictions:
        print("Aucune restriction de jour configurée.")
        return
    
    users_to_disable = []
    users_to_enable = []
    
    day_activations = disabled_data.get('day_activations', {})
    
    for uid, jours_desactives in day_restrictions.items():
        if jour_actuel in jours_desactives:
            users_to_disable.append(uid)
        else:
            users_to_enable.append(uid)
    
    # Traiter les activations par jour (l'utilisateur est actif SEULEMENT ces jours)
    for uid, jours_actifs in day_activations.items():
        if jour_actuel not in jours_actifs:
            if uid not in users_to_disable:
                users_to_disable.append(uid)
        else:
            if uid not in users_to_enable:
                users_to_enable.append(uid)
    
    # Désactiver les utilisateurs pour aujourd'hui
    for uid in users_to_disable:
        # Vérifier si l'utilisateur est sur l'appareil
        users = conn.get_users()
        for user in users:
            if str(user.uid) == uid:
                # Sauvegarder et désactiver
                user_data = {
                    'uid': user.uid,
                    'name': user.name,
                    'privilege': user.privilege,
                    'password': user.password,
                    'group_id': user.group_id,
                    'user_id': user.user_id,
                    'card': user.card,
                    'temp_disabled': True
                }
                disabled_data[uid] = user_data
                conn.delete_user(uid=int(uid))
                print(f"  Désactivé: {user.name} (UID #{uid})")
                break
    
    # Réactiver les utilisateurs qui ne doivent pas être désactivés aujourd'hui
    for uid in users_to_enable:
        if uid in disabled_data and disabled_data[uid].get('temp_disabled'):
            user_data = disabled_data[uid]
            try:
                # Convertir group_id correctement
                group_id = user_data['group_id']
                if isinstance(group_id, str) and group_id.strip() == '':
                    group_id = 0
                else:
                    group_id = int(group_id) if group_id else 0
                
                conn.set_user(
                    uid=int(uid),
                    name=user_data['name'],
                    privilege=int(user_data['privilege']),
                    password=user_data['password'],
                    group_id=group_id,
                    user_id=user_data['user_id'],
                    card=int(user_data['card']) if user_data['card'] else 0
                )
                del disabled_data[uid]
                print(f"  Réactivé: {user_data['name']} (UID #{uid})")
            except Exception as e:
                print(f"  ERREUR - Impossible de réactiver {user_data['name']}: {str(e)}")
    
    save_disabled_users_data(disabled_data)
    print("\nRestrictions du jour appliquées.")

def view_day_restrictions():
    """Voir toutes les restrictions"""
    print("\n=== Toutes les restrictions ===")
    
    disabled_data = load_disabled_users_data()
    day_restrictions = disabled_data.get('day_restrictions', {})
    day_activations = disabled_data.get('day_activations', {})
    date_restrictions = disabled_data.get('date_restrictions', {})
    date_activations = disabled_data.get('date_activations', {})
    time_restrictions = disabled_data.get('time_restrictions', {})
    time_activations = disabled_data.get('time_activations', {})
    
    jours = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 5: 'Vendredi', 6: 'Samedi', 7: 'Dimanche'}
    
    has_restrictions = day_restrictions or day_activations or date_restrictions or date_activations or time_restrictions or time_activations
    
    if not has_restrictions:
        print("Aucune restriction configurée.")
        return
    
    if day_restrictions:
        print("\n[JOURS DE SEMAINE - DÉSACTIVÉS]:")
        for uid, jours_desactives in day_restrictions.items():
            jours_noms = [jours[j] for j in jours_desactives]
            print(f"  UID #{uid}: Désactivé les {', '.join(jours_noms)}")
    
    if day_activations:
        print("\n[JOURS DE SEMAINE - ACTIFS uniquement]:")
        for uid, jours_actifs in day_activations.items():
            jours_noms = [jours[j] for j in jours_actifs]
            print(f"  UID #{uid}: Actif uniquement les {', '.join(jours_noms)}")
    
    if date_restrictions:
        print("\n[DATES SPÉCIFIQUES - DÉSACTIVÉS]:")
        for uid, dates in date_restrictions.items():
            print(f"  UID #{uid}: Désactivé les {', '.join(dates)}")
    
    if time_restrictions:
        print("\n[PLAGES HORAIRES - DÉSACTIVÉS]:")
        for uid, horaires in time_restrictions.items():
            print(f"  UID #{uid}:")
            for h in horaires:
                print(f"    - De {h['debut']} à {h['fin']}")
    
    if date_activations:
        print("\n[DATES SPÉCIFIQUES - ACTIFS uniquement]:")
        for uid, dates in date_activations.items():
            print(f"  UID #{uid}: Actif uniquement les {', '.join(dates)}")
    
    if time_activations:
        print("\n[PLAGES HORAIRES - ACTIFS uniquement]:")
        for uid, horaires in time_activations.items():
            print(f"  UID #{uid}:")
            for h in horaires:
                print(f"    - De {h['debut']} à {h['fin']}")

def disable_user_by_date_interactive(conn):
    """Désactiver un utilisateur pour des dates spécifiques de l'année"""
    print("\n=== Désactiver par date spécifique ===")
    
    disabled_data = load_disabled_users_data()
    
    if 'date_restrictions' not in disabled_data:
        disabled_data['date_restrictions'] = {}
    
    users = conn.get_users()
    
    if not users:
        print("Aucun utilisateur trouvé sur l'appareil.")
        return
    
    print("Utilisateurs sur l'appareil:")
    for user in users:
        print(f"  UID #{user.uid} - {user.name}")
    
    uid = input("\nEntrez l'UID de l'utilisateur: ").strip()
    
    target_user = None
    for user in users:
        if str(user.uid) == uid:
            target_user = user
            break
    
    if not target_user:
        print(f"Utilisateur UID #{uid} non trouvé.")
        return
    
    existing_dates = disabled_data['date_restrictions'].get(uid, [])
    if existing_dates:
        print(f"\nDates actuellement désactivées: {', '.join(existing_dates)}")
    
    print(f"\nConfiguration pour '{target_user.name}':")
    print("Options:")
    print("  1. Ajouter des dates")
    print("  2. Supprimer toutes les dates")
    print("  3. Ajouter une plage de dates")
    
    choix = input("Choix [1]: ").strip() or '1'
    
    if choix == '2':
        if uid in disabled_data['date_restrictions']:
            del disabled_data['date_restrictions'][uid]
        save_disabled_users_data(disabled_data)
        print(f"Toutes les restrictions de date supprimées pour '{target_user.name}'.")
        return
    
    if choix == '3':
        print("\nEntrez la plage de dates (format: YYYY-MM-DD)")
        date_debut = input("Date début: ").strip()
        date_fin = input("Date fin: ").strip()
        
        try:
            from datetime import datetime, timedelta
            d1 = datetime.strptime(date_debut, '%Y-%m-%d')
            d2 = datetime.strptime(date_fin, '%Y-%m-%d')
            
            nouvelles_dates = []
            current = d1
            while current <= d2:
                nouvelles_dates.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
            
            if uid not in disabled_data['date_restrictions']:
                disabled_data['date_restrictions'][uid] = []
            
            for d in nouvelles_dates:
                if d not in disabled_data['date_restrictions'][uid]:
                    disabled_data['date_restrictions'][uid].append(d)
            
            disabled_data['date_restrictions'][uid].sort()
            save_disabled_users_data(disabled_data)
            
            print(f"\n{len(nouvelles_dates)} dates ajoutées pour '{target_user.name}'.")
            return
            
        except ValueError:
            print("Format de date invalide.")
            return
    
    # Option 1: Ajouter des dates
    print("\nEntrez les dates séparées par des virgules (format: YYYY-MM-DD)")
    print("Exemple: 2026-03-15, 2026-04-01, 2026-12-25")
    
    dates_input = input("Dates à désactiver: ").strip()
    
    try:
        from datetime import datetime
        dates = [d.strip() for d in dates_input.split(',') if d.strip()]
        
        dates_valides = []
        for d in dates:
            datetime.strptime(d, '%Y-%m-%d')
            dates_valides.append(d)
        
        if uid not in disabled_data['date_restrictions']:
            disabled_data['date_restrictions'][uid] = []
        
        for d in dates_valides:
            if d not in disabled_data['date_restrictions'][uid]:
                disabled_data['date_restrictions'][uid].append(d)
        
        disabled_data['date_restrictions'][uid].sort()
        save_disabled_users_data(disabled_data)
        
        print(f"\nUtilisateur '{target_user.name}' sera désactivé les:")
        print(f"  {', '.join(dates_valides)}")
        
    except ValueError:
        print("Format de date invalide. Utilisez YYYY-MM-DD.")

def disable_user_by_time_interactive(conn):
    """Désactiver un utilisateur pour des plages horaires"""
    print("\n=== Désactiver par plage horaire ===")
    
    disabled_data = load_disabled_users_data()
    
    if 'time_restrictions' not in disabled_data:
        disabled_data['time_restrictions'] = {}
    
    users = conn.get_users()
    
    if not users:
        print("Aucun utilisateur trouvé sur l'appareil.")
        return
    
    print("Utilisateurs sur l'appareil:")
    for user in users:
        print(f"  UID #{user.uid} - {user.name}")
    
    uid = input("\nEntrez l'UID de l'utilisateur: ").strip()
    
    target_user = None
    for user in users:
        if str(user.uid) == uid:
            target_user = user
            break
    
    if not target_user:
        print(f"Utilisateur UID #{uid} non trouvé.")
        return
    
    existing_times = disabled_data['time_restrictions'].get(uid, [])
    if existing_times:
        print(f"\nPlages horaires actuelles:")
        for i, h in enumerate(existing_times, 1):
            print(f"  {i}. De {h['debut']} à {h['fin']}")
    
    print(f"\nConfiguration pour '{target_user.name}':")
    print("Options:")
    print("  1. Ajouter une plage horaire")
    print("  2. Supprimer toutes les plages")
    
    choix = input("Choix [1]: ").strip() or '1'
    
    if choix == '2':
        if uid in disabled_data['time_restrictions']:
            del disabled_data['time_restrictions'][uid]
        save_disabled_users_data(disabled_data)
        print(f"Toutes les restrictions horaires supprimées pour '{target_user.name}'.")
        return
    
    print("\nEntrez la plage horaire (format: HH:MM)")
    print("L'utilisateur sera DÉSACTIVÉ pendant cette plage.")
    
    heure_debut = input("Heure début (ex: 12:00): ").strip()
    heure_fin = input("Heure fin (ex: 14:00): ").strip()
    
    try:
        from datetime import datetime
        datetime.strptime(heure_debut, '%H:%M')
        datetime.strptime(heure_fin, '%H:%M')
        
        if uid not in disabled_data['time_restrictions']:
            disabled_data['time_restrictions'][uid] = []
        
        disabled_data['time_restrictions'][uid].append({
            'debut': heure_debut,
            'fin': heure_fin
        })
        
        save_disabled_users_data(disabled_data)
        
        print(f"\n✓ Restriction horaire sauvegardée!")
        print(f"  Utilisateur: '{target_user.name}'")
        print(f"  Désactivé de: {heure_debut} à {heure_fin}")
        print(f"\n⚠️  IMPORTANT: Les restrictions ne sont PAS encore actives!")
        print(f"  Pour ACTIVER cette restriction, vous DEVEZ:")
        print(f"    → Retourner au MENU PRINCIPAL")
        print(f"    → Sélectionner l'option: 13 - Appliquer toutes les restrictions")
        print(f"\n  Cela va désactiver/réactiver les utilisateurs selon l'heure actuelle.")
        
    except ValueError:
        print("Format d'heure invalide. Utilisez HH:MM.")

def apply_all_restrictions(conn):
    """Appliquer toutes les restrictions (jour, date, heure)"""
    from datetime import datetime
    
    print("\n=== Appliquer toutes les restrictions ===")
    
    now = datetime.now()
    jour_actuel = now.isoweekday()
    date_actuelle = now.strftime('%Y-%m-%d')
    heure_actuelle = now.strftime('%H:%M')
    
    jours = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 5: 'Vendredi', 6: 'Samedi', 7: 'Dimanche'}
    
    print(f"Date: {date_actuelle} ({jours[jour_actuel]})")
    print(f"Heure: {heure_actuelle}")
    
    disabled_data = load_disabled_users_data()
    day_restrictions = disabled_data.get('day_restrictions', {})
    day_activations = disabled_data.get('day_activations', {})
    date_restrictions = disabled_data.get('date_restrictions', {})
    date_activations = disabled_data.get('date_activations', {})
    time_restrictions = disabled_data.get('time_restrictions', {})
    time_activations = disabled_data.get('time_activations', {})
    
    users_to_disable = set()
    users_to_enable = set()
    
    # Vérifier restrictions par jour de semaine
    for uid, jours_desactives in day_restrictions.items():
        if jour_actuel in jours_desactives:
            users_to_disable.add(uid)
        else:
            users_to_enable.add(uid)
    
    # Vérifier activations par jour (actif SEULEMENT ces jours)
    for uid, jours_actifs in day_activations.items():
        if jour_actuel not in jours_actifs:
            users_to_disable.add(uid)
        else:
            users_to_enable.add(uid)
    
    # Vérifier restrictions par date
    for uid, dates in date_restrictions.items():
        if date_actuelle in dates:
            users_to_disable.add(uid)
            users_to_enable.discard(uid)
    
    # Vérifier activations par date (actif SEULEMENT ces dates)
    for uid, dates in date_activations.items():
        if date_actuelle not in dates:
            users_to_disable.add(uid)
            users_to_enable.discard(uid)
        else:
            users_to_enable.add(uid)
    
    # Vérifier restrictions par heure
    for uid, horaires in time_restrictions.items():
        for h in horaires:
            if h['debut'] <= heure_actuelle <= h['fin']:
                users_to_disable.add(uid)
                users_to_enable.discard(uid)
                break
    
    # Vérifier activations par heure (actif SEULEMENT pendant ces plages)
    for uid, horaires in time_activations.items():
        is_active_time = False
        for h in horaires:
            if h['debut'] <= heure_actuelle <= h['fin']:
                is_active_time = True
                break
        if not is_active_time:
            users_to_disable.add(uid)
            users_to_enable.discard(uid)
        else:
            users_to_enable.add(uid)
    
    # Enlever de enable ceux qui doivent être disabled
    users_to_enable -= users_to_disable
    
    # Désactiver les utilisateurs
    for uid in users_to_disable:
        users = conn.get_users()
        for user in users:
            if str(user.uid) == uid:
                user_data = {
                    'uid': user.uid,
                    'name': user.name,
                    'privilege': user.privilege,
                    'password': user.password,
                    'group_id': user.group_id,
                    'user_id': user.user_id,
                    'card': user.card,
                    'temp_disabled': True
                }
                disabled_data[uid] = user_data
                conn.delete_user(uid=int(uid))
                print(f"  Désactivé: {user.name} (UID #{uid})")
                break
    
    # Réactiver les utilisateurs qui ne doivent pas être désactivés
    for uid in users_to_enable:
        if uid in disabled_data and disabled_data[uid].get('temp_disabled'):
            user_data = disabled_data[uid]
            try:
                # Convertir group_id correctement
                group_id = user_data['group_id']
                if isinstance(group_id, str) and group_id.strip() == '':
                    group_id = 0
                else:
                    group_id = int(group_id) if group_id else 0
                
                conn.set_user(
                    uid=int(uid),
                    name=user_data['name'],
                    privilege=int(user_data['privilege']),
                    password=user_data['password'],
                    group_id=group_id,
                    user_id=user_data['user_id'],
                    card=int(user_data['card']) if user_data['card'] else 0
                )
                del disabled_data[uid]
                print(f"  Réactivé: {user_data['name']} (UID #{uid})")
            except Exception as e:
                print(f"  ERREUR - Impossible de réactiver {user_data['name']}: {str(e)}")
    
    save_disabled_users_data(disabled_data)
    print("\nRestrictions appliquées.")

def enable_user_by_day_interactive(conn):
    """Réactiver un utilisateur pour certains jours de la semaine uniquement"""
    print("\n=== Réactiver un utilisateur par jour ===")
    
    # Charger les données
    disabled_data = load_disabled_users_data()
    
    # Initialiser la clé pour les activations par jour si elle n'existe pas
    if 'day_activations' not in disabled_data:
        disabled_data['day_activations'] = {}
    
    # Afficher les utilisateurs (actifs + désactivés)
    users = conn.get_users()
    
    print("Utilisateurs sur l'appareil:")
    for user in users:
        print(f"  UID #{user.uid} - {user.name} (User ID: {user.user_id})")
    
    # Afficher aussi les utilisateurs désactivés
    disabled_users = {k: v for k, v in disabled_data.items() 
                      if k not in ['day_restrictions', 'day_activations'] and isinstance(v, dict) and 'name' in v}
    if disabled_users:
        print("\nUtilisateurs désactivés (sauvegardés):")
        for uid, user_data in disabled_users.items():
            print(f"  UID #{uid} - {user_data['name']} (User ID: {user_data['user_id']})")
    
    uid = input("\nEntrez l'UID de l'utilisateur: ")
    
    # Trouver l'utilisateur (actif ou désactivé)
    target_user = None
    user_name = None
    
    for user in users:
        if str(user.uid) == uid:
            target_user = user
            user_name = user.name
            break
    
    if not target_user and uid in disabled_users:
        user_name = disabled_users[uid]['name']
    
    if not user_name:
        print(f"Utilisateur UID #{uid} non trouvé.")
        return
    
    # Afficher les jours de la semaine
    jours = {
        '1': 'Lundi',
        '2': 'Mardi',
        '3': 'Mercredi',
        '4': 'Jeudi',
        '5': 'Vendredi',
        '6': 'Samedi',
        '7': 'Dimanche'
    }
    
    print(f"\nConfiguration pour '{user_name}':")
    print("Sélectionnez les jours où l'utilisateur sera ACTIF:")
    for num, jour in jours.items():
        print(f"  {num}. {jour}")
    
    # Vérifier les activations existantes
    existing_days = disabled_data['day_activations'].get(uid, [])
    if existing_days:
        jours_noms = [jours[str(d)] for d in existing_days if str(d) in jours]
        print(f"\nJours actuellement actifs: {', '.join(jours_noms)}")
    
    print("\nEntrez les numéros des jours séparés par des virgules (ex: 1,2,3,4,5 pour jours ouvrables)")
    print("Ou tapez 'tous' pour supprimer les restrictions (actif tous les jours)")
    
    choix = input("Jours à activer: ").strip()
    
    if choix.lower() == 'tous':
        if uid in disabled_data['day_activations']:
            del disabled_data['day_activations'][uid]
        save_disabled_users_data(disabled_data)
        print(f"\nRestrictions supprimées - '{user_name}' sera actif tous les jours.")
        return
    
    # Parser les jours sélectionnés
    try:
        jours_selectionnes = [int(j.strip()) for j in choix.split(',') if j.strip()]
        jours_valides = [j for j in jours_selectionnes if 1 <= j <= 7]
        
        if not jours_valides:
            print("Aucun jour valide sélectionné.")
            return
        
        # Sauvegarder les activations
        disabled_data['day_activations'][uid] = jours_valides
        
        # Supprimer les restrictions de désactivation si elles existent (éviter conflit)
        if 'day_restrictions' in disabled_data and uid in disabled_data['day_restrictions']:
            del disabled_data['day_restrictions'][uid]
        
        save_disabled_users_data(disabled_data)
        
        jours_noms = [jours[str(j)] for j in jours_valides]
        print(f"\nUtilisateur '{user_name}' sera ACTIF uniquement les:")
        print(f"  {', '.join(jours_noms)}")
        print("\nNote: Utilisez 'Appliquer restrictions du jour' pour activer/désactiver selon le jour actuel.")
        
    except ValueError:
        print("Format invalide. Utilisez des chiffres séparés par des virgules.")

def enable_user_by_date_interactive(conn):
    """Réactiver un utilisateur pour des dates spécifiques uniquement"""
    print("\n=== Réactiver par date spécifique ===")
    
    disabled_data = load_disabled_users_data()
    
    if 'date_activations' not in disabled_data:
        disabled_data['date_activations'] = {}
    
    users = conn.get_users()
    
    if not users:
        print("Aucun utilisateur trouvé sur l'appareil.")
        return
    
    print("Utilisateurs sur l'appareil:")
    for user in users:
        print(f"  UID #{user.uid} - {user.name}")
    
    # Afficher aussi les utilisateurs désactivés
    disabled_users = {k: v for k, v in disabled_data.items() 
                      if k not in ['day_restrictions', 'day_activations', 'date_restrictions', 'date_activations', 'time_restrictions', 'time_activations'] 
                      and isinstance(v, dict) and 'name' in v}
    if disabled_users:
        print("\nUtilisateurs désactivés:")
        for uid, user_data in disabled_users.items():
            print(f"  UID #{uid} - {user_data['name']}")
    
    uid = input("\nEntrez l'UID de l'utilisateur: ").strip()
    
    target_user = None
    user_name = None
    for user in users:
        if str(user.uid) == uid:
            target_user = user
            user_name = user.name
            break
    
    if not target_user and uid in disabled_users:
        user_name = disabled_users[uid]['name']
    
    if not user_name:
        print(f"Utilisateur UID #{uid} non trouvé.")
        return
    
    existing_dates = disabled_data['date_activations'].get(uid, [])
    if existing_dates:
        print(f"\nDates actuellement actives: {', '.join(existing_dates)}")
    
    print(f"\nConfiguration pour '{user_name}':")
    print("L'utilisateur sera ACTIF UNIQUEMENT ces dates.")
    print("Options:")
    print("  1. Ajouter des dates")
    print("  2. Supprimer toutes les restrictions (actif tous les jours)")
    print("  3. Ajouter une plage de dates")
    
    choix = input("Choix [1]: ").strip() or '1'
    
    if choix == '2':
        if uid in disabled_data['date_activations']:
            del disabled_data['date_activations'][uid]
        # Supprimer aussi les restrictions de désactivation
        if 'date_restrictions' in disabled_data and uid in disabled_data['date_restrictions']:
            del disabled_data['date_restrictions'][uid]
        save_disabled_users_data(disabled_data)
        print(f"Restrictions de date supprimées pour '{user_name}'.")
        return
    
    if choix == '3':
        print("\nEntrez la plage de dates (format: YYYY-MM-DD)")
        date_debut = input("Date début: ").strip()
        date_fin = input("Date fin: ").strip()
        
        try:
            from datetime import datetime, timedelta
            d1 = datetime.strptime(date_debut, '%Y-%m-%d')
            d2 = datetime.strptime(date_fin, '%Y-%m-%d')
            
            nouvelles_dates = []
            current = d1
            while current <= d2:
                nouvelles_dates.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
            
            if uid not in disabled_data['date_activations']:
                disabled_data['date_activations'][uid] = []
            
            for d in nouvelles_dates:
                if d not in disabled_data['date_activations'][uid]:
                    disabled_data['date_activations'][uid].append(d)
            
            disabled_data['date_activations'][uid].sort()
            
            # Supprimer les restrictions de désactivation
            if 'date_restrictions' in disabled_data and uid in disabled_data['date_restrictions']:
                del disabled_data['date_restrictions'][uid]
            
            save_disabled_users_data(disabled_data)
            
            print(f"\n{len(nouvelles_dates)} dates ajoutées. '{user_name}' sera ACTIF uniquement ces jours.")
            return
            
        except ValueError:
            print("Format de date invalide.")
            return
    
    # Option 1: Ajouter des dates
    print("\nEntrez les dates séparées par des virgules (format: YYYY-MM-DD)")
    print("Exemple: 2026-03-15, 2026-04-01, 2026-12-25")
    
    dates_input = input("Dates actives: ").strip()
    
    try:
        from datetime import datetime
        dates = [d.strip() for d in dates_input.split(',') if d.strip()]
        
        dates_valides = []
        for d in dates:
            datetime.strptime(d, '%Y-%m-%d')
            dates_valides.append(d)
        
        if uid not in disabled_data['date_activations']:
            disabled_data['date_activations'][uid] = []
        
        for d in dates_valides:
            if d not in disabled_data['date_activations'][uid]:
                disabled_data['date_activations'][uid].append(d)
        
        disabled_data['date_activations'][uid].sort()
        
        # Supprimer les restrictions de désactivation
        if 'date_restrictions' in disabled_data and uid in disabled_data['date_restrictions']:
            del disabled_data['date_restrictions'][uid]
        
        save_disabled_users_data(disabled_data)
        
        print(f"\nUtilisateur '{user_name}' sera ACTIF uniquement les:")
        print(f"  {', '.join(dates_valides)}")
        
    except ValueError:
        print("Format de date invalide. Utilisez YYYY-MM-DD.")

def enable_user_by_time_interactive(conn):
    """Réactiver un utilisateur pour des plages horaires spécifiques uniquement"""
    print("\n=== Réactiver par plage horaire ===")
    
    disabled_data = load_disabled_users_data()
    
    if 'time_activations' not in disabled_data:
        disabled_data['time_activations'] = {}
    
    users = conn.get_users()
    
    if not users:
        print("Aucun utilisateur trouvé sur l'appareil.")
        return
    
    print("Utilisateurs sur l'appareil:")
    for user in users:
        print(f"  UID #{user.uid} - {user.name}")
    
    # Afficher aussi les utilisateurs désactivés
    disabled_users = {k: v for k, v in disabled_data.items() 
                      if k not in ['day_restrictions', 'day_activations', 'date_restrictions', 'date_activations', 'time_restrictions', 'time_activations'] 
                      and isinstance(v, dict) and 'name' in v}
    if disabled_users:
        print("\nUtilisateurs désactivés:")
        for uid, user_data in disabled_users.items():
            print(f"  UID #{uid} - {user_data['name']}")
    
    uid = input("\nEntrez l'UID de l'utilisateur: ").strip()
    
    target_user = None
    user_name = None
    for user in users:
        if str(user.uid) == uid:
            target_user = user
            user_name = user.name
            break
    
    if not target_user and uid in disabled_users:
        user_name = disabled_users[uid]['name']
    
    if not user_name:
        print(f"Utilisateur UID #{uid} non trouvé.")
        return
    
    existing_times = disabled_data['time_activations'].get(uid, [])
    if existing_times:
        print(f"\nPlages horaires actives:")
        for i, h in enumerate(existing_times, 1):
            print(f"  {i}. De {h['debut']} à {h['fin']}")
    
    print(f"\nConfiguration pour '{user_name}':")
    print("L'utilisateur sera ACTIF UNIQUEMENT pendant ces plages horaires.")
    print("Options:")
    print("  1. Ajouter une plage horaire")
    print("  2. Supprimer toutes les restrictions (actif toute la journée)")
    
    choix = input("Choix [1]: ").strip() or '1'
    
    if choix == '2':
        if uid in disabled_data['time_activations']:
            del disabled_data['time_activations'][uid]
        # Supprimer aussi les restrictions de désactivation
        if 'time_restrictions' in disabled_data and uid in disabled_data['time_restrictions']:
            del disabled_data['time_restrictions'][uid]
        save_disabled_users_data(disabled_data)
        print(f"Restrictions horaires supprimées pour '{user_name}'.")
        return
    
    print("\nEntrez la plage horaire (format: HH:MM)")
    print("L'utilisateur sera ACTIF uniquement pendant cette plage.")
    print("Exemple: 08:00 à 18:00 pour les heures de travail")
    
    heure_debut = input("Heure début (ex: 08:00): ").strip()
    heure_fin = input("Heure fin (ex: 18:00): ").strip()
    
    try:
        from datetime import datetime
        datetime.strptime(heure_debut, '%H:%M')
        datetime.strptime(heure_fin, '%H:%M')
        
        if uid not in disabled_data['time_activations']:
            disabled_data['time_activations'][uid] = []
        
        disabled_data['time_activations'][uid].append({
            'debut': heure_debut,
            'fin': heure_fin
        })
        
        # Supprimer les restrictions de désactivation
        if 'time_restrictions' in disabled_data and uid in disabled_data['time_restrictions']:
            del disabled_data['time_restrictions'][uid]
        
        save_disabled_users_data(disabled_data)
        
        print(f"\n✓ Activation horaire sauvegardée!")
        print(f"  Utilisateur: '{user_name}'")
        print(f"  ACTIF UNIQUEMENT de: {heure_debut} à {heure_fin}")
        print(f"\n⚠️  IMPORTANT: Les restrictions ne sont PAS encore actives!")
        print(f"  Pour ACTIVER cette restriction, vous DEVEZ:")
        print(f"    → Retourner au MENU PRINCIPAL")
        print(f"    → Sélectionner l'option: 13 - Appliquer toutes les restrictions")
        print(f"\n  Cela va désactiver/réactiver les utilisateurs selon l'heure actuelle.")
        
    except ValueError:
        print("Format d'heure invalide. Utilisez HH:MM.")

def modify_user_interactive(conn):
    """Modifier un utilisateur existant"""
    print("\n=== Modifier un utilisateur ===")
    
    # Afficher la liste des utilisateurs
    users = conn.get_users()
    
    if not users:
        print("Aucun utilisateur trouvé.")
        return
    
    print("Utilisateurs disponibles:")
    for user in users:
        print(f"  UID #{user.uid} - {user.name} (User ID: {user.user_id})")
    
    uid = int(input("\nEntrez l'UID de l'utilisateur à modifier: "))
    
    # Trouver l'utilisateur
    target_user = None
    for user in users:
        if user.uid == uid:
            target_user = user
            break
    
    if not target_user:
        print(f"Utilisateur UID #{uid} non trouvé.")
        return
    
    print(f"\nUtilisateur actuel:")
    print(f"  Nom        : {target_user.name}")
    print(f"  User ID    : {target_user.user_id}")
    print(f"  Privilège  : {target_user.privilege} (0=User, 14=Admin)")
    print(f"  Mot de passe: {target_user.password if target_user.password else '(aucun)'}")
    print(f"  Group ID   : {target_user.group_id if target_user.group_id else '(aucun)'}")
    print(f"  Carte      : {target_user.card if target_user.card else '(aucune)'}")
    
    print("\n(Laissez vide pour garder la valeur actuelle)")
    
    # Demander les nouvelles valeurs
    new_name = input(f"Nouveau nom [{target_user.name}]: ")
    new_name = new_name if new_name else target_user.name
    
    new_user_id = input(f"Nouveau User ID [{target_user.user_id}]: ")
    new_user_id = new_user_id if new_user_id else target_user.user_id
    
    new_password = input(f"Nouveau mot de passe [{target_user.password}]: ")
    new_password = new_password if new_password else target_user.password
    
    priv_input = input(f"Nouveau privilège (0=User, 14=Admin) [{target_user.privilege}]: ")
    new_privilege = int(priv_input) if priv_input else target_user.privilege
    
    new_group_id = input(f"Nouveau Group ID [{target_user.group_id}]: ")
    new_group_id = new_group_id if new_group_id else target_user.group_id
    
    card_input = input(f"Nouveau numéro de carte [{target_user.card}]: ")
    new_card = int(card_input) if card_input else target_user.card
    
    # Appliquer les modifications
    conn.set_user(
        uid=target_user.uid,
        name=new_name,
        privilege=new_privilege,
        password=new_password,
        group_id=new_group_id,
        user_id=new_user_id,
        card=new_card
    )
    print(f"\nUtilisateur '{new_name}' modifié avec succès!")

def get_device_info(conn):
    """Afficher les informations du dispositif"""
    print("\n" + "="*50)
    print("         INFORMATIONS DU DISPOSITIF")
    print("="*50)
    print(f"Nom du dispositif : {conn.get_device_name()}")
    print(f"Numéro de série   : {conn.get_serialnumber()}")
    print(f"Version firmware  : {conn.get_firmware_version()}")
    print(f"Plateforme        : {conn.get_platform()}")
    print(f"Adresse MAC       : {conn.get_mac()}")
    print("="*50)

def sync_attendance_to_json(conn):
    """Synchroniser tous les pointages de l'appareil vers le fichier JSON"""
    print("\n=== Synchronisation des pointages ===")
    
    # Récupérer tous les pointages de l'appareil
    attendance = conn.get_attendance()
    
    if not attendance:
        print("Aucun pointage trouvé sur l'appareil.")
        return
    
    # Récupérer les utilisateurs pour avoir les noms
    users = conn.get_users()
    user_map = {str(user.uid): user.name for user in users}
    
    # Charger les données existantes
    attendance_data = load_attendance_data()
    
    new_records = 0
    
    for record in attendance:
        uid = str(record.user_id)
        
        # Initialiser la liste pour cet utilisateur si nécessaire
        if uid not in attendance_data:
            attendance_data[uid] = {
                'name': user_map.get(uid, f'Utilisateur #{uid}'),
                'records': []
            }
        
        # Créer l'enregistrement de pointage
        timestamp = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        # Types de pointage ZK
        punch_types = {
            0: 'Entrée',
            1: 'Sortie',
            2: 'Pause début',
            3: 'Pause fin',
            4: 'HS entrée',
            5: 'HS sortie'
        }
        punch_type = punch_types.get(record.punch, f'Type {record.punch}')
        
        pointage = {
            'timestamp': timestamp,
            'date': record.timestamp.strftime('%Y-%m-%d'),
            'heure': record.timestamp.strftime('%H:%M:%S'),
            'type': punch_type,
            'type_code': record.punch,
            'status': record.status
        }
        
        # Vérifier si ce pointage existe déjà
        exists = any(
            p['timestamp'] == timestamp 
            for p in attendance_data[uid]['records']
        )
        
        if not exists:
            attendance_data[uid]['records'].append(pointage)
            new_records += 1
    
    # Trier les enregistrements par date/heure
    for uid in attendance_data:
        attendance_data[uid]['records'].sort(key=lambda x: x['timestamp'])
    
    # Sauvegarder
    save_attendance_data(attendance_data)
    
    print(f"Synchronisation terminée!")
    print(f"  - Total pointages sur l'appareil: {len(attendance)}")
    print(f"  - Nouveaux pointages ajoutés: {new_records}")
    print(f"  - Fichier: {ATTENDANCE_FILE}")

def get_user_attendance(conn):
    """Afficher les pointages d'un utilisateur spécifique"""
    print("\n=== Pointages d'un utilisateur ===")
    
    # D'abord synchroniser les données
    print("Synchronisation des données...")
    sync_attendance_to_json(conn)
    
    # Charger les données
    attendance_data = load_attendance_data()
    
    if not attendance_data:
        print("Aucun pointage enregistré.")
        return
    
    # Afficher les utilisateurs disponibles
    print("\nUtilisateurs avec pointages:")
    for uid, data in attendance_data.items():
        nb_records = len(data['records'])
        print(f"  UID #{uid} - {data['name']} ({nb_records} pointages)")
    
    uid = input("\nEntrez l'UID de l'utilisateur: ").strip()
    
    if uid not in attendance_data:
        print(f"Aucun pointage trouvé pour l'UID #{uid}.")
        return
    
    user_data = attendance_data[uid]
    records = user_data['records']
    
    print(f"\n" + "="*60)
    print(f"  POINTAGES DE: {user_data['name']} (UID #{uid})")
    print("="*60)
    
    # Option de filtrage par date
    print("\nOptions de filtrage:")
    print("  1. Tous les pointages")
    print("  2. Aujourd'hui")
    print("  3. Derniers 7 jours")
    print("  4. Date spécifique")
    print("  5. Plage de dates")
    
    filtre = input("Choix [1]: ").strip() or '1'
    
    today = datetime.now().strftime('%Y-%m-%d')
    filtered_records = []
    
    if filtre == '1':
        filtered_records = records
    elif filtre == '2':
        filtered_records = [r for r in records if r['date'] == today]
    elif filtre == '3':
        from datetime import timedelta
        date_limite = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        filtered_records = [r for r in records if r['date'] >= date_limite]
    elif filtre == '4':
        date_spec = input("Entrez la date (YYYY-MM-DD): ").strip()
        filtered_records = [r for r in records if r['date'] == date_spec]
    elif filtre == '5':
        date_debut = input("Date début (YYYY-MM-DD): ").strip()
        date_fin = input("Date fin (YYYY-MM-DD): ").strip()
        filtered_records = [r for r in records if date_debut <= r['date'] <= date_fin]
    else:
        filtered_records = records
    
    if not filtered_records:
        print("\nAucun pointage trouvé pour ce filtre.")
        return
    
    print(f"\nTotal: {len(filtered_records)} pointage(s)\n")
    print("-"*60)
    print(f"{'Date':<12} {'Heure':<10} {'Type':<15}")
    print("-"*60)
    
    for record in filtered_records:
        print(f"{record['date']:<12} {record['heure']:<10} {record['type']:<15}")
    
    print("-"*60)

def view_all_attendance_from_json():
    """Voir tous les pointages depuis le fichier JSON (sans connexion)"""
    print("\n=== Tous les pointages (depuis JSON) ===")
    
    attendance_data = load_attendance_data()
    
    if not attendance_data:
        print("Aucun pointage enregistré dans le fichier JSON.")
        print(f"Fichier: {ATTENDANCE_FILE}")
        return
    
    print(f"\nUtilisateurs enregistrés: {len(attendance_data)}\n")
    
    for uid, data in attendance_data.items():
        records = data['records']
        print(f"\n{'='*60}")
        print(f"  {data['name']} (UID #{uid}) - {len(records)} pointage(s)")
        print("="*60)
        
        if records:
            # Afficher les 10 derniers pointages
            derniers = records[-10:]
            print(f"{'Date':<12} {'Heure':<10} {'Type':<15}")
            print("-"*40)
            for record in derniers:
                print(f"{record['date']:<12} {record['heure']:<10} {record['type']:<15}")
            
            if len(records) > 10:
                print(f"\n... et {len(records) - 10} autres pointages")

def main_menu():
    print("\n" + "="*50)
    print("            MENU PRINCIPAL")
    print("="*50)
    print("1. Ajouter un utilisateur")
    print("2. Lister tous les utilisateurs")
    print("3. Modifier un utilisateur")
    print("4. Supprimer un utilisateur")
    print("5. Désactiver un utilisateur")
    print("6. Réactiver un utilisateur")
    print("--- RESTRICTIONS ---")
    print("7. Désactiver par jour de la semaine")
    print("8. Réactiver par jour de la semaine")
    print("9. Désactiver par date")
    print("10. Réactiver par date")
    print("11. Désactiver par plage horaire")
    print("12. Réactiver par plage horaire")
    print("13. Appliquer toutes les restrictions")
    print("14. Voir toutes les restrictions")
    print("--- POINTAGES ---")
    print("15. Pointages d'un utilisateur")
    print("16. Voir tous les pointages (JSON)")
    print("17. Synchroniser pointages")
    print("--- AUTRES ---")
    print("18. Informations du dispositif")
    print("19. Quitter")
    print("="*50)
    return input("Choisissez une option: ")

conn = None
zk = ZK('10.0.22.56', port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)

try:
    conn = zk.connect()
    conn.disable_device()
    print("Connexion réussie au dispositif ZK!")
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            add_user_interactive(conn)
        elif choice == '2':
            list_users(conn)
        elif choice == '3':
            modify_user_interactive(conn)
        elif choice == '4':
            delete_user_interactive(conn)
        elif choice == '5':
            disable_user_interactive(conn)
        elif choice == '6':
            enable_user_interactive(conn)
        elif choice == '7':
            disable_user_by_day_interactive(conn)
        elif choice == '8':
            enable_user_by_day_interactive(conn)
        elif choice == '9':
            disable_user_by_date_interactive(conn)
        elif choice == '10':
            enable_user_by_date_interactive(conn)
        elif choice == '11':
            disable_user_by_time_interactive(conn)
        elif choice == '12':
            enable_user_by_time_interactive(conn)
        elif choice == '13':
            apply_all_restrictions(conn)
        elif choice == '14':
            view_day_restrictions()
        elif choice == '15':
            get_user_attendance(conn)
        elif choice == '16':
            view_all_attendance_from_json()
        elif choice == '17':
            sync_attendance_to_json(conn)
        elif choice == '18':
            get_device_info(conn)
        elif choice == '19':
            print("Au revoir!")
            break
        else:
            print("Option invalide, veuillez réessayer.")
        
        # Retour au menu après chaque option (sauf Quitter)
        if choice != '19':
            input("\n" + "="*50 + "\nAppuyez sur ENTRÉE pour revenir au menu principal...")

    
    conn.test_voice()
    conn.enable_device()
    
except Exception as e:
    print(f"Erreur: {e}")
finally:
    if conn:
        conn.disconnect()