import json
import sys
import logging
logging.basicConfig(level=logging.DEBUG)

from oscar_lib import OscarClient, extractSchedules, Station

client = OscarClient( oscarurl = OscarClient.OSCAR_DEPL , token="248eadae-8d38-4410-85c9-ccfd0ba897fa" )

# my_id = "0-20000-0-10520"
my_id = "0-20008-0-AKN"

wmdr = client.load_station(wigos_id=my_id)
s = Station(wmdr)

defaultSchedule = {   "from": None,     "to" : None,     "startMonth": 1,     "endMonth": 12,     "startWeekday": 1,
    "endWeekday": 7,     "startHour": 0,     "endHour": 23,     "startMinute": 0,     "endMinute": 59,     "interval": "PT1H",     "international": True   }

#s.validate()

s.fix_deployments(mode="update",defaultSchedule = defaultSchedule )
s.validate()


wdqms_variables = [216,210,224,251,309,12005,12006] # pressure,precipitation,temperature,humidity,wind deprecated, wind speed, wind direction

schedules = s.current_schedules(variables=wdqms_variables)
precipition_schedules = schedules[210]

print(json.dumps(precipition_schedules,indent=2))

tmp = precipition_schedules["deployments"][0]["datagenerations"][0]
mygid = tmp["gid"]
myschedule = tmp["schedule"]

newschedule = myschedule.copy()
newschedule["from"] = "2007-12-02T00:00:00Z"
newschedule["to"] = "2008-12-01T00:00:00Z"
newschedule["interval"] = "PT30M"

s.update_schedule(mygid,newschedule)

new_schedules = s.current_schedules()

assert not 210 in new_schedules.keys() 
    
with open("tests/out-prod.xml","w",encoding="utf8") as f:
    f.write(str(s))
    
print("validation",s.validate() )

#s.save(client)    