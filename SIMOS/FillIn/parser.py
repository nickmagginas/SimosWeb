import datetime
import os



def parse():
	pathe = os.path.dirname(__file__)
	with open(os.path.join(pathe, 'datafiles/Aircraft_Capacity.csv'), 'r') as f:
		f.readline()
		capdict = {}
		it = 0
		for line in f:
			st = line.replace('\n', '')
			st = st.split(',')
			st[-1] = int(st[-1])
			st[-2] = int(st[-2])
			capdict[st[0] + ' ' + st[1]] = st[2:]
			it +=1

	with open(os.path.join(pathe,'datafiles/Airport_Distances.csv'), 'r') as f:
		f.readline()
		disdict = {}
		for line in f:
			st = line.replace('\n', '')
			st = st.split(',')
			st[-1] = float(st[-1])
			disdict[st[0]] = st[1]

	with open(os.path.join(pathe,'datafiles/Average_Flight_Times.csv'), 'r') as f:
		first = f.readline()
		first = first.replace('\n', '')
		first = first.split(',')
		first.pop(0)
		second = f.readline()
		second = second.replace('\n', '')
		second = second.split(',')
		second.pop(0)
		f.readline()
		models = []
		airports = []
		datlist = []
		ftdict = {}
		models = [first[i] + ' ' + second[i] for i in range(len(first))]
		for line in f:
			st = line.replace('\n', '')
			st = st.split(',')
			airports.append(st[0])
			st = st[1:]
			[datlist.append(float(i)) for i in st]
		it = 0
		for i in airports:
			for j in models:
				ftdict[j + ':' + i] = datlist[it]
				it += 1

	with open(os.path.join(pathe, 'datafiles/Average_Fuel_Consumption.csv'), 'r') as f:
		first = f.readline()
		first = first.replace('\n', '')
		first = first.split(',')
		first.pop(0)
		second = f.readline()
		second = second.replace('\n', '')
		second = second.split(',')
		second.pop(0)
		models = []
		airports = []
		datlist = []
		fcdict = {}
		models = [first[i] + ' ' + second[i] for i in range(len(first))]
		for line in f:
			st = line.replace('\n', '')
			st = st.split(',')
			airports.append(st[0])
			st = st[1:]
			[datlist.append(float(st[i])) if st[i] != '' else datlist.append('N/A') for i in range(len(st))]
		it = 0
		for i in airports:
			for j in models:
				fcdict[j + ':' + i] = datlist[it]
				it += 1


	with open(os.path.join(pathe, 'datafiles/Crew_Roster.csv'), 'r') as f:
		f.readline()
		crewdict = {}
		it = 0 
		keys = []
		for line in f:
			st = line.replace('\n', '')
			st = st.split(',')
			keys.append(st[0])
			st.pop(0)
			crewdict[keys[it]] = st
			it +=1

	with open(os.path.join(pathe, 'datafiles/Flight_Log.csv'), 'r') as f:
		f.readline()
		idlist = []
		fldict = {}
		datlist = []
		for line in f:
			st = line.replace('\n', '')
			st = st.split(',')
			idlist.append(st[0])
			datlist.append(st)
		idlist = list(set(idlist))
		for i in idlist:
			fldict[i] = []
		for st in datlist:
			st[2] = int(st[2])
			st[1] = datetime.datetime.strptime(st[1], '%d-%b-%y')
			fldict[st[0]].append(st[1:])
		for i in range(1, len(crewdict) + 1):
			recent_ft = 0
			for j in fldict['C' + str(i)]:
				if j[0] + datetime.timedelta(days=3) >= datetime.datetime.now():
					recent_ft += j[1]
			fldict['C' + str(i)].append(recent_ft)

	return capdict, disdict, ftdict, crewdict, fldict, fcdict


parse()


# for i in range(1, len(crewdict) + 1):
# 	recent_ft = 0
# 	for j in fldict['C' + str(i)]:
# 		if j[0] + datetime.timedelta(days=3) >= datetime.datetime.now():
# 			recent_ft += j[1]
# 	fname = crewdict['C' + str(i)][0]
# 	lname = crewdict['C' + str(i)][1]
# 	DOB = crewdict['C' + str(i)][2]
# 	role = crewdict['C' + str(i)][3]
# 	crsr.execute("""INSERT INTO CrewInfo (CrewID, fname, lname, DOB, role, recent_ft)  VALUES (?, ?, ?, ?, ?, ?)""",
# 		(i, fname, lname, DOB, role, recent_ft))

def main():
	parse()


if __name__ == '__name__':
	main()