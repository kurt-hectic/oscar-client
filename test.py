import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("dicttoxml").setLevel(logging.WARNING)
logging.getLogger("oscar_lib.station").setLevel(logging.DEBUG)

from oscar_lib import OscarInterfaceDummy

# instantiate interface
oscar = OscarInterfaceDummy(server="DEPL",token="dd2108de-6483-4422-8b8f-9d2e78edae53")

# check token
#print(OscarInterfaceDummy.validate_token(server="DEPL",token="68a1e82f-7c4f-49c8-ad3d-4912dc8cfeee"))

# create a station
new_station = {
    "name": "payerne III",
    "longitude": 77.64,
    "latitude": 32.78,
    "altitude": 23.45,
    "creation": "2020-12-06",
    "international": True,
    "manufacturer": "Biral",
    "parametersObserved": "216, 224",
    "operationalStatus": "operational",
    "realTime": True,
    "affiliations": "GOS, GUAN",
    #"observationsFrequency": "Jan-Jun/Mon-Fri/14-18/00-59:3600",
    "internationalReportingFrequency": "Jan-Jun/Mon-Fri/14:00-18:59/3600",
    "country": "IND",
    "utc": "UTC-06:00",
    "wigosID": "0-356-20-3610256932584798",
    "supervisingOrganization": "IMD",
    "type" : "landFixed",
    "automatic" : True,
    "region" : "southWestPacific",
    "description" : "a nice station",
}

#print(oscar.create_station(station=new_station,wigos_id=new_station["wigosID"]))

# retrieve wigos ids
#print("wigos_ids:",oscar.retrieve_wigosids(["0-20000-1-123456","0-104-6-4807100","0-20000-0-01007"]))

# retrieve schedules

#print("schedules:",oscar.retrieve_schedules(["0-20000-0-06610","0-20000-0-40875"]))

#print(oscar.update_wigosid(wigos_id=new_station["wigosID"]+"xxx", wigos_ids={'primaryWigosID':'0-356-20-3610256932584799', 'wigosID2':'0-356-20-3610256932584797'} ))

#oscar.update_affiliation(wigos_id="0-20000-0-10961xxx",affiliation="ANTON",variables=[57,179,227],operational_status="operational",program_id=None)


schedules = oscar.retrieve_schedules(new_station["wigosID"])

for schedule in schedules:
    tmp = schedule["schedule"].split('/')
    schedule["schedule"] =  "{}/{}".format("/".join(tmp[0:-1]),  int(int(tmp[-1]) / 2)) # shorten the reporting interval by half
    print(schedule)


oscar.update_schedule(wigos_id=new_station["wigosID"],schedules=schedules)

