import logging

from asgiref.sync import sync_to_async
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import localtime
from urllib.parse import urlencode

# Vérifie si ALLOWED_HOSTS est défini et ne contient pas "*"
host = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS[0] != "*" else "localhost"

# Détermine le protocole et le port dynamiquement
protocol = "https" if not settings.DEBUG else "http"
port = getattr(settings, "PORT", 8000)  # Utilise un port par défaut si non spécifié

# Construit l'URL dynamique
base_url = f"{protocol}://{host}:{port}" if settings.DEBUG else f"{protocol}://{host}"

def send_email(subject, body, destinataires, from_email="noreply@example.com"):
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=destinataires
    )
    email.send()

def send_notification_email(participantnotification):
    print(f"Sending email to {participantnotification.participant.email}")
    try:
        send_mail(
            participantnotification.notification.subject, 
            participantnotification.notification.message, from_email="noreply@example.com", 
            recipient_list=[participantnotification.participant.email], fail_silently=False
        )
        participantnotification.envoye_avec_succes = True
        participantnotification.heure_denvoi = timezone.now()
        participantnotification.save()
    except Exception as e:
        logging.error("Error sending notification email to participant")

async def send_email_async(subject, body, destinataires, from_email="noreply@example.com"):
    print(f"Sending emails to {destinataires}")
    await sync_to_async(send_mail)(
        subject, body, from_email, destinataires, fail_silently=False
    )

# Générer le lien Google Calendar
def generate_google_calendar_url(event):
    start_time = localtime(event.date_heure_debut).strftime("%Y%m%dT%H%M%SZ")
    end_time = localtime(event.date_heure_fin).strftime("%Y%m%dT%H%M%SZ") if event.date_heure_fin else start_time

    params = {
        "action": "TEMPLATE",
        "text": event.nom,
        "dates": f"{start_time}/{end_time}",
        "details": event.description or _("Aucune description fournie"),
        "location": event.lieu or "",
        "trp": "false"
    }
    return f"https://www.google.com/calendar/render?{urlencode(params)}"


# Envoyer un email d'invitation
def send_invitation_email(instance):
    evenement = instance.evenement

    google_calendar_url = generate_google_calendar_url(evenement)  # Générer l'URL Google Calendar

    subject = _("Invitation à l'événement : {event_name}").format(event_name=evenement.nom)
    message = _(
        """Bonjour {name},

        Nous avons le plaisir de vous inviter à notre {event_type}. Cet événement est un {event_category} organisé par {organisateur}.

        📅 **Date et heure** :
        Début : {date_debut}
        Fin : {date_fin}

        📍 **Lieu** : {lieu}
        🔗 **Lien** : {lien}

        Ajoutez cet événement à votre calendrier Google : {google_calendar_url}

        Nous espérons vous voir bientôt !

        Cordialement,
        L'équipe d'organisation"""
    ).format(
        name=instance.name,
        event_type=evenement.get_type_display(),
        event_category=evenement.get_categorie_display(),
        organisateur=evenement.organisateur or _("Non spécifié"),
        date_debut=evenement.date_heure_debut.strftime("%d/%m/%Y %H:%M"),
        date_fin=evenement.date_heure_fin.strftime("%d/%m/%Y %H:%M") if evenement.date_heure_fin else _("Non spécifié"),
        lieu=evenement.lieu or _("Non spécifié"),
        lien=evenement.lien or _("Aucun lien disponible"),
        google_calendar_url=google_calendar_url
    )

    EMAIL_TEMPLATE = _(
        """<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>%(titre)s</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>%(bonjour)s <strong>%(name)s</strong>,</p>

            <p>
                %(intro)s <strong>%(event_type)s</strong>. %(event_desc)s <strong>%(event_category)s</strong> %(organized_by)s <strong>%(organisateur)s</strong>.
            </p>

            <h3>📅 %(date_heure)s :</h3>
            <p>
                <strong>%(debut)s</strong> %(date_debut)s<br>
                <strong>%(fin)s</strong> %(date_fin)s
            </p>

            <h3>📍 %(lieu_label)s :</h3>
            <p>%(lieu)s</p>

            <h3>🔗 %(lien_label)s :</h3>
            <p><a href="%(lien)s" style="color: #1a73e8;">%(lien)s</a></p>

            <h3>📅 Ajouter à Google Calendar :</h3>
            <p><a href="%(google_calendar_url)s" target="_blank" style="background-color: #34a853; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                📆 Ajouter à Google Calendar
            </a></p>

            <h3>📝 %(details_label)s :</h3>
            <ul>
                <li><strong>%(categorie_label)s</strong> %(event_category)s</li>
                <li><strong>%(type_label)s</strong> %(event_type)s</li>
                <li><strong>%(organisateur_label)s</strong> %(organisateur)s</li>
            </ul>

            <p>%(closing_text)s</p>

            <p>%(cordialement)s,<br><strong>%(team_label)s</strong></p>
        </body>
        </html>"""
    )

    context = {
        "titre": _("Invitation à l'événement"),
        "bonjour": _("Bonjour"),
        "name": instance.name,
        "intro": _("Nous avons le plaisir de vous inviter à notre"),
        "event_type": evenement.get_type_display(),
        "event_desc": _("Cet événement est un"),
        "event_category": evenement.get_categorie_display(),
        "organized_by": _("organisé par"),
        "organisateur": evenement.organisateur or _("Non spécifié"),
        "date_heure": _("Date et heure"),
        "debut": _("Début :"),
        "date_debut": evenement.date_heure_debut.strftime("%d/%m/%Y %H:%M"),
        "fin": _("Fin :"),
        "date_fin": evenement.date_heure_fin.strftime("%d/%m/%Y %H:%M") if evenement.date_heure_fin else _(
            "Non spécifié"),
        "lieu_label": _("Lieu"),
        "lieu": evenement.lieu or _("Non spécifié"),
        "lien_label": _("Lien"),
        "lien": evenement.lien or "#",
        "google_calendar_url": google_calendar_url,  # Lien Google Calendar
        "details_label": _("Détails"),
        "categorie_label": _("Catégorie :"),
        "type_label": _("Type :"),
        "organisateur_label": _("Organisateur :"),
        "closing_text": _("Nous espérons vous voir bientôt !"),
        "cordialement": _("Cordialement"),
        "team_label": _("L'équipe d'organisation"),
    }

    email_html = EMAIL_TEMPLATE % context

    email = EmailMultiAlternatives(
        subject=subject,
        body=message,  # Plain text fallback
        from_email="noreply@example.com",
        to=[instance.email],
    )
    email.attach_alternative(email_html, "text/html")  # Attach HTML version

    try:
        email.send()
        instance.invitation_successful = True
        instance.save()
    except Exception as e:
        logging.error(f"Error sending invitation email, error: {e}")
        instance.invitation_successful = False
        instance.save()
