import os
from random import choice
from string import ascii_uppercase

import logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("oscar_lib").setLevel(logging.INFO)
logging.getLogger("oscar_lib.oscar_interface_dummy").setLevel(logging.INFO)
logging.getLogger("oscar_lib.oscar_client").setLevel(logging.INFO)
logging.getLogger("oscar_lib.utils").setLevel(logging.INFO)


from oscar_lib import OscarInterfaceDummy
from oscar_lib import OscarClient, extractSchedules, Station, OscarGUIClient
from dotenv import load_dotenv

import unittest


class TestInterface(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

        

        
    @classmethod
    def tearDownClass(cls):        
        return
        cls.interface.close()
        
        load_dotenv()
        user = os.getenv("OSCAR_USERNAME")
        password = os.getenv("OSCAR_PASSWORD")
        client = OscarGUIClient(oscar_url=OscarClient.OSCAR_DEPL,username=user,password=password)

        internal_id = client.wigos_to_internal_id(cls.test_wigos_id)
        client.delete_station(internal_id)
        client.close()
        
        cls.client.close()

    @unittest.skip("skipping")                
    def test_invalid_xml(self):
    
        load_dotenv()
        token = os.getenv("OSCAR_TOKEN")
        self.interface = OscarInterfaceDummy(server="DEPL",token=token)
        #self.client = OscarClient(oscar_url = OscarClient.OSCAR_DEPL, token=token)
    
        wid = "0-20000-0-10961"
    
        schedules = self.interface.retrieve_schedules(wigos_ids=[wid,])
              
        to_fix = ["id_30e3d639-fab8-4124-95ef-c81074c655b0","id_2b5c608a-7d1a-434e-99ce-b924580d4056","id_1e469410-a8dc-46f9-8255-1969ccba3722"]
              
        new_schedules=[]
        for schedule in schedules:
            if schedule["deployment_id"] in to_fix:
                
                new_schedule = schedule.copy()
                new_schedule["schedule"] = "Jan-Dec/Mon-Sun/0:0-23:59/3600"
                
                new_schedules.append(new_schedule)
                

        self.interface.update_schedule(wigos_id=wid, schedules=new_schedules)
              
        #self.assertEqual(ret["status"],499)
    
    @unittest.skip("skipping")                
    def test_create_existing(self):
        load_dotenv()
        token = os.getenv("OSCAR_TOKEN")
        self.interface = OscarInterfaceDummy(server="DEPL",token=token)
        self.client = OscarClient(oscar_url = OscarClient.OSCAR_DEPL, token=token)
        
        ## create station
        rand_str = ''.join(choice(ascii_uppercase) for i in range(6))

        self.test_name = "TEST CLIENT TIMO ({})".format(rand_str)
        self.test_wigos_id = "0-20000-0-06610" ## good old payerne

        params = {
            "rowNumber": 1,
            "latitude": 48.864716,
            "longitude": 2.349014,
            "altitude": 23,
            "creation": "2020-12-09T01:00:00+01:00",
            "international": True,
            "parametersObserved": "216, 224",
            #"parametersObserved": "216",
            "operationalStatus": "partlyOperational",
            "affiliations": "GOS, GUAN",
            #"affiliations": "GOS",
            "internationalReportingFrequency": "Jan-Jun/Mon-Fri/14:00-18:59/3600",
            "country": "IND",
            "utc": "UTC-06:00",
            "wigosID": self.test_wigos_id,
            "automatic": True,
            "name": self.test_name,
            "type": "landFixed",
            "region": "southWestPacific",
            "supervisingOrganization" : "EARS",
        }
        
        ret = self.interface.create_station(wigos_id=params["wigosID"],station=params)
        
        self.assertEqual(ret["status"],400)
       
    
                
    @unittest.skip("skipping")                
    def test_create(self):
        load_dotenv()
        token = os.getenv("OSCAR_TOKEN")
        self.interface = OscarInterfaceDummy(server="DEPL",token=token)
        self.client = OscarClient(oscar_url = OscarClient.OSCAR_DEPL, token=token)
        
        ## create station
        rand_str = ''.join(choice(ascii_uppercase) for i in range(6))

        self.test_name = "TEST CLIENT TIMO ({})".format(rand_str)
        self.test_wigos_id = "0-356-20-TEST{}".format(rand_str)

        params = {
            "rowNumber": 1,
            "latitude": 48.864716,
            "longitude": 2.349014,
            "altitude": 23,
            "creation": "2020-12-09T01:00:00+01:00",
            "international": True,
            "parametersObserved": "216, 224",
            #"parametersObserved": "216",
            "operationalStatus": "partlyOperational",
            "affiliations": "GOS, GUAN",
            #"affiliations": "GOS",
            "internationalReportingFrequency": "Jan-Jun/Mon-Fri/14:00-18:59/3600",
            "country": "IND",
            "utc": "UTC-06:00",
            "wigosID": self.test_wigos_id,
            "automatic": True,
            "name": self.test_name,
            "type": "landFixed",
            "region": "southWestPacific",
            "supervisingOrganization" : "EARS",
            "realTime": True
        }
        
        ret = self.interface.create_station(wigos_id=params["wigosID"],station=params)
        if not ret["status"] == 200:
            raise Exception("station creation failed")
  
    
    @unittest.skip("skipping")                
    def test_schedules(self):
    
        load_dotenv()
        token = os.getenv("OSCAR_TOKEN")
        self.interface = OscarInterfaceDummy(server="DEPL",token=token)
        #self.client = OscarClient(oscar_url = OscarClient.OSCAR_DEPL, token=token)
    
        wids =  """0-20000-0-12846
0-20000-0-12960
0-20000-0-12992
0-20000-0-12839
0-20000-0-12882
0-348-1-24120
0-348-1-28700"""

        for wid in wids.split('\n'):
            print("loading",wid)
            schedules = self.interface.retrieve_schedules(wigos_ids=[wid,])
            print(schedules)
    
    @unittest.skip("skipping")                
    def test_invalid_xml_plus(self):
    
        load_dotenv()
        token = os.getenv("OSCAR_TOKEN")
        self.interface = OscarInterfaceDummy(server="DEPL",token=token)
        #self.client = OscarClient(oscar_url = OscarClient.OSCAR_DEPL, token=token)
    
        wid = "0-20000-0-11027"
    
        schedules = self.interface.retrieve_schedules(wigos_ids=[wid,])

        for schedule in schedules:
            print("xx",schedule)

        return 
              
        to_fix = ["id_30e3d639-fab8-4124-95ef-c81074c655b0","id_2b5c608a-7d1a-434e-99ce-b924580d4056","id_1e469410-a8dc-46f9-8255-1969ccba3722"]
              
        new_schedules=[]
        for schedule in schedules:
            if schedule["deployment_id"] in to_fix:
                
                new_schedule = schedule.copy()
                new_schedule["schedule"] = "Jan-Dec/Mon-Sun/0:0-23:59/3600"
                
                new_schedules.append(new_schedule)
                

        self.interface.update_schedule(wigos_id=wid, schedules=new_schedules)
        
        
        
    @unittest.skip("skipping")  
    def test_update_affiliation(self):
    
        load_dotenv()
        token = os.getenv("OSCAR_TOKEN")
        self.interface = OscarInterfaceDummy(server="DEPL",token=token)
        #s
    
        ret = self.interface.update_affiliation(wigos_id="0-356-33-1",affiliation="GTOS",variables=[216,224])
        self.assertEqual(ret["status"],200)  

        #ret = self.client.oscar_search({"programAffiliation":"GTOS"})
        #self.assertTrue([station for station in ret["data"] if station["name"] == "Test final batch really 1"  ]) 


    def test_add_observation(self):
    
        with open("tests/stationinfo.xml", "rb") as file_xml:
            with open("tests/test-station-xml.xml",encoding="utf8") as file_validate:

                xml = file_xml.read()
                xml_test = file_validate.read()

                station = Station(xml)
                
                schedule = {   
                           "startMonth": 1,   "endMonth": 12,
                           "startWeekday": 1, "endWeekday": 7,
                           "startHour": 0,    "endHour": 23,
                           "startMinute": 0,  "endMinute": 59,
                           "interval": 60*60, "international": True , "real-time" : True 
                        }
                        
                current_location = station.get_location(active_only=True)
                
                #print(current_location)
                        
                instrument_coords = current_location.copy()
                instrument_coords["elevation"] = str(float(instrument_coords["elevation"]) + 2)
                
                observations = [ 
                    {"variable":226 , "observationsource" : "manualReading", "affiliation":"GOS", "schedule" : schedule , 
                    #"instrumentcoordinates" : instrument_coords 
                    } ,  
                     {"variable":227 , "observationsource" : "manualReading", "affiliation":"GOS", "schedule" : schedule , 
                    #"instrumentcoordinates" : instrument_coords 
                    } ,  
                ] 
                
                wigos_id = str(station.get_wigos_ids(primary=True))

                station.add_observations( observations , wigos_id , "2021-05-01")
                station.set_instrument_coordinates(226, 50.123456, 60.123456, 100)
                
                self.assertTrue( 226 in station.variables() )
                self.assertTrue( 227 in station.variables() )
                
                try:
                    station.validate()
                except:
                    self.assertTrue( False )
                
