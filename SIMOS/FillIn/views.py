from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.views.generic import TemplateView
from reportlab.pdfgen import canvas
from . import parser
import datetime
import numpy as np
import os
import io
from django_xhtml2pdf.utils import generate_pdf

class Information(TemplateView):


	def displayCrewForm(request):
		capdict, disdict, ftdict, crewdict, fldict, fcdict = parser.parse()
		names = [crewdict[i][0] + ' ' + crewdict[i][1] for i in crewdict]
		roles = [crewdict[i][3] for i in crewdict]
		namerol = zip(names, roles)
		models = list(set([i[:-3] if i[-2:] == '10' else i[:-2] for i in fcdict]))
		airports = [i for i in disdict if i != 'LHR']
		return render(request,'FillIn/crew_form.html',{'name': namerol, 'models': models, 'airports' : airports})

	def crewDetails(request):
		capdict, disdict, ftdict, crewdict, fldict, fcdict = parser.parse()
		information = request.GET
		keys = [i for i in information]
		crew_ids = ['C' + str(int(i[4:]) + 1) for i in keys if 'Crew' in i]
		crew = [crewdict[i][0] + crewdict[i][1] for i in crew_ids]
		
		#~~~~~~~~~~CHECKS~~~~~~~~~~~
		#pilot check
		roles = [crewdict[i][3] for i in crew_ids]
		pilot_check = False
		if 'Pilot' not in roles:
			pilot_check = True
		#recent flight check
		rf_check = [fldict[i][-1] < 20 for i in crew_ids]
		if not all(rf_check):
			rf_check = [crew[i] for i in range(len(rf_check)) if not rf_check[i]]
		#fuel cap + altitude check
		alt_check = False
		fuel_check = False
		#model = information['plane']
		model = 'Boeing 777'
		altitude = information['altitude']
		av_fuel_cons = fcdict[model + ':' + altitude]
		#destination = information['destination']
		destination = 'BHX'
		distance = disdict[destination]
		fuel_cap = capdict[model][1]
		if not av_fuel_cons:
			alt_check = True
		else:
			fuel_req = av_fuel_cons * distance
			if float(fuel_req) > int(fuel_cap):
				fuel_check = True
		#Weather check
		weather_check = False
		if information['Weather'] == 'Severe':
			weather_check = True
		#Passenger checks
		pass_cap_check = False
		meal_num_check = False
		if int(information['passengers']) > capdict[model][0]:
			pass_cap_check = True
		if int(information['Chicken']) + int(information['Fish']) + int(information['Vegetarian']) != int(information['passengers']):
			meal_num_check = True
		#Date checks
		past_check = False
		date = datetime.datetime.strptime(information['fl_date'], '%Y-%m-%d')
		if date < datetime.datetime.now():
			past_check = True
		daycheck = [True for _ in range(len(crew_ids))]
		for i in range(len(crew_ids)):
			for j in range(len(fldict[crew_ids[i]]) - 1):
				cur = fldict[crew_ids[i]]
				if cur[0] == date:
					daycheck[i] = False
		if not all(daycheck):
			daycheck = [crew[i] for i in range(len(daycheck)) if not daycheck[i]]
		
		#~~~~~~~~~~~~FLIGHT INFO~~~~~~~~~~~~
		flight_info = {}
		crewinfo = [crewdict[crew_ids[i]] for i in range(len(crew_ids))]
		flight_info['crew'] = crewinfo
		flight_time = round(ftdict[model + ':' + destination] * 10)
		flight_info['flight_time'] = flight_time
		route = [date, model, 'LHR', destination, distance, altitude]		
		flight_info['route'] = route
		flight_info['meal_info'] = [information['Chicken'], information['Fish'], information['Vegetarian']]
		flight_info['meal_weight'] = int(information['passengers']) * int(information['weight'])
		flight_info['reg_date'] = datetime.datetime.now()

		if any([alt_check, fuel_check, weather_check, pass_cap_check, meal_num_check, past_check, pilot_check]) or not all(daycheck) or not all(rf_check):
			debug = ''
			nameser = [crewdict[i][0] + ' ' + crewdict[i][1] for i in crewdict]
			roleser = [crewdict[i][3] for i in crewdict]
			nameroler = zip(nameser, roleser)
			modelser = list(set([i[:-3] if i[-2:] == '10' else i[:-2] for i in fcdict]))
			airportser = [i for i in disdict if i != 'LHR']
			error_messages = []
			if alt_check:
				error_messages.append(f'The selected aircraft can not fly at {altitude} altitude.\n')
			if fuel_check:
				error_messages.append(f'The selected aircraft can only carry {fuel_cap} kg of fuel. The selected route is out of range.\n')
			if weather_check:
				error_messages.append(f'It is not recommended to fly under ' + information['Weather'] + ' weather conditions.\n')
			if pass_cap_check:
				error_messages.append(f'The selected aircraft can only fit {capdict[model][0]} passengers.\n')
			if meal_num_check:
				error_messages.append('The amount of meals specified are not enough for ' + information['passengers'] +' passengers.\n')
			if past_check:
				error_messages.append('The flight date must be in the future.\n')
			if pilot_check:
				error_messages.append('No pilot selected.\n')
			if not all(daycheck):
				for i in range(len(daycheck)):
					if not daycheck[i]:
						error_messages.append(f'{crewdict[crew_ids[i]][0]} {crewdict[crew_ids[i]][1]} is going to be flying elsewhere on the date specified.\n')
			if not all(rf_check):
				for i in range(len(rf_check)):
					if not rf_check[i]:
						error_messages.append(f'{crewdict[crew_ids[i]][0]} {crewdict[crew_ids[i]][1]} would exceed 20 hours of flight in 72 hours.\n ')
			return render(request,'FillIn/error_form.html',{'name':nameroler, 'models': modelser, 'airports' : airportser, 'errors': error_messages, 'debug':debug})

		else:
			#~~~~~~~~~~~UPDATE CSVS~~~~~~~~~~~~~
			dir_path = os.path.dirname(__file__)
			with open(os.path.join(dir_path, 'datafiles/Flight_log.csv'), 'a') as f:
				for i in range(len(crew_ids)):
					f.write(str(crew_ids[i]) + ',' + date.strftime('%d-%b-%y') + ',' + str(flight_time) + '\n')
			with open(os.path.join(dir_path, 'datafiles/Registered_Flights.csv'), 'a') as f:
				crewstr = ''
				mealstr = ''
				for i in crew_ids:
					crewstr += i 
					crewstr += ' '
				for i in flight_info['meal_info']:
					mealstr += i
					mealstr += ' '
				f.write(date.strftime('%d %B %Y')+ ',' + 'LHR' + '-' + str(destination) + ',' + str(model) +',' + crewstr + ',' + mealstr + ',' + str(flight_info['meal_weight']) + ',' + str(distance) + ',' + str(altitude) + ',' + str(flight_time) + ',' + str(fuel_req) + ',' + flight_info['reg_date'].strftime('%d-%b-%y') + '\n')
			# report = []
			# report.append('LHR --' + destination)
			# report.append(date)
			# report.append(f'Travelling on a {model}.')
			# report.append(f'Selected crew: {crew}.')
			# report.append('Meals ordered:' + information['Chicken'] + ' Chicken\t' + information['Fish'] + ' Fish\t' + information['Vegetarian'] + ' Vegetarian')
			# report.append(f'Expected flight length {flight_time} hours.')
			return render(request, 'Fillin/report.html', {
				'origin': 'LHR', 
				'destination': destination,
				'date': date,
				'model': model,
				'crew': crew,
				'passengers': information['passengers'],
				'chicken': information['Chicken'],
				'fish': information['Fish'],
				'vegetarian': information['Vegetarian'],
				'flight_time': flight_time,
				'flight_cost': int(information['passengers'])*5 + int(fuel_req)*2
				})

	def pdf_out(request):
		resp = HttpResponse(content_type='application/pdf')
		result = generate_pdf('FillIn/report.html', file_object=resp)
		return result

