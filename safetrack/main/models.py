from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import datetime
from django.utils.translation import gettext_lazy as _

import pandas as pd

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

    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nom}: {self.ville}, {self.pays}"

    def get_invitations_with_status(self, status="pending"):
        status = status.lower()
        if status not in ["pending", "accepted", 'rejected']:
            raise ValueError(f"Status must either be pending, accepted or rejected")
        
        return self.participant_set.filter(statut=status)

    @property
    def accepted_invitations(self):
        return self.get_invitations_with_status("accepted")

    @property
    def rejected_invitations(self):
        return self.get_invitations_with_status("rejected")

    @property
    def pending_invitations(self):
        return self.get_invitations_with_status("pending")

    @property
    def nombres_de_places_restantes(self):
        return self.nombres_de_places - self.participant_set.count()

class Billets(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE)
    date_paye = models.DateField(default=datetime.date.today)

class Participant(models.Model):
    INVITATION_STATUS = [
        ("pending", _("En attente")),
        ("rejected", _("Rejetée")),
        ("accepted", _("Accepté"))
    ]

    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    statut = models.CharField(max_length=15, choices=INVITATION_STATUS, default="pending")
    invitation_successful = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.name}, {self.statut}"

    @classmethod
    def add_from_excel_file(cls,file, event):
        df = pd.read_excel(file)

        for index, row in df.iterrows():
            email = row.get("Email")
            name = row.get("Nom")

            if email and name:
                cls.objects.create(
                    evenement=event,
                    email=email,
                    statut='pending',
                    name=name
                )

class Notification(models.Model):
    message = models.TextField()
    event = models.ForeignKey(Evenement, on_delete=models.CASCADE)

class ParticipantNotification(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    envoye_avec_succes = models.BooleanField(default=False)
    heure_denvoi = models.DateTimeField(auto_now_add=True, null=True)