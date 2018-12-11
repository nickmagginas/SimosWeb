from . import views
from django.urls import path

urlpatterns = [
    path('', views.Information.displayCrewForm, name='displayCrewForm'),
    path('crewDetails/',views.Information.crewDetails, name = 'crewDetails'),
]