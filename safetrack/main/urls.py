from . import views
from django.urls import path

urlpatterns = [
    path("test", views.test_view, name="test"),
    path("", views.events, name="events"),
]