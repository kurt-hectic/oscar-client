# oscar-lib

A library to interact with OSCAR/Surface, developed by the WMO Community and kick-started by the WMO Secretariat. The oscar-lib allows to batch create stations using simple Python objects, and it also has support for downloading and changing information in OSCAR/Surface directly. Currently the modification of schedules is supported. More extensive documentation is currently being worked on.

For more details on how to use the library, see the [series of example code](https://github.com/kurt-hectic/wmo-notebooks) provided in jupyter notebooks.

This library is a community effort and supported by the WMO community, through the [OSCAR/Surface support forum](https://etrp.wmo.int/mod/forum/view.php?id=10062). Everybody is welcome to contribute to oscar-lib, please work through github to suggest improvements or post to the forum. As oscar-lib is a community-lead effort, the official OSCAR/Surface helpdesk at MeteoSwiss can not provide support for the oscar-lib.

Some part of the code, grouped in the object OscarGUIClient, is experimental and uses an internal API of OSCAR/Surface. These methods should be used with care and awareness that the internal API endpoint in OSCAR/Surface may change.

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
