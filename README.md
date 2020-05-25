# oscar-lib
Library to interact with OSCAR/Surface

### create a station in OSCAR/Surface
```python
from oscar_lib import Station, OscarClient

schedule = { "startMonth": 1, "endMonth": 12,
   "startWeekday": 1, "endWeekday": 7,
   "startHour": 0, "endHour": 23,
   "startMinute": 0, "endMinute": 59,
   "interval": 60*60, "international": True, "real-time" : True}

modified_schedule = schedule.copy()
modified_schedule["interval"] = 30*60 # one observation has a half hourly schedule

observations = [ { "variable" : 224 , "observationsource" : "automaticReading" , "affiliation": "GOS" , "schedule": modified_schedule } , {   "affiliation": "GCOS" , "variable" : 226 , "observationsource" : "manualReading" }  ]

s = Station(name="Timo's station", urls="http://test.de" , stationtype="landFixed", status="operational" , wigosid="0-20000-0-12345", latitude="60.1" , longitude="45.34", elevation = "123.1" , country="TZA", region = "africa" , established = "2016-01-01Z" , observations =  observations , default_schedule = schedule)

s.validate()
 
client = OscarClient(oscar_url = OscarClient.OSCAR_DEPL, token="my_token")
client.upload_XML(str(s))

```
