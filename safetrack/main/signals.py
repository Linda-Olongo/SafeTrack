import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .models import Participant
from main.utils.send_mail import send_invitation_email

@receiver(post_save, sender=Participant)
def send_email_on_participant_creation(sender, instance, created, **kwargs):
    print(f"Sending invitation to {instance.email}")

    if instance.invitation_successful is None and instance.email:
        try:
            send_invitation_email(instance)
        except Exception as e:
            # already logged by the utils/send_mail module
            pass