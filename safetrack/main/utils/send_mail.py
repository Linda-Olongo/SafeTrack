import logging

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Vérifie si ALLOWED_HOSTS est défini et ne contient pas "*"
host = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS[0] != "*" else "localhost"

# Détermine le protocole et le port dynamiquement
protocol = "https" if not settings.DEBUG else "http"
port = getattr(settings, "PORT", 8000)  # Utilise un port par défaut si non spécifié

# Construit l'URL dynamique
base_url = f"{protocol}://{host}:{port}" if settings.DEBUG else f"{protocol}://{host}"


# generer le contenu d'un email d'invitation pour un participant
def send_invitation_email(instance):
    evenement = instance.evenement

    subject = _("Invitation à l'événement : {event_name}").format(event_name=evenement.nom)
    message = _(
        """Bonjour {name},
    
        Nous avons le plaisir de vous inviter à notre {event_type}. Cet événement est un {event_category} organisé par {organisateur}.
    
        📅 **Date et heure** :
        Début : {date_debut}
        Fin : {date_fin}
    
        📍 **Lieu** : {lieu}
        🔗 **Lien** : {lien}
    
        📝 **Détails** :
        - Catégorie : {event_category}
        - Type : {event_type}
        - Organisateur : {organisateur}
    
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
        lien=evenement.lien or _("Aucun lien disponible")
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

            <span><h3>📍 %(lieu_label)s :</h3> <p>%(lieu)s</p></span>    

            <span><h3>🔗 %(lien_label)s :</h3> <p><a href="%(lien)s" style="color: #1a73e8;">%(lien)s</a></p></span>

            <h3>📝 %(details_label)s :</h3>
            <ul>
                <li><strong>%(categorie_label)s</strong> %(event_category)s</li>
                <li><strong>%(type_label)s</strong> %(event_type)s</li>
                <li><strong>%(organisateur_label)s</strong> %(organisateur)s</li>
            </ul>

            <p>%(closing_text)s</p>

            <p>%(cordialement)s,<br><strong>%(team_label)s</strong></p>

            <!-- Buttons -->
            <div style="text-align: center; margin-top: 20px;">
                <a href="%(accept_url)s" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px; display: inline-block;">
                    ✅ %(accept_label)s
                </a>

                <a href="%(reject_url)s" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    ❌ %(reject_label)s
                </a>
            </div>
        </body>
        </html>"""
    )
    context = {
        "titre": _("Invitation à l'événement"),
        "bonjour": _("Bonjour"),
        "name": instance.name,
        "intro": _("Nous avons le plaisir de vous inviter à notre"),
        "event_type": instance.evenement.get_type_display(),
        "event_desc": _("Cet événement est un"),
        "event_category": instance.evenement.get_categorie_display(),
        "organized_by": _("organisé par"),
        "organisateur": instance.evenement.organisateur,
        "date_heure": _("Date et heure"),
        "debut": _("Début :"),
        "date_debut": instance.evenement.date_heure_debut.strftime("%d/%m/%Y %H:%M"),
        "fin": _("Fin :"),
        "date_fin": instance.evenement.date_heure_fin.strftime(
            "%d/%m/%Y %H:%M") if instance.evenement.date_heure_fin else _("Non spécifié"),
        "lieu_label": _("Lieu"),
        "lieu": instance.evenement.lieu or _("Non spécifié"),
        "lien_label": _("Lien"),
        "lien": instance.evenement.lien or "#",
        "details_label": _("Détails"),
        "categorie_label": _("Catégorie :"),
        "type_label": _("Type :"),
        "organisateur_label": _("Organisateur :"),
        "closing_text": _("Nous espérons vous voir bientôt !"),
        "cordialement": _("Cordialement"),
        "team_label": _("L'équipe d'organisation"),
        "accept_label": _("Accepter l'invitation"),
        "reject_label": _("Rejeter l'invitation"),
        "accept_url": f"{base_url}/invitation/{instance.id}/accept/",
        "reject_url": f"{base_url}/invitation/{instance.id}/reject/",

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
