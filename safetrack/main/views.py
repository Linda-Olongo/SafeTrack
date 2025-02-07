from django.http import JsonResponse
from django.shortcuts import render

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