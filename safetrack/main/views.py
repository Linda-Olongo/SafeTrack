from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404

import pandas as pd

from .forms import EvenementForm, UpdateEvenementForm
from .models import Evenement, Participant

def test_view(request):
    return render(request, "main/test.html")

def events(request, event_id=None):
    edit_form = UpdateEvenementForm

    if not event_id:
        if request.method == 'POST':
            form = EvenementForm(request.POST, request.FILES)
            
            if form.is_valid():
                evenement = form.save()
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
            evenements = Evenement.objects.all()

        return render(request, "main/evenements.html", context={'evenements': evenements, 'form': form, 'edit_form': edit_form})
    else:
        return HttpResponse("Page underway")

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