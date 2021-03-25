import json
import sys
from oscar_lib import OscarClient, extractSchedules, Station
from lxml import etree

import unittest
 

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
            "interval": 3600,
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
