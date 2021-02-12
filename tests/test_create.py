import json
import sys
from xmldiff import main
from oscar_lib import OscarClient, extractSchedules, Station
from lxml import etree

import unittest



class TestCreateStation(unittest.TestCase):

    def test_create_xml(self):
        
        with open("tests/stationinfo.xml", "rb") as file_xml:
            with open("tests/test-station-xml.xml",encoding="utf8") as file_validate:

                xml = file_xml.read()
                xml_test = file_validate.read()

                station = Station(xml)
                xml_station = str(station)
              
                diff = main.diff_texts(xml_test,xml_station)
              
                self.assertFalse(diff)
              
                #self.assertEqual(xml_station,xml_test)
    
    
            
    def test_create_json(self):
        
        station_json = {
                "name":"Test Station",
                "wigosid": "0-20000-1-1",
                "latitude": 60.1234,
                "longitude": 60.1234,
                "elevation": 1234,
                "country" : "BRA",
                "established": "2018-01-10",
                "region" : "southAmerica",
                "stationtype": "landFixed",
                "status" : "operational",
                "description" : "test description",
                "timezone" : "UTC+3",
                "organization" : "INMET",
                "urls" : ["https://test.de","https://test.de/2"],
                "observations" : [{ 
                        "variable" : 210 , "observationsource" : "automaticReading" , 
                        "affiliation": "GOS" , "schedule" : {   
                           "startMonth": 1,   "endMonth": 12,
                           "startWeekday": 1, "endWeekday": 7,
                           "startHour": 0,    "endHour": 23,
                           "startMinute": 0,  "endMinute": 59,
                           "interval": 60*60, "international": True , "real-time" : True 
                        }
                },{ 
                        "variable" : 216 , "observationsource" : "manualReading" , 
                        "affiliation": "GCOS" , "schedule" : {   
                           "startMonth": 1,   "endMonth": 12,
                           "startWeekday": 1, "endWeekday": 7,
                           "startHour": 0,    "endHour": 23,
                           "startMinute": 0,  "endMinute": 59,
                           "interval": 60*60*30, "international": False, "real-time" : False
                        }
                }
                    ]
                }


        station = Station( station_json )
    
        self.maxDiff=None
        with open('tests/test-station-json.xml', encoding="utf8") as file:
            xml_station = str(station)
            xml_test = file.read()

            diff = main.diff_texts(xml_station,xml_test)
          
            self.assertFalse(diff)
            #self.assertEqual(xml,xml_test)
    
    def test_create_dict(self):
        
        observations = [{ 
            "variable" : 210 , "observationsource" : "automaticReading" , 
            "affiliation": "GOS" , "schedule" : {   
               "startMonth": 1,   "endMonth": 12,
               "startWeekday": 1, "endWeekday": 7,
               "startHour": 0,    "endHour": 23,
               "startMinute": 0,  "endMinute": 59,
               "interval": 60*60, "international": True , "real-time" : True 
            }}, { 
            "variable" : 216 , "observationsource" : "manualReading" , 
            "affiliation": "GCOS" , "schedule" : {   
               "startMonth": 1,   "endMonth": 12,
               "startWeekday": 1, "endWeekday": 7,
               "startHour": 0,    "endHour": 23,
               "startMinute": 0,  "endMinute": 59,
               "interval": 60*60*30, "international": False, "real-time" : False
                }
        }
        ]

        station = Station(name="Test Station",wigosid="0-20000-1-1",latitude=70.123,longitude=60.1111,elevation=123,country="BRA",
                           established="2020-01-01",region="africa",stationtype="landFixed",status="operational",
                           description="test description",timezone="UTC+3",organization="INMET",urls=["http://test.de","http://test.de/2"],
                           observations=observations
                           )
        
        self.maxDiff=None
        with open('tests/test-station.xml', encoding="utf8") as file:
            xml_station = str(station)
            xml_test = file.read()
            
            diff = main.diff_texts(xml_station,xml_test)
          
            self.assertFalse(diff)
            #self.assertEqual(xml,xml_test)   
