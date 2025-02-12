from django.contrib import admin

from .models import  Evenement, Participant

admin.site.register(Evenement)
admin.site.register(Participant)