import os, json

import logging
logging.basicConfig(level=logging.ERROR)
logging.getLogger("oscar_lib.oscar_client").setLevel(logging.ERROR)
logging.getLogger("oscar_lib.station").setLevel(logging.ERROR)


#from dotenv import load_dotenv
from oscar_lib import OscarClient, extractSchedules, Station, OscarGUIClient
from oscar_lib import OscarInterfaceDummy

region_map = {
    "africa":"I",
    "asia":"II",
    "southAmerica":"III",
    "northCentralAmericaCaribbean":"IV",
    "southWestPacific":"V",
    "europe":"VI"
}

def get_region(station):

        try:
            notation = detailed_station.get_region()
            region = region_map[notation.split("/")[5].lower()]
        except Exception as e:
            region = ""
        
        return region



my_region = None # if set to None it obtains the actual region from the WMRD (slow, not recommended) 
#my_region = "I"

client = OscarClient()
stations = client.oscar_search(params={"territoryName":"KEN"})

for station in stations["data"]["stationSearchResults"]:
  
    station["WMOIndex"] = station["wigosId"].split("-")[3] if "0-2000" in station["wigosId"] else ""

    if not my_region:
        detailed_station = Station(client.load_station(wigos_id=station["wigosId"]))
        region=get_region(detailed_station)
    else:
        region = my_region
 
    keys = ["name","wigosId","WMOIndex","stationTypeName","latitude","longitude","elevation","territory"]

    # Keetmanshoop Airport,0-20000-0-68312,68321,Land (fixed),-26.53333,18.1166666,1064,Namibia,I
    line = ",".join( [ (str(station[k]) if k in station else "") for k in keys]) + "," + region
 
    print(line)



