import json
import sys
from oscar_lib import OscarClient, extractSchedules, Station
from lxml import etree

import unittest


class TestStation(unittest.TestCase):

    def setUp(self):
        self.client = OscarClient()
        super().setUp()

    def tearDown(self):
        self.client.close()

    def test_load(self):
        """
        Test if we can load good old Payerne
        """

        xml=self.client.load_station(wigos_id="0-20008-0-PAY")
        self.assertIn("PAYERNE" , str(xml)  )
        
    def test_mapids(self):
        """
        Test if we can map a WIGOSID to an internal id.
        We use the station Bandarabbas
        """        

        id=self.client.wigos_to_internal_id("0-20000-0-40875")
        self.assertEqual(6064,id)
        
    def test_search(self):
        """
        Test if we can find German stations.
        Germany should have between 100 and 500 landFixed stations and the climtological station UECKERMUENDE should be there.
        """

        res=self.client.oscar_search({"territoryName":"DEU","facilityType":"landFixed"})
        
        self.assertIn("meta",res)
        self.assertIn("length",res["meta"])
        
        self.assertGreaterEqual(res["meta"]["length"],100)
        self.assertLessEqual(res["meta"]["length"],500)
        
        self.assertIn( "UECKERMUENDE",json.dumps(res["data"]) )
        

class TestFixschedules(unittest.TestCase):
    def test_delete(self):
        """
        Test if the schedule can be fixed by deleting the schedule
        """

        filenames = ["tests/invalid_station.xml","tests/valid-station-payerne-multi_depl.xml"]

        for filename in filenames:
            with open(filename,"br") as f:
                s = Station(  f.read() )
            
                valid=False
                try:
                    s.fix_deployments(mode="delete")
                    valid=True
                except etree.DocumentInvalid as err:
                    pass
                    
                self.assertTrue( valid )

    def test_assign_default(self):
        """
        Test if the schedule can be fixed by assigning a default schedule
        """

        filenames = ["tests/invalid_station.xml","tests/valid-station-payerne-multi_depl.xml"]

        defaultSchedule = {
            "from": None,
            "to" : None,
            "startMonth": 1,
            "endMonth": 12,
            "startWeekday": 1,
            "endWeekday": 7,
            "startHour": 0,
            "endHour": 23,
            "startMinute": 0,
            "endMinute": 59,
            "interval": "PT1H",
            "international": True
        }


        for filename in filenames:
            with open(filename,"br") as f:
                s = Station(  f.read() )
            
                valid=False
                try:
                    s.fix_deployments( defaultSchedule=defaultSchedule )
                    valid=True
                except etree.DocumentInvalid as err:
                    pass
                    
                self.assertTrue( valid )
