from . import views
from django.urls import path

urlpatterns = [
    path("test", views.test_view, name="test"),
    path("events/", views.events, name="events"),
    path('events/<int:event_id>', views.events, name="event-detail"),
    path('events/<int:event_id>/change/', views.change_event, name='change_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),

]