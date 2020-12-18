import os, json

from jsonschema import validate, FormatChecker
from jsonschema.exceptions import ValidationError

from .oscar_interface import FormalOscarInterface
from . import OscarClient, Station

from .utils import convert_schedule

mydir = os.path.dirname(__file__) + "/static/"


with open(mydir+"/json-schemas/create_station.json","r") as f:
    station_schema = json.load( f )

class OscarInterfaceDummy(FormalOscarInterface):
   
    def __init__(self, server: str = "DEPL", token : str = None) :
        """initialize the OscarInterface class for usage with the token at the specificed server.
        
        server (str): whether the token is validated  in the production or testing system (PROD|DEPL) (default DEPL)
        token (str): the user API token
        """
        if server != "DEPL":
            raise Exception("only DEPL implemented at this stage")
        
        self.client = OscarClient(oscar_url = OscarClient.OSCAR_DEPL, token=token)
   
    def create_station(self, station: dict, wigos_id: str = None  ) -> dict :
        """create an WDMR record for the information contained in dict and push it to OSCR
        station is a JSON object representing the status with a grammar.
           
        Parameters:
        wigos_id (str): the WIGOS identifier of the station that should be created
        station (dict): a dictionary containing the information about the station that should be created. Note that this also includes the wigos id
        
        Returns:
        dict: status code (status) and message (message)
        """
        try:
            validate( instance=station , schema=station_schema ,  format_checker=FormatChecker() )
        except ValidationError as ve:
            raise ValueError("station object not valid {}".format(str(ve)))
            
        schedule = convert_schedule(station["internationalReportingFrequency"])
        schedule["international"] = station["international"]
        schedule["real-time"] = station["realTime"]

        observation_ids = [int(o.strip()) for o in station["parametersObserved"].split(",")]
        
        if not "affiliations" in station:
            station["affiliations"] = "unknown"
        affiliations =  [a.strip() for a in station["affiliations"].split(",") ]
        
        if len(affiliations) > 1 and len(affiliations) != len(observation_ids):
            raise Exception("number of affiliations must be equal number of observations or 1")
            
        # same length as observation to facilitate loop underneath
        if len(affiliations) == 1:
            affiliations = affiliations[0] * len(observation_ids)
        

        observations = []
        observationsource = "automaticReading" if station["automatic"] else "manualReading"
        
        for idx,oid in enumerate(observation_ids):
            observations.append( { "variable" : oid , "observationsource" : observationsource , "affiliation": affiliations[idx] , "schedule": schedule } )

        required_parameter_map = { "name" : "name", "stationtype":"type", "status":"operationalStatus",
            "wigosid":"wigosID","timezone":"utc","latitude":"latitude","longitude":"longitude",
            "elevation":"altitude","country":"country","region":"region","established":"creation"
        }
        
        optional_parameter_map = { "description":"description", "manufacturer" : None, "observationsFrequency" : None , "organization":"supervisingOrganization" }

        station_params = { k:station[v] for k,v in required_parameter_map.items() }

        station_params["urls"] = ["http://test.de",]
        station_params["observations"] = observations
        station_params["default_schedule"] = schedule

        # add optional parameters if not empty
        for k,v in optional_parameter_map.items():
            if v:
                station_params[k]=station[v]

        new_station = Station(**station_params)
        
        new_station.validate()

        status = self.client.upload_XML(str(new_station))
                
        if status == 'AUTH_ERROR':
            return {"status": 403, "message" : "auth error. Check token"}
            
        if status == 'SERVER_ERROR':
            return {"status": 500, "message" : "processing error on server"}
        
        if status in ['SUCCESS_WITH_WARNINGS','SUCCESS','VALID_XML_WITH_ERRORS_OR_WARNINGS']:
            return {"status": 200, "message" : "request processed: {}".format(status) }
            
        return {"status": 501, "message" : "unknown error ({})".format(status) }
                        
    def update_wigosid(self, wigos_ids: dict,  wigos_id: str = None) -> dict:
        """update wigos ids of station identified by _wigos_id, as per information in _wigos_ids_"""        
        return {"status": 200, "message" : "I did nothing"}
        
        
    def retrieve_wigosids(self, any_ids: list = []) -> dict:
        """retrieve information about current WIGOS IDs of stations passed as argument
        
        Parameters:
        any_ids (list): list of WIGOS Identifiers for which identifier information should be retrieved
        
        Returns:
        dict: Dict of dict containing primary and secondary WIGOS Identifiers. Key of the first dict is the any_id used in the request. The second level dict is encoded according to the JSON grammar specified for WIGOS IDs of a station.
        
        """
        
        wigos_ids = self.client.get_wigos_ids(any_ids)       
        
        result = {}
            
        for idx,station in enumerate(wigos_ids):
            
            search_wid = any_ids[idx] # the wigos ID that was searched
           
            if not station:
                result[search_wid] = None # no match found
            else:
                        
                primary = [ wid["wigosStationIdentifier"] for wid in station if wid["primary"] ][0]
                rest = [ wid["wigosStationIdentifier"] for wid in station if not wid["primary"] ]
                rest = rest + [None for i in range(max(0,3-len(rest)))] # make sure that the array has at least 3 entries
                
                result[search_wid] = { "primaryWigosID": primary , "wigosID2" : rest[0], "wigosID3" : rest[1] , "wigosID4" : rest[2] , "all" : [primary,] + [r for r in rest if r] } 
             
        return  result
        
        
    def retrieve_schedules(self, wigos_ids: list = [] , var_id: int = None ) -> list:
        """retrieve schedules of stations specified in the argument.
        
        
        Parameters:
        wigos_ids (list): list of WIGOS Identifiers for which schedules should be retrieved
        var_id (int): limit schedules to those related to variable. If nothing is supplied all schedules are returned
        
        Returns:
        list: List of dict containing individual schedules. Note that the result likely contains more schedules than number of stations passed as argument

        """
        
        schedules = {}
        
        for wid in wigos_ids:
            station=Station(self.client.load_station(wigos_id=wid,cache=True))
        
            schedules[wid] = station.schedules()
    
        ret = []
        
        for wigos_id,station in schedules.items():
            for var_id,observation in station.items():
                for deployment in observation["deployments"]:
                    for dg in deployment["datagenerations"]:
                        schedule = dg["schedule"]
                        
                        new_schedule = {"wigosID": wigos_id, "variable" : var_id, "deployment_id" : deployment["gid"] , "deployment_name" : "{from}-{to}".format(**deployment) ,
            "schedule_id" : dg["gid"], "schedule_name" : "{from}-{to}".format(**schedule), "schedule" : "{startMonth}-{endMonth}/{startWeekday}-{endWeekday}/{startHour}-{endHour}/{startMinute}-{endMinute}:{interval}".format(**schedule) , "international" : dg["schedule"]["international"], "near-real-time" : True, "date_from" :  schedule["from"] , "status" : "operational" }
                    
                        ret.append(new_schedule)
                    
    
        return ret
        return [ {"wigosID":"0-20000-2-123456", "variable" : 16 , 
            "deployment_id" : "id_47312301-88df-44e8-a05d-f7423f17ad95" , "deployment_name" : "some deployment" ,
            "schedule_id" : "id_37b9eb94-869c-4c4d-8fbd-d7e112fbb418", "schedule_name" : "some schedule", "schedule" : "Jan-Jun/Mon-Fri/14-18/11-23/00-59:3600" , "international" : True, "near-real-time" : True,
            "date_from" : "2020-12-01", "status" : "operational"
            },  ]
    