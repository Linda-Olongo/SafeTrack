import csv
import json
import logging

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
import os
from django.core.mail import EmailMessage
from django.utils.timezone import localtime
from icalendar import Calendar, Event
from datetime import datetime
from django.conf import settings
from django.utils.timezone import localtime
# from django.views.decorators.http import require_POST

import pandas as pd

from .forms import EvenementForm, UpdateEvenementForm, ParticipantForm, UpdateParticipantForm, BulkParticipantUploadForm
from .models import Evenement, Participant
from main.utils.send_mail import send_invitation_email

def generate_ics_file(event):
    """Génère un fichier ICS pour l'événement."""
    cal = Calendar()
    cal.add('prodid', '-//Mon Application//Calendrier//FR')
    cal.add('version', '2.0')

    ical_event = Event()
    ical_event.add('summary', event.nom)
    ical_event.add('dtstart', localtime(event.date_heure_debut))
    ical_event.add('dtend', localtime(event.date_heure_fin))
    ical_event.add('location', event.lieu)
    ical_event.add('description', f"Description : {event.description}")

    cal.add_component(ical_event)

    # Sauvegarde du fichier ICS
    file_path = os.path.join(settings.MEDIA_ROOT, f"event_{event.id}.ics")
    with open(file_path, 'wb') as f:
        f.write(cal.to_ical())

    return file_path




def index(request):
    return redirect("events")  # change this when dashboard will be created


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        print("request data is:")
        print(request.POST)
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            context = {
                "errrors": [
                    {
                        "message": _("Nom d'utilisateur ou mot de passe incorrect")
                    }
                ]
            }
            return render(request, "main/login.html", context=context, status=400)

        if not user.check_password(password):
            print("Mismatched passwords")
            return render(
                request,
                "main/login.html",
                context={
                    "errors": [
                        {
                            "message": _("Nom d'utilisateur ou mot de passe incorrect"),
                        }
                    ]
                },
                status=400
            )

        if not user.is_active:
            print("User is not active")
            return render(
                request,
                "main/login.html",
                context={
                    "errors": [
                        {
                            "message": _("Compte a ete desactive"),
                        }
                    ]
                },
                status=403
            )

        login(request, user)
        print("User logged in successfully")

        return redirect("events")
    else:
        return render(request, "main/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


def signup(request):
    if request.method == "POST":
        print("POST data")
        print(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        if User.objects.filter(username=username).count() > 0:
            context = {
                "errors": [
                    {"message": _("Nom d'utilisateur deja prit")}
                ]
            }
            return render(request, "main/signup.html", context=context)

        else:
            print("Creating user account")
            user = User.objects.create(username=username, password=password, email=email)
            print(f"Created user {user}")
            return redirect("login")
    return render(request, "main/signup.html")


def test_view(request):
    return render(request, "main/test.html")


@login_required
def events(request, event_id=None):
    user = request.user
    edit_form = UpdateEvenementForm

    if not event_id:
        if request.method == 'POST':
            form = EvenementForm(request.POST, request.FILES)

            if form.is_valid():
                evenement = form.save()
                evenement.user = user
                evenement.save()
                excel_file = form.cleaned_data.get("participants_file")
                if excel_file:
                    try:
                        df = pd.read_excel(excel_file)

                        for index, row in df.iterrows():
                            email = row.get("Email")
                            name = row.get("Nom")

                            if email and name:
                                Participant.objects.create(
                                    evenement=evenement,
                                    email=email,
                                    statut='pending',
                                    name=name
                                )
                    except Exception as e:
                        evenement.delete()
                        return JsonResponse({'success': False, 'errors': ['Error adding participants from excel file']})

                return JsonResponse({'success': True})  # Return success response

            return JsonResponse({'success': False, 'errors': form.errors})  # Return validation errors

        else:
            form = EvenementForm()
            evenements = Evenement.objects.filter(Q(user=user) | Q(user__isnull=True))

        return render(request, "main/evenements.html",
                      context={'evenements': evenements, 'form': form, 'edit_form': edit_form})
    else:
        event = get_object_or_404(Evenement, id=event_id, user=user)

        context = {
            'event': event,
            'update_participant_form': UpdateParticipantForm,
            'participant_form': ParticipantForm,
            'participants_json': [model_to_dict(p) for p in event.participant_set.all()]
        }

        print("Returning context... ")
        print(context)

        return render(request, "main/event_detail.html", context=context)


@login_required
def event_list(request):
    evenements = Evenement.objects.all()
    form = EvenementForm()
    edit_form = UpdateEvenementForm()
    return render(request, 'main/evenements.html', {'evenements': evenements, 'form': form, 'edit_form': edit_form})


@login_required
def event_dashboard(request, event_id):
    event = Evenement.objects.filter(user=request.user, id=event_id)

    if not event.count():
        return HttpResponse("You are not allowed to access this resource", status=403)

    return render(request, "main/event_dashboard.html", {'event': event})


@login_required
def change_event(request, event_id):
    event = get_object_or_404(Evenement, id=event_id)

    if request.method == 'POST':
        form = EvenementForm(request.POST, instance=event)
        if form.is_valid():
            updated_event = form.save()

            # Génération du fichier ICS
            ics_file_path = generate_ics_file(updated_event)

            # Lien Google Calendar
            google_calendar_link = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={updated_event.nom}&dates={updated_event.date_heure_debut.strftime('%Y%m%dT%H%M%S')}/{updated_event.date_heure_fin.strftime('%Y%m%dT%H%M%S')}&location={updated_event.lieu}&details={updated_event.description}"

            # Notifier les participants
            participants = Participant.objects.filter(evenement=event)
            for participant in participants:
                email = EmailMessage(
                    subject="📅 Mise à jour de l'événement",
                    body="",
                    from_email="jamiecho456@gmail.com",
                    to=[participant.email],
                )

                email.attach_file(ics_file_path)  # Ajout du fichier ICS en pièce jointe
                email.content_subtype = "html"
                email.body = f"""
                    <div style="font-family: Arial, sans-serif; text-align: center;">
                        <h2 style="color: #2C3E50;">Mise à jour de l'événement 🎉</h2>
                        <p>Bonjour <strong>{participant.name}</strong>,</p>
                        <p>L'événement <strong>{event.nom}</strong> a été modifié. Voici les nouveaux détails :</p>
                        <p><strong>📆 Date et heure de début :</strong> {updated_event.date_heure_debut}</p>
                        <p><strong>⌛ Date et heure de fin :</strong> {updated_event.date_heure_fin}</p>
                        <p><strong>📍 Lieu :</strong> {updated_event.lieu}</p>
                        <p>Merci de prendre en compte ces modifications.</p>
                        <p>📅 <a href="{google_calendar_link}" style="color: #007BFF;">Ajouter à Google Calendar</a></p>
                        <p style="color: #16A085; font-weight: bold;">À bientôt !</p>
                    </div>
                """
                email.send()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'event': model_to_dict(event)})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Evenement, id=event_id)

    if request.method == 'POST':
        participants = Participant.objects.filter(evenement=event)

        for participant in participants:
            send_mail(
                subject="⚠️ Annulation de l'événement",
                message="",
                html_message=f"""
                    <div style="font-family: Arial, sans-serif; text-align: center;">
                        <h2 style="color: #E74C3C;">Événement annulé ❌</h2>
                        <p>Bonjour <strong>{participant.name}</strong>,</p>
                        <p>Nous avons le regret de vous informer que l'événement <strong>{event.nom}</strong> a été annulé.</p>
                        <p>Nous nous excusons pour la gêne occasionnée.</p>
                        <p style="color: #E67E22; font-weight: bold;">Merci de votre compréhension.</p>
                    </div>
                """,
                from_email="jamiecho456@gmail.com",
                recipient_list=[participant.email],
                fail_silently=False,
            )

        event.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})


@login_required
def add_participants(request, event_id):
    user = request.user
    event = get_object_or_404(Evenement, id=event_id, user=user)

    if request.method == "POST":
        file_form = BulkParticipantUploadForm(request.POST, request.FILES)
        data = json.loads(request.body)

        if "file" in request.FILES:
            file = file_form.cleaned_data.get("file")
            if file:
                Participant.add_from_excel_file(file)
            return JsonResponse({"message": "Participants uploaded successfully"}, status=200)

        elif "participants" in data:
            participants_list = data.get("participants", [])
            for p in participants_list:
                participant = Participant.objects.create(
                    evenement=event, name=p["name"], email=p["email"], statut="pending"
                )

                # Envoi de l'invitation
                try:
                    send_invitation_email(participant)
                except Exception as e:
                    logging.error(f"❌ Erreur lors de l'envoi de l'email à {p['email']}: {e}")
                    print(f"❌ Erreur lors de l'envoi de l'email à {p['email']}: {e}")

            return JsonResponse({"message": "Participants added and invitations sent"}, status=200)

        return HttpResponse("error", status=500)


@login_required
def update_participant(request, participant_id):
    """ View to update a participant """
    if request.method == "POST":
        try:
            data = request.POST
            participant = get_object_or_404(Participant, id=participant_id, evenement__user=request.user)

            old_email = participant.email  # Store old email before update

            participant.name = data.get("name", participant.name)
            participant.email = data.get("email", participant.email)
            participant.statut = data.get("statut", participant.statut)
            participant.save()

            # If email has changed, send a new invitation
            if old_email != participant.email:
                participant.invitation_successful = False
                send_invitation_email(participant)

            return JsonResponse({"success": "Participant updated"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def delete_participant(request, participant_id):
    if request.method == "DELETE":
        participant = get_object_or_404(Participant, id=participant_id)
        participant.delete()

        return JsonResponse({"success": True, "message": "Participant supprimé avec succès."})

    return JsonResponse({"success": False, "message": "Méthode non autorisée."}, status=405)



def accept_invitation(request, participant_id):
    """Accepter une invitation et mettre à jour le statut"""
    # if request.method != "POST":
    #     return JsonResponse({"success": False, "message": "Méthode non autorisée."}, status=405)

    participant = get_object_or_404(Participant, id=participant_id)

    if participant.statut != "accepted":
        participant.statut = "accepted"
        participant.invitation_successful = True
        participant.save()
        return JsonResponse({"success": True, "message": "Invitation acceptée."})

    return JsonResponse({"success": False, "message": "L'invitation est déjà acceptée."})


def reject_invitation(request, participant_id):
    """Rejeter une invitation et mettre à jour le statut"""
    # if request.method != "POST":
    #     return JsonResponse({"success": False, "message": "Méthode non autorisée."}, status=405)

    participant = get_object_or_404(Participant, id=participant_id)

    if participant.statut != "rejected":
        participant.statut = "rejected"
        participant.invitation_successful = False
        participant.save()
        return JsonResponse({"success": True, "message": "Invitation rejetée."})

    return JsonResponse({"success": False, "message": "L'invitation est déjà rejetée."})


def invitation_confirmation(request):
    """Afficher un message de confirmation après une action sur une invitation"""
    return render(request, "main/confirmation.html")
