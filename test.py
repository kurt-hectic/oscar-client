from oscar_lib import OscarInterfaceDummy

# instantiate interface
oscar = OscarInterfaceDummy(server="PROD",token="mytoken")

# check token
print(OscarInterfaceDummy.validate_token(server="DEPL",token="xxx"))

# create a station
new_station = {
    "longitude": 77.64,
    "latitude": 32.78,
    "altitude": 23.45,
    "creation": "2020-12-06",
    "international": True,
    "manufacturer": "Biral",
    "parametersObserved": "345, 596, 258",
    "operationalStatus": "Operational",
    "realTime": True,
    "affiliations": "851, 693",
    "observationsFrequency": "12",
    "internationalReportingFrequency": "16",
    "country": "India",
    "utc": "UTC-06:00",
    "wigosID": "0-01-20-3610256932584798",
    "supervisingOrganization": "AAED"
}
print(oscar.create_station(station=new_station,wigos_id=new_station["wigosID"]))

# retrieve wigos ids
print(oscar.retrieve_wigosids(["0-20000-1-123456",]))