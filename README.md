# SafeTrack
Application Web Sécurisée et Intelligente de Gestion d'Événements


# Comment le lancer
- Cloner le projet: `git clone git@github.com:Linda-Olongo/SafeTrack.git`
- Entrer dans l'emplacement du dossier: `cd SafeTrack`
- Creer un environnement virtuel: `python -m venv env` ou `python3 -m venv env` (env c'est le nom de l'environnement, si vous utilisez un autre nom, il faut l'ajouter dans le fichier .gitignore)
- Activer l'environnement:
    - Sur Windows: `env\Scripts\activate`
    - Sur Linux ou Mac: `source env/bin/activate`
- Installer les bibliotheques: `pip install -r requirements.txt`
- Lancer le serveur: `python safetrack\manage.py runserver` (Windows) ou `python3 safetrack/manage.py runserver` (Linux et macOS)


# Les bons pratiques
- Si vous telechargez un nouveau bibliotheque, il faut mettre a jour le fichier `requirements.txt`: `pip freeze > requirements.txt`
- Si vous travaillez sur une nouvelle fonctionnalite, creez un autre branche pour ne pas deranger les autres modules existants.


# La structure du projet.
Le depot a cette structure
```
└── SafeTrack/
    ├── safetrack/
    │   ├── main
    │   └── safetrack
    ├── README.md
    └── requirements.txt
```

Le dossier principal avec le code source c'est le dossier `SafeTrack/safetrack` dans le depot, qui est le projet django.

Dans le dossier `SafeTrack/safetrack`, il y a 2 sous-dossiers, `main` et `safetrack`.

Le dossier `SafeTrack/safetrack/safetrack` contient les configurations du projet et l'autre dossier `SafeTrack/safetrack/main` c'est ou toutes les fonctionnalites seront appliques.

Voici la structure de l'application main
```
└── SafeTrack/
    ├── safetrack/
    │   ├── main/
    │   │   ├── migrations/
    |   |   ├── static/main/
    |   |   ├── templates/main/
    |   |   ├── utils/
    │   │   ├── __init__.py
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── models.py
    │   │   ├── test.py
    │   │   └── urls.py
    │   └── safetrack
    ├── README.md
    └── requirements.txt
```

Les fichiers les plus importants au developpement sont:
- `models.py`: contient la structure des bases de donnees. Les differents tables sont definits ici en forme de classes
- `views.py`: on peut l'appeler la partie backend. Il contient le logique de metier (en forme de fonctions ou classes) et est charge de l'affichage des pages HTML.
- `urls.py`: definit les routes qui vont lancer les objets definit dans le `views.py`
- `static/main`: tous les fichiers `static` (JS, CSS, images, etc.) se trouvent ici.
- `templates/main`: pour les fichiers HTML, si vous voulez ajoutez un fichier HTML, ca s'ajoute ici.

Pour plus de details sur l'interaction entre les `views` les `urls` et les templates, veuillez consulter: [Creation et affichage de templates.md](Creation%20et%20affichage%20de%20templates.md)