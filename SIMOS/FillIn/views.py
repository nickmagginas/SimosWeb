from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

class Information(TemplateView):


	def displayCrewForm(request):
		name = ['John Stasinski', 'Michael BANANA']
		return render(request,'FillIn/crew_form.html',{'name': name})

	def crewDetails(request):
		name = 'BANANA'
		if 'Crew1' in request.GET:
			message = 'You Entered' + request.GET['Crew1']
		return HttpResponse(message)
