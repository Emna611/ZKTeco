# ZK Teco - Gestion de Présence

Ce projet fournit une interface Python complète en ligne de commande pour gérer les utilisateurs, les restrictions d'accès et les pointages depuis les appareils biométriques ZKTeco/ZKBio.

## 📋 Description

Ce projet permet de :

- Gérer les utilisateurs (ajout, modification, suppression, activation/désactivation)
- Configurer des **restrictions d'accès** par jour de semaine, date spécifique et plage horaire
- Synchroniser et consulter les **pointages** (entrées/sorties) depuis l'appareil vers un fichier JSON
- Sauvegarder les données des utilisateurs désactivés pour une réactivation future
- Afficher les informations du dispositif ZKTeco

## 📁 Structure du Projet

```
├── attendance.json              # Données de pointage synchronisées (entrée/sortie)
├── disabled_users.json          # Utilisateurs désactivés + restrictions configurées
├── from zk import ZK, const.py  # Script principal de gestion ZK
└── README.md                    # Documentation du projet
```

## 🚀 Installation

### Prérequis

- Python 3.11+
- Bibliothèque `pyzk`
- Un appareil ZKTeco connecté au réseau (même sous-réseau)

### Appareils compatibles

La bibliothèque `pyzk` est compatible avec la majorité des terminaux ZKTeco utilisant le protocole ZK sur le port **4370** :

- ZKBio CVSecurity
- iClock (iClock 880, iClock 360, etc.)
- K-series (K40, K20, etc.)
- F-series (F18, F22, etc.)
- uFace (uFace 800, uFace 402, etc.)
- SpeedFace
- Tout appareil ZKTeco communiquant via UDP/TCP port 4370

### Setup

```bash
# Cloner le dépôt
git clone https://github.com/Emna611/ZKTeco.git

# Accéder au répertoire
cd ZKTeco

# Installer les dépendances
pip install pyzk
```

### Configuration réseau

Le script se connecte à l'appareil via l'adresse IP configurée dans le code :

```python
zk = ZK('10.0.22.56', port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)
```

> **⚠️ Important** : Modifiez l'adresse IP `10.0.22.56` par celle de votre appareil ZKTeco. Vous pouvez la trouver dans le menu réseau de l'appareil (Menu > Comm. > Ethernet).

## 💻 Utilisation

```bash
python "from zk import ZK, const.py"
```

Au lancement, le script se connecte à l'appareil et affiche un **menu principal interactif** avec 19 options.

## 📋 Menu Principal

```
==================================================
            MENU PRINCIPAL
==================================================
1.  Ajouter un utilisateur
2.  Lister tous les utilisateurs
3.  Modifier un utilisateur
4.  Supprimer un utilisateur
5.  Désactiver un utilisateur
6.  Réactiver un utilisateur
--- RESTRICTIONS ---
7.  Désactiver par jour de la semaine
8.  Réactiver par jour de la semaine
9.  Désactiver par date
10. Réactiver par date
11. Désactiver par plage horaire
12. Réactiver par plage horaire
13. Appliquer toutes les restrictions
14. Voir toutes les restrictions
--- POINTAGES ---
15. Pointages d'un utilisateur
16. Voir tous les pointages (JSON)
17. Synchroniser pointages
--- AUTRES ---
18. Informations du dispositif
19. Quitter
==================================================
```

## 🔧 Fonctionnalités détaillées

### 👤 Gestion des utilisateurs (Options 1-6)

| Option | Fonction | Description |
|--------|----------|-------------|
| **1** | Ajouter un utilisateur | Créer un nouvel utilisateur avec UID, nom, ID, mot de passe, privilège (User/Admin), Group ID et carte |
| **2** | Lister les utilisateurs | Afficher tous les utilisateurs enregistrés sur l'appareil avec leurs détails |
| **3** | Modifier un utilisateur | Modifier les informations d'un utilisateur existant (nom, ID, mot de passe, privilège, etc.) |
| **4** | Supprimer un utilisateur | Supprimer définitivement un utilisateur de l'appareil |
| **5** | Désactiver un utilisateur | Supprimer l'utilisateur de l'appareil **en sauvegardant ses données** dans `disabled_users.json` pour réactivation future |
| **6** | Réactiver un utilisateur | Restaurer un utilisateur désactivé sur l'appareil depuis la sauvegarde JSON |

> **Note** : La désactivation (option 5) est différente de la suppression (option 4). La désactivation sauvegarde les données, la suppression est définitive.

### ⏰ Restrictions d'accès (Options 7-14)

#### Par jour de la semaine (Options 7-8)

- **Option 7** : Choisir les jours où un utilisateur sera **DÉSACTIVÉ** (ex: désactiver le samedi et dimanche)
- **Option 8** : Choisir les jours où un utilisateur sera **ACTIF UNIQUEMENT** (ex: actif uniquement du lundi au vendredi)

```
Jours disponibles :
  1. Lundi    2. Mardi    3. Mercredi    4. Jeudi
  5. Vendredi 6. Samedi   7. Dimanche
Saisie : 1,2,3,4,5  (pour les jours ouvrables)
```

#### Par date spécifique (Options 9-10)

- **Option 9** : Désactiver un utilisateur à des dates précises (ex: jours fériés, congés)
- **Option 10** : Activer un utilisateur UNIQUEMENT à certaines dates

Formats supportés :
- Dates individuelles : `2026-03-15, 2026-04-01, 2026-12-25`
- Plage de dates : date début → date fin

#### Par plage horaire (Options 11-12)

- **Option 11** : Désactiver un utilisateur pendant une plage horaire (ex: de 12:00 à 14:00)
- **Option 12** : Activer un utilisateur UNIQUEMENT pendant une plage horaire (ex: de 08:00 à 18:00)

Format : `HH:MM` (ex: 08:00 à 18:00)

#### Appliquer les restrictions (Option 13)

**⚠️ Important** : Les restrictions configurées (options 7-12) ne sont **pas appliquées automatiquement**. Il faut utiliser l'option **13** pour les activer/désactiver selon la date et l'heure actuelles.

Cette option :
1. Vérifie le jour, la date et l'heure actuels
2. Désactive les utilisateurs qui ont des restrictions actives
3. Réactive les utilisateurs temporairement désactivés dont les restrictions ne s'appliquent plus

#### Voir les restrictions (Option 14)

Affiche un résumé de toutes les restrictions configurées :
- Jours de semaine désactivés/activés
- Dates spécifiques désactivées/activées
- Plages horaires désactivées/activées

### 📊 Pointages (Options 15-17)

| Option | Fonction | Description |
|--------|----------|-------------|
| **15** | Pointages d'un utilisateur | Afficher les pointages d'un utilisateur avec filtres (aujourd'hui, 7 jours, date, plage) |
| **16** | Voir tous les pointages | Afficher tous les pointages depuis le fichier JSON (10 derniers par utilisateur) |
| **17** | Synchroniser pointages | Récupérer les pointages de l'appareil et les sauvegarder dans `attendance.json` |

Types de pointage reconnus :
| Code | Type |
|------|------|
| 0 | Entrée |
| 1 | Sortie |
| 2 | Pause début |
| 3 | Pause fin |
| 4 | Heures sup. entrée |
| 5 | Heures sup. sortie |

### ℹ️ Autres (Options 18-19)

- **Option 18** : Afficher les informations du dispositif (nom, numéro de série, firmware, plateforme, adresse MAC)
- **Option 19** : Quitter le programme

## 📄 Fichiers de données

### attendance.json

Stocke les pointages synchronisés depuis l'appareil. Structure :

```json
{
  "1": {
    "name": "Nom Utilisateur",
    "records": [
      {
        "timestamp": "2026-02-23 08:30:00",
        "date": "2026-02-23",
        "heure": "08:30:00",
        "type": "Entrée",
        "type_code": 0,
        "status": 1
      }
    ]
  }
}
```

### disabled_users.json

Stocke les utilisateurs désactivés et toutes les restrictions configurées. Structure :

```json
{
  "1": {
    "uid": 1,
    "name": "Nom Utilisateur",
    "privilege": 0,
    "password": "",
    "group_id": "",
    "user_id": "1",
    "card": 0
  },
  "day_restrictions": { "2": [6, 7] },
  "day_activations": { "3": [1, 2, 3, 4, 5] },
  "date_restrictions": { "2": ["2026-12-25", "2026-01-01"] },
  "date_activations": {},
  "time_restrictions": { "4": [{"debut": "12:00", "fin": "14:00"}] },
  "time_activations": { "5": [{"debut": "08:00", "fin": "18:00"}] }
}
```

## 🔌 Paramètres de connexion

| Paramètre | Valeur par défaut | Description |
|-----------|-------------------|-------------|
| IP | `10.0.22.56` | Adresse IP de l'appareil ZKTeco |
| Port | `4370` | Port de communication (standard ZK) |
| Timeout | `5` secondes | Délai de connexion |
| Password | `0` | Mot de passe de communication |
| Force UDP | `False` | Forcer le protocole UDP |
| Ommit Ping | `False` | Ignorer le ping de vérification |

## ❓ Dépannage

| Problème | Solution |
|----------|----------|
| Connexion refusée | Vérifiez que l'IP est correcte et que l'appareil est allumé |
| Timeout | Vérifiez que le PC et l'appareil sont sur le même réseau |
| Port bloqué | Assurez-vous que le port 4370 n'est pas bloqué par le pare-feu |
| Empreintes perdues | Après réactivation, les empreintes doivent être réenregistrées manuellement sur l'appareil |

## 📞 Support

Pour toute question ou problème :
- Consultez la [documentation pyzk](https://github.com/fananimi/pyzk)
- Documentation officielle ZKTeco

## 📝 Licence

Tous droits réservés - ZK Teco

---

**Auteur** : Emna
