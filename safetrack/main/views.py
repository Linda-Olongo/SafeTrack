from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

import pandas as pd

from .forms import EvenementForm, UpdateEvenementForm
from .models import Evenement, Participant

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

        return render(request, "main/evenements.html", context={'evenements': evenements, 'form': form, 'edit_form': edit_form})
    else:
        event = get_object_or_404(Evenement, id=event_id, user=user)
        
        return render(request, "main/event_detail.html", {'event': event})

def event_list(request):
    evenements = Evenement.objects.all()
    form = EvenementForm()
    edit_form = UpdateEvenementForm()
    return render(request, 'main/evenements.html', {'evenements': evenements, 'form': form, 'edit_form': edit_form})

def change_event(request, event_id):
    event = get_object_or_404(Evenement, id=event_id)
    if request.method == 'POST':
        form = EvenementForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        event_data = model_to_dict(event)
        
        return JsonResponse({'event': event_data})
        
def delete_event(request, event_id):
    event = get_object_or_404(Evenement, id=event_id)
    if request.method == 'POST':
        event.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})