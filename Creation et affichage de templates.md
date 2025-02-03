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

Pour qu'un template (page HTML) soit visible sur le navigateur, il faut faire les suivants:
- Creer le fichier HTML (par ex. `index.html`) et le mettre dans le dossier `templates/main`:
    - Ajoutez ce ligne au debut de fichier: `{% load static %}`
    - Assurez vous que les fichiers statiques (CSS, JS, images, etc.) references par le fichier sont stockes dans le dossier `static/main`
    - Modifier les references des fichiers statiques dans la page HTML pour avoir un lien plus dynamique. <br/><br/>Par exemple, `<link rel="stylesheet" href="bootstrap.min.css">` deviendra `<link rel="stylesheet" href="{% static 'main/bootstrap.min.css' %}">`

    Voici a quoi le template peut ressembler:
    ```html
    {% load static %}
    <head>
        <title>Page de test</title>
        <!-- inclusion de bootstrap CSS -->
        <link rel="stylesheet" href="{% static 'main/bootstrap.min.css' %}">
    </head>
    <body>
        <p>Une paragraphe</p>
    </body>
    <!-- Inclusion de bootstrap JS -->
    <script src="{% static 'main/bootstrap.min.js' %}"></script>
    </html>
    ```

- Creer le view (fonction ou classe) qui va retourner le template en reponse (on va utiliser une fonction pour cet exemple):
```python
from django.shortcuts import render

# la fonction peut avoir n'importe quel nom,
# c'est pas oblige que ca soit le meme avec le template.
def home(request):
    # fait des operations si necessaire

    # retourne le template
    return render(request, "main/index.html")
```

- Ajouter une route dans le fichier `main/urls.py` qui va appeler le view quand l'utilisateur va naviguer a ce lien.<br/><br/>
Dans le fichier `main/urls.py`, il y a une liste qui s'appelle `urlpatterns`. Il faut ajouter la route dans cette liste.
```python
urlpatterns = [
    # les autres routes deja definis,
    path('/home', views.home, name='home')
]
```
Ce nouveau route nous dire que quand l'utilisateur va naviguer sur `/home` on va executer la fonction `views.home` (qui retourne la page `home.html`) <br/>

Le `name='home'` ajoute a la fin est important car ca nous permet d'identifier un route en particulier depuis n'importe ou dans le projet (meme les templates)


<br><br><br><br>
Apres avoir fait tout ceci, vous pouvez lancer votre serveur de developpement: `python manage.py runserver` et naviguez vers `localhost:8000/home` pour voir votre page.

<br><br>
Il y a deja un route de test avec son template deja rendu pour vous faire mieux comprendre.