from django.db import models
from django.utils import timezone
import datetime
from django.utils.translation import gettext_lazy as _


class Evenement(models.Model):
    EVENT_TYPES = [
        ("pres", _("Presentiel")), 
        ("online", _("En ligne"))
    ]
    EVENT_CATEGORIES = [
        ("marriage", _("Marriage")),
        ("seminar", _("Seminaire")),
        ("workshop", _("Atelier")),
        ("meeting", _("Meeting")),
    ]

    nom = models.CharField(max_length=100)
    ville = models.CharField(max_length=100, default="Yaounde")
    pays = models.CharField(max_length=100, default="Cameroun")
    lieu = models.TextField()
    nombres_de_places = models.IntegerField(null=True, blank=True)
    rempli = models.BooleanField(default=False) # this is True when the event is sold out
    prix = models.FloatField(default=0)
    # entree gratuit veux dire que n'importe qui peut assister meme sans invitation
    entree_gratuit = models.BooleanField(default=False)

    description = models.TextField(null=True, blank=True)
    categorie = models.CharField(default="marriage", choices=EVENT_CATEGORIES, max_length=20)
    type =models.CharField(default="pres", choices=EVENT_TYPES, max_length=10)

    organisateur = models.CharField(max_length=50, null=True, blank=True)
    contact = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Contact d'organisateur"))

    date_heure_debut = models.DateTimeField(default=timezone.now, verbose_name=_("Debut (Date & heure)"))
    date_heure_fin = models.DateTimeField(null=True, blank=True, verbose_name=_("Fin (Date & heure)"))
    lieu = models.TextField(null=True, blank=True)
    lien = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom}: {self.ville}, {self.pays}"

class Billets(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE)
    date_paye = models.DateField(default=datetime.date.today)

class Participant(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE)
    email = models.EmailField()
    statut = models.CharField(max_length=15, choices=[
        ("pending", _("En attente")),
        ("rejected", _("Rejetée")),
        ("accepted", _("Accepté"))
    ])