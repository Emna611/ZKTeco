# ZK Teco - Gestion de Présence

Ce projet fournit une interface Python pour gérer les données de présence et les utilisateurs désactivés depuis les dispositifs ZK Teco.

## 📋 Description

Ce projet permet de :
- Récupérer et traiter les données de présence (attendance.json)
- Gérer les utilisateurs désactivés (disabled_users.json)
- Interagir avec les appareils biométriques ZK Teco

## 📁 Structure du Projet

```
├── attendance.json              # Données de présence
├── disabled_users.json          # Liste des utilisateurs désactivés
├── from zk import ZK, const.py  # Script principal de gestion ZK
└── README.md
```

## 🚀 Installation

### Prérequis
- Python 3.11+
- Bibliothèque `pyzk`

### Setup

```bash
# Cloner le dépôt
git clone https://github.com/Emna611/ZKTeco.git

# Accéder au répertoire
cd ZKTeco

# Installer les dépendances
pip install pyzk
```

## 💻 Utilisation

```bash
python "from zk import ZK, const.py"
```

## 📄 Fichiers

- **attendance.json** : Contient les enregistrements de présence des employés
- **disabled_users.json** : Liste des utilisateurs désactivés du système
- **from zk import ZK, const.py** : Script principal pour l'interaction avec les appareils ZK

## 🔧 Fonctionnalités

- Gestion des enregistrements de présence
- Gestion des utilisateurs désactivés
- Communication avec les appareils biométriques ZK Teco

## 📞 Support

Pour toute question ou problème, veuillez consulter la documentation officielle de ZK Teco.

## 📝 Licence

Tous droits réservés - ZK Teco

---

**Dernier commit** : Initial commit (298157b)
**Auteur** : Emna
