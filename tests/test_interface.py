import os
from random import choice
from string import ascii_uppercase

from oscar_lib import OscarClient, extractSchedules, Station, OscarGUIClient
from dotenv import load_dotenv

import unittest
import logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("oscar_lib").setLevel(logging.WARNING)
logging.getLogger("oscar_lib.oscar_interface_dummy").setLevel(logging.INFO)

from oscar_lib import OscarInterfaceDummy

class TestInterface(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        token = os.getenv("OSCAR_TOKEN")
        cls.interface = OscarInterfaceDummy(server="DEPL",token=token)
        cls.client = OscarClient(oscar_url = OscarClient.OSCAR_DEPL, token=token)
        
        ## create station
        rand_str = ''.join(choice(ascii_uppercase) for i in range(6))

        cls.test_name = "TEST CLIENT ({})".format(rand_str)
        cls.test_wigos_id = "0-356-20-TEST{}".format(rand_str)

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
            "wigosID": cls.test_wigos_id,
            "automatic": True,
            "name": cls.test_name,
            "type": "landFixed",
            "region": "southWestPacific"
        }
        
        ret = cls.interface.create_station(wigos_id=params["wigosID"],station=params)
        if not ret["status"] == 200:
            raise Exception("station creation failed")

        
    @classmethod
    def tearDownClass(cls):        
        cls.interface.close()
        
        load_dotenv()
        user = os.getenv("OSCAR_USERNAME")
        password = os.getenv("OSCAR_PASSWORD")
        client = OscarGUIClient(oscar_url=OscarClient.OSCAR_DEPL,username=user,password=password)

        internal_id = client.wigos_to_internal_id(cls.test_wigos_id)
        client.delete_station(internal_id)
        client.close()
        
        cls.client.close()


    def test_retrieve_wigosid(self):
        
        ret = self.interface.retrieve_wigosids(any_ids=['0-20000-0-60490',])
        
        primary = ret["0-20000-0-60490"]["primaryWigosID"]
        secondary = ret["0-20000-0-60490"]["wigosID2"]
        
        self.assertEqual(primary,"0-20000-0-60490")
        self.assertEqual(secondary,"0-12-20000-60490")

    
    def test_update_wigosid(self):
    
        params = {
        "primaryWigosID": self.test_wigos_id,
        "wigosID2": self.test_wigos_id+"2",
        "wigosID3": self.test_wigos_id+"3"
        }

        ret = self.interface.update_wigosid(wigos_id=self.test_wigos_id,wigos_ids=params)
        try:
            self.assertEqual(ret["status"],200)
        except AssertionError as ae:
            print(ret["message"])
            raise ae
        
        ret = self.interface.retrieve_wigosids(any_ids=[self.test_wigos_id,])
        
        primary = ret[self.test_wigos_id]["primaryWigosID"]
        secondary = ret[self.test_wigos_id]["wigosID2"]
        tertiary = ret[self.test_wigos_id]["wigosID3"]
        
        
        self.assertEqual(primary,self.test_wigos_id)
        self.assertIn(secondary,[params["wigosID2"],params["wigosID3"]])
        self.assertIn(tertiary,[params["wigosID2"],params["wigosID3"]])


    def test_update_affiliation(self):
        ret = self.interface.update_affiliation(wigos_id=self.test_wigos_id,affiliation="GTOS",variables=[216,224])
        self.assertEqual(ret["status"],200)  

        ret = self.client.oscar_search({"programAffiliation":"GTOS"})
        self.assertTrue([station for station in ret["data"] if station["name"] == self.test_name  ])    
        
        
    def test_update_schedule(self):
    
        schedules = self.interface.retrieve_schedules(self.test_wigos_id)
        
        self.assertTrue(schedules)

        for schedule in schedules:
            tmp = schedule["schedule"].split('/')
            schedule["schedule"] =  "{}/{}".format("/".join(tmp[0:-1]),  int(int(tmp[-1]) / 2)) # shorten the reporting interval by half

        ret = self.interface.update_schedule(wigos_id=self.test_wigos_id,schedules=schedules)
        
        self.assertEqual(ret["status"],200)

        schedules = self.interface.retrieve_schedules(self.test_wigos_id)
        self.assertTrue(schedules)
        for schedule in schedules:
            self.assertEqual( schedule["schedule"].split('/')[-1] , "1800" )
            
            
    def test_update_schedule_2(self):
    
    

    
        params =  {'wigosID': self.test_wigos_id, 
        'variable': 216, 
        'deployment_id': 'depl_1_1', 
        'deployment_name': '2020-12-09T00:00:00Z-None', 
        'schedule_id': 'dg_1_1', 
        'schedule': 'Jan-Jun/Mon-Fri/14:0-18:59/900', 
        'international': True, 
        'near-real-time': True, 
        'date_from': '2020-12-09T00:00:00Z', 
        'date_to': None, 
        'status': 'operational'}
        
        schedules = [params,]

        ret = self.interface.update_schedule(wigos_id=self.test_wigos_id,schedules=schedules)
        self.assertEqual(ret["status"],200)

        schedules = self.interface.retrieve_schedules(self.test_wigos_id)
        
        found=False
        for schedule in schedules:
            if schedule['schedule_id']=='dg_1_1':
                self.assertEqual(schedule["schedule"].split('/')[-1] , "900")
                found=True
                
        self.assertTrue(found)
