from . import views
from django.urls import path

urlpatterns = [
    path('', views.Information.displayCrewForm, name='displayCrewForm'),
    #path('',views.Information.crewDetails, name = 'Form'),
    path('report', views.Information.crewDetails, name='report'),
    path('report/pdf_out', views.Information.pdf_out, name='output')
]