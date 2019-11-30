import json

import logging
logging.basicConfig(level=logging.DEBUG)

from oscar_lib import OscarClient, extractSchedules, Station



# client = OscarClient()

# id = client.getInternalIDfromWigosId('0-20000-0-10424')


# myjson = client.getFullStationJson(id,level='deployments')

# myjson2 = extractSchedules(myjson,filterInternational=True)

# print(json.dumps(myjson2, indent=4, sort_keys=True))


#s = Station.load_station(internal_id="3256")

with open("tests/invalid_station.xml","br") as f:
    s = Station(  f.read() )
    
    
    s.fixDeployments(delete=True)