from . import views
from django.urls import path

urlpatterns = [
    path("", views.index, name='index'),
    path("test", views.test_view, name="test"),
    path("events/", views.events, name="events"),
    path('events/<int:event_id>', views.events, name="event-detail"),
    path('events/<int:event_id>/change/', views.change_event, name='change_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('events/<int:event_id>/add_participants/', views.add_participants, name='add_participants'),
    path('participants/<int:participant_id>/change/', views.update_participant, name='update_participant'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('signup', views.signup, name='signup'),
]