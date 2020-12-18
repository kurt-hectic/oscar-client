from oscar_lib import OscarInterfaceDummy

# instantiate interface
oscar = OscarInterfaceDummy(server="DEPL",token="68a1e82f-7c4f-49c8-ad3d-4912dc8cfeee")

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
    "internationalReportingFrequency": "Jan-Jun/Mon-Fri/14-18/00-59:3600",
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
#print(oscar.retrieve_wigosids(["0-20000-1-123456","0-104-6-4807100","0-20000-0-01007"]))

# retrieve schedules

print(oscar.retrieve_schedules(["0-20000-0-06610","0-20000-0-40875"]))