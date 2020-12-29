import json
import sys
from oscar_lib import OscarClient, extractSchedules, Station
from lxml import etree

import unittest

import logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("dicttoxml").setLevel(logging.WARNING)
logging.getLogger("oscar_lib").setLevel(logging.WARNING)

from oscar_lib import OscarInterfaceDummy

class TestInterface(unittest.TestCase):

    def setUp(self):
        self.interface = OscarInterfaceDummy(server="DEPL",token="no-token")
        super().setUp()

    def tearDown(self):
        self.interface.close()

    def test_create_1(self):
        
        params = {
            "rowNumber": 1,
            "latitude": 77.64,
            "longitude": 32.78,
            "altitude": 23,
            "creation": "2020-12-09",
            "international": True,
            "parametersObserved": "216, 224",
            "operationalStatus": "operational",
            "affiliations": "GOS, GUAN",
            "internationalReportingFrequency": "Jan-Jun/Mon-Fri/14:00-18:59/3600",
            "country": "IND",
            "utc": "UTC-06:00",
            "wigosID": "0-356-20-3610256932584798",
            "automatic": True,
            "name": "payerne III",
            "type": "landFixed",
            "region": "southWestPacific"
        }
        
        ret = self.interface.create_station(wigos_id=params["wigosID"],station=params)
        self.assertEqual(ret["message"],"auth error. Check token")

    def test_create_2(self):
        
        params = {
            "rowNumber": 1,
            "latitude": 77.64,
            "longitude": 32.78,
            "altitude": 23,
            "creation": "2020-12-23",
            "international": True,
            "manufacturer": "Biral",
            "parametersObserved": "216, 224",
            "operationalStatus": "Operational",
            "realTime": True,
            "affiliations": "GOS, GUAN",
            "observationsFrequency": "Jan-Jun/Mon-Fri/14:00-18:59/3600",
            "internationalReportingFrequency": "Jan-Jun/Mon-Fri/14:00-18:59/3600",
            "country": "IND",
            "utc": "UTC-06:00",
            "wigosID": "0-356-20-3610256932584798",
            "supervisingOrganization": "IMD",
            "automatic": True,
            "name": "payerne III",
            "type": "landFixed",
            "region": "southWestPacific",
            "description": "a nice station"
        }
        
        ret = self.interface.create_station(wigos_id=params["wigosID"],station=params)
        self.assertEqual(ret["message"],"auth error. Check token")

    def test_create_3(self):
        
        params = {
        "rowNumber": 1,
        "latitude": 77.64,
        "longitude": 32.78,
        "altitude": 23,
        "creation": "2020-12-23",
        "international": True,
        "manufacturer": "Biral",
        "parametersObserved": "216, 224",
        "operationalStatus": "Operational",
        "realTime": True,
        "affiliations": "GOS, GUAN",
        "observationsFrequency": "Jan-Jun/Mon-Fri/14:00-18:00/3600",
        "internationalReportingFrequency": "Jan-Jun/Mon-Fri/14:00-18:59/3600",
        "country": "IND",
        "utc": "UTC-06:00",
        "wigosID": "0-356-20-3610256932584798",
        "supervisingOrganization": "IMD",
        "automatic": True,
        "name": "payerne III",
        "type": "landFixed",
        "region": "southWestPacific",
        "description": "a nice station"
        }
        
        ret = self.interface.create_station(wigos_id=params["wigosID"],station=params)
        self.assertEqual(ret["message"],"auth error. Check token")


    def test_schedule_1(self):
    
        ret = self.interface.retrieve_schedules(wigos_ids=["0-20000-0-60490",])
        self.assertEqual(ret[0]["wigosID"],"0-20000-0-60490")
        
        #self.assertEqual(ret["message"],"error: station 0-356-20-3610256932584798 does not exist '0-356-20-3610256932584798 not contained in OSCAR or cannot be downloaded'")


    def test_update_schedule(self):
    
        schedules = [{
        "wigosID": "0-356-20-3610256932584798",
        "variable": 123,
        "schedule_id": "12", # the schedule id by which the schedule is matched
        "schedule": "Jan-Jun/Mon-Fri/14:00-18:00/1800",
        "international": True,
        "status": "operational",
        "date_from": "2020-12-06",
        "date_to": "2020-12-07"
        },]
    
        ret = self.interface.update_schedule(wigos_id='0-356-20-3610256932584798',schedules=schedules)
        self.assertEqual(ret["message"],"error: station 0-356-20-3610256932584798 does not exist '0-356-20-3610256932584798 not contained in OSCAR or cannot be downloaded'")
        
        
    def test_retrieve_wigosid(self):
        
        ret = self.interface.retrieve_wigosids(any_ids=['0-20000-0-60490',])
        
        primary = ret["0-20000-0-60490"]["primaryWigosID"]
        secondary = ret["0-20000-0-60490"]["wigosID2"]
        
        self.assertEqual(primary,"0-20000-0-60490")
        self.assertEqual(secondary,"0-12-20000-60490")
        
    def test_update_wigosid(self):
    
        params = {
        "primaryWigosID": "0-356-20-3610256932584798",
        "wigosID2": "0-356-20-3610256932584798",
        "wigosID3": "0-356-20-3610256932584798"
        }

        ret = self.interface.update_wigosid(wigos_id="0-356-20-3610256932584798",wigos_ids=params)
        self.assertEqual(ret["status"],400)

    def test_update_wigosid_2(self):
    
        params =   {
        "primaryWigosID": "0-356-20-3610256932584798",
        "wigosID2": "0-356-20-3610256932584798",
        "wigosID3": "0-356-20-3610256932584798",
        "wigosID4": "0-356-20-3610256932584798"
        }

        ret = self.interface.update_wigosid(wigos_id="0-356-20-3610256932584798",wigos_ids=params)
        self.assertEqual(ret["status"],400)

    def test_update_affiliation(self):
    
        ret = self.interface.update_affiliation(wigos_id="0-356-20-3610256932584798",affiliation="GTOS",variables=[216,224])
        self.assertEqual(ret["status"],400)


    @unittest.skip("migating code")
    def test_newstation(self):

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

