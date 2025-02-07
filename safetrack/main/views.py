from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from .forms import EvenementForm
from .models import Evenement

def test_view(request):
    return render(request, "main/test.html")

def events(request):
    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})  # Return success response
        return JsonResponse({'success': False, 'errors': form.errors})  # Return validation errors
    else:
        form = EvenementForm()
        evenements = Evenement.objects.all()

    return render(request, "main/evenements.html", context={'evenements': evenements, 'form': form})

def event_list(request):
    evenements = Evenement.objects.all()
    form = EvenementForm()
    return render(request, 'main/evenements.html', {'evenements': evenements, 'form': form})

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
        event_data = {
            'id': event.id,
            'nom': event.nom,
            'nombres_de_places': event.nombres_de_places,
            'lieu': event.lieu,
            'ville': event.ville,
            'pays': event.pays,
            'prix': event.prix,
            'rempli': event.rempli,
            'entree_gratuit': event.entree_gratuit,
        }
        return JsonResponse({'event': event_data})

def delete_event(request, event_id):
    event = get_object_or_404(Evenement, id=event_id)
    if request.method == 'POST':
        event.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})