from django.db import models
import datetime

class Evenement(models.Model):
    nom = models.CharField(max_length=100)
    ville = models.CharField(max_length=100, default="Yaounde")
    pays = models.CharField(max_length=100, default="Cameroun")
    lieu = models.TextField()
    nombres_de_places = models.IntegerField(null=True, blank=True)
    rempli = models.BooleanField(default=False) # this is True when the event is sold out
    prix = models.FloatField(default=0)
    # entree gratuit veux dire que n'importe qui peut assister meme sans invitation
    entree_gratuit = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nom}: {self.ville}, {self.pays}"

class Billets(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE)
    date_paye = models.DateField(default=datetime.date.today)